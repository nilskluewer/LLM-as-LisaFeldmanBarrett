from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI
import json
from icecream import ic

from langsmith.run_helpers import traceable
from src_llm_pipeline.utils.enums import Aspect

# TODO ander aspect typen adden
# TODO maybe critique einfügen das man auch weiß was laut model hätte besser sein können

class EvaluationResult(BaseModel):
    aspect: str
    score: bool = Field()
    reasoning: str = Field(description="The reasoning for the score. Max three sentences!")
    critique: str = Field(description="Suggested improvements to the summary. Short precise key points! Max. 3 points.")

class CoherenceEvaluation(EvaluationResult):
    aspect: str = "coherence" # fixed value

class RelevanceEvaluation(EvaluationResult):
    aspect: str = "relevance" # fixed value

class ConsistencyEvaluation(EvaluationResult):
    aspect: str = "consistency" # fixed value

class HelpfulnessEvaluation(EvaluationResult):
    aspect: str = "helpfulness" # fixed value

class ComprehensivenessEvaluation(EvaluationResult):
    aspect: str = "comprehensiveness" # fixed value

def load_config():
    config_path = Path('src_llm_pipeline/config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config

load_dotenv()

client = Client()

config = load_config()

prompts_version = config["prompt_version"]





def read_prompts(filename: str) -> str:
    """Load system prompt from file."""
    folder = Path(f"src_llm_pipeline/inputs/prompts/{prompts_version}")
    return (folder / filename).read_text()

llm_evaluator_prompt_text = read_prompts("prompt_eval_aspects.md")
instructions_report = read_prompts("step_2_summary_prompt.md")


@traceable(name="LLM as a Judge: Aspects Eval", run_type="chain")
def aspect_evaluator(step_1_classification, step_2_classification_summary, aspect: Aspect,llm_model_name : str, run_tree_parent_id):    
    aspect, ant_aspect, aspect_inst = aspect.value
    task_ins = "report of an in-depth analysis"
    
    # Select the appropriate Pydantic model based on the aspect
    print("ASPECT:", aspect)
    if aspect == "Coherence":
        pydantic_model = CoherenceEvaluation
    elif aspect == "Relevance":
        pydantic_model = RelevanceEvaluation
    elif aspect == "Consistency":
        pydantic_model = ConsistencyEvaluation
    elif aspect == "Helpfulness":
        pydantic_model = HelpfulnessEvaluation
    elif aspect == "Comprehensiveness":
        pydantic_model = ComprehensivenessEvaluation
    else:
        raise ValueError(f"Aspect {aspect} not supported")
    
    # TODO: if model string start with gpt string then use the model name and use ChatOpenAi
    
    if llm_model_name.startswith("gpt"):
        llm = ChatOpenAI(
                model_name=llm_model_name,
                max_tokens=2000,
                temperature=0.0,
                
            )
    elif llm_model_name.startswith("claude"):
        llm = ChatAnthropic(
                model_name=llm_model_name,
                max_tokens=1000,
                temperature=0.0,
            )

    llm = llm.with_structured_output(pydantic_model)
    prompt = PromptTemplate.from_template(llm_evaluator_prompt_text)
    chain = (prompt | llm).with_config({"tags": [f"{aspect}"]})
    
    response = chain.invoke({"task-ins": task_ins,
                             "aspect" : aspect,
                             "ant-aspect" : ant_aspect,
                             "aspect-inst": aspect_inst,
                             "step_1_classification": step_1_classification,
                             "step_2_classification_summary": step_2_classification_summary,
                            "instructions_report": instructions_report})
    #print(response)
    ic("The Score from OpenAi is:", response.score)
    ic("The Reasoning from OpenAi is:", response.reasoning)
    ic("The Critique from OpenAi is:", response.critique)
    
    client.create_feedback(
        run_id=run_tree_parent_id,
        key=aspect,
        value=response.critique,
        score=response.score,
        comment=response.reasoning,
        feedback_source_type="api",
        source_info={"model": llm_model_name}
    )
    return response



@traceable(name="LLM-as-a-Judge: Confabulation Check", run_type="chain")
def hallucination_confabulation_evaluator(question, answer, step_of_process, run_tree_parent_id,
                                            use_4o: bool = True,
                                            use_haiku: bool = True,
                                            use_sonnet: bool = True,
                                            use_flash: bool = True):
    """
    Evaluate the potential confabulation of an answer using one or more language models.
    
    This function accepts a question and its answer, and then uses up to four different LLM evaluators
    to assess whether the answer contains confabulated content. The evaluation is based on a prompt template 
    read from "prompt_eval_confabulation.md". For each LLM corresponding to llm_A, llm_B, llm_C, and llm_D,
    the Boolean parameters (use_llm_a, use_llm_b, use_llm_c, use_llm_d) determine if that LLM is used.

    The function then collects responses from the selected evaluators, submits the feedback via a client,
    and computes the average confabulation rating across only the invoked evaluators.

    Parameters:
        question (str): The initial question to be evaluated for confabulation.
        answer (str): The answer associated with the question.
        step_of_process (str): A string to tag the evaluation step.
        run_tree_parent_id (str): An identifier for logging/associating the evaluation in the run tree.
        use_llm_a (bool, optional): If True, use LLM_A (GPT-4o) for evaluation. Defaults to True.
        use_llm_b (bool, optional): If True, use LLM_B (Claude-3-5-haiku) for evaluation. Defaults to True.
        use_llm_c (bool, optional): If True, use LLM_C (Claude-3-5-sonnet) for evaluation. Defaults to True.
        use_llm_d (bool, optional): If True, use LLM_D (Gemini-1.5-flash) for evaluation. Defaults to True.
    
    Returns:
        float: The average confabulation rating computed from the selected evaluators.
    """
    eval_prompt = read_prompts("prompt_eval_confabulation.md")
    eval_prompt = PromptTemplate.from_template(eval_prompt)
    
    # Define the structured output model for evaluation results.
    class ConfabulationEvaluation(BaseModel):
        explanation: str = Field(
            description="Short explanation if there is confabulation. Based on the given question and corresponding answer. "
                        "Provide a 1:1 text example if confabulation is present. Keep the initial question in mind."
        )
        scale_rating: int = Field(
            description="The rating of the confabulation on a scale from 1 to 10. 1 means no confabulation, 10 means high confabulation. "
                        "The score reflects only the aspect of confabulation."
        )
    
    # Initialize the LLMs.
    llm_A = ChatOpenAI(
        model_name="gpt-4o",
        max_tokens=2000,
        temperature=0.0,       
    )
    llm_B = ChatAnthropic(
        model_name="claude-3-5-haiku-20241022",
        max_tokens=1000,
        temperature=0.0,
    )
    llm_C = ChatAnthropic(
        model_name="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0.0,
    )
    llm_D = ChatVertexAI(
        model_name="gemini-1.5-flash-002",
        max_tokens=1000,
        temperature=0.0,
    )
    
    # Wrap each LLM with structured output using the evaluation model.
    llm_A_structured = llm_A.with_structured_output(ConfabulationEvaluation)
    llm_B_structured = llm_B.with_structured_output(ConfabulationEvaluation)
    llm_C_structured = llm_C.with_structured_output(ConfabulationEvaluation)
    llm_D_structured = llm_D.with_structured_output(ConfabulationEvaluation)
    
    # Create evaluation chains.
    chain_A = (eval_prompt | llm_A_structured).with_config({"tags": ["confabulation"]})
    chain_B = (eval_prompt | llm_B_structured).with_config({"tags": ["confabulation"]})
    chain_C = (eval_prompt | llm_C_structured).with_config({"tags": ["confabulation"]})
    chain_D = (eval_prompt | llm_D_structured).with_config({"tags": ["confabulation"]})
    
    responses = []
    
    # Invoke each chain only if its flag is True and record the response.
    if use_4o:
        response_A = chain_A.invoke({"question": question, "answer": answer})
        ic("Response from LLM_A (gpt-4o):", response_A)
        client.create_feedback(
            run_id=run_tree_parent_id,
            key=("confabulation_4o_" + step_of_process),
            comment=response_A.explanation,
            score=response_A.scale_rating,
            feedback_source_type="api",
            source_info={"model": "gpt-4o-mini"}
        )
        responses.append(response_A.scale_rating)
    
    if use_haiku:
        response_B = chain_B.invoke({"question": question, "answer": answer})
        ic("Response from LLM_B (claude-3-5-haiku):", response_B)
        client.create_feedback(
            run_id=run_tree_parent_id,
            key=("confabulation_haiku_" + step_of_process),
            comment=response_B.explanation,
            score=response_B.scale_rating,
            feedback_source_type="api",
            source_info={"model": "claude-3-5-haiku-20241022"}
        )
        responses.append(response_B.scale_rating)
    
    if use_sonnet:
        response_C = chain_C.invoke({"question": question, "answer": answer})
        ic("Response from LLM_C (claude-3-5-sonnet):", response_C)
        client.create_feedback(
            run_id=run_tree_parent_id,
            key=("confabulation_sonnet_" + step_of_process),
            comment=response_C.explanation,
            score=response_C.scale_rating,
            feedback_source_type="api",
            source_info={"model": "claude-3-5-sonnet-20241022"}
        )
        responses.append(response_C.scale_rating)
    
    if use_flash:
        response_D = chain_D.invoke({"question": question, "answer": answer})
        ic("Response from LLM_D (gemini-1.5-flash):", response_D)
        client.create_feedback(
            run_id=run_tree_parent_id,
            key=("confabulation_gemini_" + step_of_process),
            comment=response_D.explanation,
            score=response_D.scale_rating,
            feedback_source_type="api",
            source_info={"model": "gemini-1.5-flash-002"}
        )
        responses.append(response_D.scale_rating)
    
    # Compute the average rating from only the invoked responses.
    if responses:
        avg_confabulation_rating = sum(responses) / len(responses)
    else:
        avg_confabulation_rating = 0  # Alternatively, raise an exception if no LLM was selected.
    
    print("Average Confabulation Rating equals:", avg_confabulation_rating)
    return avg_confabulation_rating



def aspect_evaluator_all_aspects(step_1_classification, step_2_classification_summary,llm_model_name : str, run_tree_parent_id):    
    for aspect in Aspect:
        aspect_evaluator(step_1_classification, step_2_classification_summary, aspect, llm_model_name, run_tree_parent_id, langsmith_extra={"tags": [f"{aspect}"]})
        
        

if __name__ == "__main__":
    print()
    #aspect_evaluator_all_aspects()
    #hallucination_confabulation_evaluator("What is the capital of France?", "The capital of France is Paris.")