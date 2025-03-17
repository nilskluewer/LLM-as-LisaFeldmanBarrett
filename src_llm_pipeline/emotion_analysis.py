import json
from pathlib import Path
from typing import List
import time

import vertexai
from dotenv import load_dotenv
from langchain_core.utils.json_schema import dereference_refs
from langsmith import Client
from langsmith import RunTree
from langsmith.run_helpers import traceable
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    Content,
    GenerationConfig,
    GenerationResponse,
    SafetySetting,
)
from google.api_core.exceptions import ResourceExhausted
from icecream import ic


from .inputs.prompts.v17.data_models import (
    HolisticEmotionAnalysis,
    add_property_ordering_single_class,
    add_specific_property_ordering,
)

# from utils.langsmith_dataset import create_langsmith_dataset
from .utils.helper_functions import default_safety_settings
from .utils.langsmith_feedback import send_generation_response_feedback_to_trace
from .utils.output_parser import (
    parse_emotion_analysis,
    print_emotion_analysis,
    check_property_ordering,
)
from .utils.enums import MESSAGE_MAP
from .utils.eval_aspects import (
    aspect_evaluator,
    aspect_evaluator_all_aspects,
    Aspect,
    hallucination_confabulation_evaluator,
)

# Load environment variables
load_dotenv()
client = Client(api_url="https://eu.api.smith.langchain.com")

# --- load variables from config.json ---
with open("src_llm_pipeline/config.json", "r") as config_file:
    config = json.load(config_file)

model_name = config["model_name"]
prompts_version = config["prompt_version"]
debug_api_call = config["debug_api_call"]
debug_schema = config["debug_schema"]
llm_endpoint_location = config["llm_endpoint_location"]
check_for_hallucinations = config["check_for_hallucinations"]
dataset_tag = config["dataset_tag"]
temperature = config["temperature"]
top_p = config["top_p"]
eval_all_aspects = config["eval_all_aspects"]
validate_output_structure = config["validate_output_structure"]


# --- init vertexai ---
vertexai.init(project="rd-ri-genai-dev-2352", location=llm_endpoint_location)


# -- Helper functions --
def read_prompt(filename: str) -> str:
    """Load system prompt from file."""
    folder = Path(f"src_llm_pipeline/inputs/prompts/{prompts_version}")
    return (folder / filename).read_text()


def insert_context_sphere_into_prompt(
    context_file_name: Path, usere_task_prompt="user_task_prompt.md"
) -> str:
    context_sphere = context_file_name.read_text().strip()
    return usere_task_prompt.format(context_sphere=context_sphere)


@traceable(name="Simulate Conversation for Role Play Prompting", run_type="prompt")
def simulate_conversation_for_step_1(
    role_setting_prompt: str, role_feedback_prompt: str, user_task_prompt: str
) -> List[Content]:
    # Simulate the conversation flow with role play prompting
    # Consisting of a System prompt setting the scene, feedback prompt prefilling the models response
    # and the task prompt with the actual task.
    messages_google = [
        Content(role="user", parts=[Part.from_text(role_setting_prompt)]),
        Content(role="model", parts=[Part.from_text(role_feedback_prompt)]),
        Content(role="user", parts=[Part.from_text(user_task_prompt)]),
    ]
    """
    messages_langchain = [
        {"role": "user", "content": f"{role_setting_prompt}"},
        {"role": "model", "content": f"{role_feedback_prompt}"},
        {"role": "user", "content": f"{user_task_prompt}"},
    ]
    """
    return messages_google


@traceable(name="Simulate Conversation for Role Play Prompting", run_type="prompt")
def simulate_conversation_for_step_2(
    role_setting_prompt,
    role_feedback_prompt,
    role_task_prompt,
    step_1_response,
    step_2_task_prompt,
):
    # Chaning the role doent seem to alter the result
    messages_google = [
        (Content(role="user", parts=[Part.from_text(role_setting_prompt)])),
        (Content(role="model", parts=[Part.from_text(role_feedback_prompt)])),
        (Content(role="user", parts=[Part.from_text(role_task_prompt)])),
        (Content(role="model", parts=[Part.from_text(step_1_response)])),
        (Content(role="user", parts=[Part.from_text(step_2_task_prompt)])),
    ]
    """
    messages_langchain = [
        {"role": "user", "content": role_setting_prompt},
        {"role": "model", "content": role_feedback_prompt},
        {"role": "user", "content": role_task_prompt},
        {"role": "model", "content": step_2_task_prompt},
        {"role": "model", "content": step_2_task_prompt},
        {"role": "model", "content": step_2_task_prompt},
    ]
    """
    return messages_google


@traceable(name="Configuration for Controlled Generation", run_type="tool")
def create_generation_config(
    temperature, top_p, response_schema_model=None, response_mime_type=None
) -> GenerationConfig:
    # Configure generation parameters
    generation_config = GenerationConfig(
        response_mime_type=response_mime_type,  # "application/json",
        response_schema=response_schema_model,
        temperature=temperature,
        top_p=top_p,
        # seed=1,
        max_output_tokens=8000,
    )
    return generation_config


#@traceable(name="Configue LLM with Generation Config", run_type="tool")
def configure_llm(model_name, generation_config: GenerationConfig) -> GenerativeModel:
    return GenerativeModel(model_name=model_name, generation_config=generation_config)


@traceable(
    name="LLM Call",
    run_type="llm",
    tags=["api_call"],
    metadata={"ls_model_name": f"{model_name}"},
)
def call_api(
    messages: List[Content],
    configured_llm: GenerativeModel,
    safety_settings: list[SafetySetting],
    run_tree: RunTree,
) -> GenerationResponse:
    max_retries = 5
    initial_delay = 5  # initial delay in seconds for exponential backoff
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = configured_llm.generate_content(
                contents=messages, safety_settings=safety_settings, stream=False
            )
            #print(response)
            if debug_api_call:
                ic(response)

            messages.append(
                Content(role="model", parts=[Part.from_text(response.text)])
            )

            usage_metadata = response.usage_metadata
            result_dict = {
                "choices": messages,
                "usage_metadata": {
                    "input_tokens": usage_metadata.prompt_token_count,
                    "output_tokens": usage_metadata.candidates_token_count,
                    "total_tokens": usage_metadata.total_token_count,
                },
            }

            if debug_api_call:
                ic(result_dict)

            send_generation_response_feedback_to_trace(
                response=response, client=client, run_tree=run_tree
            )

            return result_dict

        except ResourceExhausted as e:
            print(
                f"Resource exhausted. Retry {retry_count + 1} in {initial_delay} seconds."
            )
            print("Error message: ", str(e))
            retry_count += 1
            time.sleep(initial_delay)
            initial_delay *= 2

        except Exception as e:
            # Handle any other exceptions that might occur
            print("An error occurred: ", str(e))
            return {"error": str(e)}

    print("Maximum retries reached. Please try again later.")
    return {"error": "Resource exhausted. Maximum retries reached."}


@traceable(name="Final Output Parser", run_type="parser")
def convert_to_dict(messages: List[Content]) -> dict:
    result_dict = {}

    for index, message in enumerate(messages):
        key = f"{message.role}-{MESSAGE_MAP.get(index)}"
        result_dict[key] = " ".join(part.text for part in message.parts)

    # result_dict["full_output_unstructured"] = str(messages)
    return result_dict


@traceable(name="Append LLM Response to Conversation", run_type="parser")
def append_response(message: List, message_to_append: Content) -> List[Content]:
    # message.append(message_to_append)
    return message


#@traceable(name="Parse LLM Output for Structure Validation", run_type="parser")
def parse_model_response_to_data_model_structure(input_text, target_schema) -> dict:
    data = parse_emotion_analysis(text=input_text, schema=target_schema)
    return data


@traceable(name="Validate Output Structure", run_type="parser")
def validate_response_property_order(
    parsed_data, schema_with_specific_ordering
) -> bool:
    if check_property_ordering(parsed_data, schema_with_specific_ordering):
        print("Output matches schema ordering exactly!")
        return True
    else:
        print("Warning: Output does not match schema ordering")
        return False


@traceable(name="Step 1: Context Sphere Analysis", run_type="chain")
def step_1_analyse_emotions_with_structureuser(
    messages: List[dict], temperature, top_p, run_tree: RunTree
):
    # Keep it in to validate if the Hallucination Eval works - input different users into the with and without context
    role_setting_prompt = read_prompt("LFB_role_setting_prompt.md")
    role_feedback_prompt = read_prompt("LFB_role_feedback_prompt.md")
    user_task_prompt = read_prompt("user_task_prompt.md")
    context_sphere = messages[1]["content"]

    user_task_prompt_with_context = user_task_prompt.format(
        context_sphere=context_sphere
    )
    role_play_prompt_google = simulate_conversation_for_step_1(
        role_setting_prompt, role_feedback_prompt, user_task_prompt_with_context
    )

    # Perform setup operations without repetition
    response_schema = dereference_refs(HolisticEmotionAnalysis.model_json_schema())
    response_schema.pop("$defs", None)
    response_schema_properties_ordered = add_specific_property_ordering(response_schema)

    if debug_schema:
        ic(response_schema_properties_ordered)

    llm_config = create_generation_config(
        response_schema_model=response_schema_properties_ordered,
        response_mime_type="application/json",
        temperature=temperature,
        top_p=top_p,
    )

    configured_llm = configure_llm(model_name=model_name, generation_config=llm_config)

    response = call_api(
        messages=role_play_prompt_google,
        configured_llm=configured_llm,
        safety_settings=default_safety_settings,
    )
    response_message = response["choices"][3].parts[0].text

    # Validate result
    if validate_output_structure:
        # Parse data to valide output structure
        parsed_data = parse_model_response_to_data_model_structure(
            input_text=response_message,
            target_schema=response_schema_properties_ordered,
        )
        validation_result = validate_response_property_order(
            parsed_data, response_schema_properties_ordered
        )

        # Feedback of validation result in Langsmith
        client.create_feedback(
            run_tree.id,
            key="llm_output_format_validation",
            value=validation_result,
            comment="1 = True: The model used the correct propertyOrder. False, the model did not!",
        )

    # Access the first candidate Content object in the response
    # message_history = append_response(
    #    role_play_conversation_langchain, response_message
    # )

    if debug_api_call:
        print_emotion_analysis(parsed_data, width=200)
    return response


@traceable(name="Step 2: Condense Emotional Analysis of User", run_type="chain")
def step_2_create_report_of_analysis(
    messages: List[dict], temperature, top_p, run_tree: RunTree
) -> List[dict]:
    """
    Created a Profile out of a given Analysis. Using messages to maintain readability in langsmith.
    Args:
        messages (List[dict]): _description_
        temperature (_type_): _description_
        top_p (_type_): _description_
        run_tree (RunTree): _description_

    Returns:
        List[dict]: _description_
    """
    summary_task_prompt = read_prompt("step_2_summary_prompt.md")

    llm_response_step_1 = messages["choices"][3].parts[0].text

    step_2_task_prompt = summary_task_prompt.format(analysis=llm_response_step_1)
    role_play_prompt_google = simulate_conversation_for_step_2(
        role_setting_prompt=messages["choices"][0].parts[0].text,
        role_feedback_prompt=messages["choices"][1].parts[0].text,
        role_task_prompt=messages["choices"][2].parts[0].text,
        step_1_response=llm_response_step_1,
        step_2_task_prompt=step_2_task_prompt,
    )

    # Configure the generation parameters
    llm_config = create_generation_config(temperature=temperature, top_p=top_p)

    # Configure the LLM with the generation config
    configured_llm = configure_llm(model_name=model_name, generation_config=llm_config)
    response = call_api(
        messages=role_play_prompt_google,
        configured_llm=configured_llm,
        safety_settings=default_safety_settings,
    )

    return response


def request_emotion_analysis_with_user_id(context_sphere, user_id: int) -> dict:
    """
    Helper function to wrap main call with user_id + traceable
    """

    @traceable(
        run_type="chain",
        name="Context Aware Emotion Analysis",
        tags=[
            f"{model_name}",
            f"User_ID: {user_id}",
            f"{dataset_tag}",
            f"{prompts_version}",
        ],
        # Optional Metadata for Langsmith
        # metadata={
        #    "check_hallucinations": check_for_hallucinations,
        #    "eval_all_aspects": eval_all_aspects,
        # },
    )
    def request_emotion_analysis(messages: List[dict], run_tree: RunTree):
        """
        Call the Google Gemini API with basic configuration.
        """

        message_history_step1 = step_1_analyse_emotions_with_structureuser(
            messages, temperature, top_p
        )
        step_1_analysis = message_history_step1["choices"][3].parts[0].text

        message_history_step1

        if debug_api_call:
            ic(step_1_analysis)

        question = str(
            [
                {
                    "role": "user",
                    "text": message_history_step1["choices"][0].parts[0].text,
                },
                {
                    "role": "user",
                    "text": message_history_step1["choices"][1].parts[0].text,
                },
                {
                    "role": "user",
                    "text": message_history_step1["choices"][2].parts[0].text,
                },
            ]
        )

        answer = str(message_history_step1["choices"][3].parts[0].text)

        if check_for_hallucinations:
            confabulation_threshold = config["confabulation_threshold"]
            avg_rating_step1 = hallucination_confabulation_evaluator(
                question=question,
                answer=answer,
                use_flash = True,
                use_haiku = False,
                use_sonnet = False,
                use_4o = False,
                step_of_process="step_1",
                run_tree_parent_id=run_tree.id,
            )
            if avg_rating_step1 < confabulation_threshold:
                print(
                    f"No hallucination detected. Continue processing. Avg. Rating: {avg_rating_step1}"
                )

                message_history_step2 = step_2_create_report_of_analysis(
                    messages=message_history_step1, temperature=temperature, top_p=top_p
                )
                
                question = str(
                    [
                        {
                            "role": "user",
                            "text": message_history_step2["choices"][0].parts[0].text,
                        },
                        {
                            "role": "model",
                            "text": message_history_step2["choices"][1].parts[0].text,
                        },
                        {
                            "role": "user",
                            "text": message_history_step2["choices"][2].parts[0].text,
                        },
                        {
                            "role": "model",
                            "text": message_history_step2["choices"][3].parts[0].text,
                        },
                        {
                            "role": "user",
                            "text": message_history_step2["choices"][4].parts[0].text,
                        },
                    ]
                )

                answer = str(message_history_step2["choices"][5].parts[0].text)

                # dict_list = convert_to_dict(message_history)
                avg_rating_step2 = hallucination_confabulation_evaluator(
                    question=question,
                    answer=answer,
                    use_flash = True,
                    use_haiku = False,
                    use_sonnet = False,
                    use_4o = False,
                    step_of_process="step_2",
                    run_tree_parent_id=run_tree.id,
                    
                    
                )

                if avg_rating_step2 < confabulation_threshold:
                    print(
                        f"No hallucination detected. Continue processing. Avg. Rating: {avg_rating_step2}"
                    )

                else:
                    raise Exception(
                        f"Confabulation detected at Step 2. Avg. Rating {avg_rating_step2}. \n --- \n No further processing."
                    )

            else:
                raise Exception(
                    f"Confabulation detected at Step 1. Avg. Rating {avg_rating_step1}. \n --- \n No further processing."
                )
        if eval_all_aspects:
            aspect_evaluator(
                message_history_step2["choices"][3].parts[0].text, 
                message_history_step2["choices"][5].parts[0].text,
                aspect=Aspect.COMPREHENSIVENESS,
                llm_model_name="gpt-4o-mini",
                run_tree_parent_id=run_tree.id,
                langsmith_extra={"tags": [f"{Aspect.COMPREHENSIVENESS}"]},
            )
            aspect_evaluator(
                message_history_step2["choices"][3].parts[0].text,
                message_history_step2["choices"][5].parts[0].text,
                aspect=Aspect.CONSISTENCY,
                llm_model_name="gpt-4o-mini",
                run_tree_parent_id=run_tree.id,
                langsmith_extra={"tags": [f"{Aspect.CONSISTENCY}"]},
            )
            aspect_evaluator(
                message_history_step2["choices"][3].parts[0].text,
                message_history_step2["choices"][5].parts[0].text,
                aspect=Aspect.HELPFULNESS,
                llm_model_name="gpt-4o-mini",
                run_tree_parent_id=run_tree.id,
                langsmith_extra={"tags": [f"{Aspect.HELPFULNESS}"]},
            )
            aspect_evaluator(
                message_history_step2["choices"][3].parts[0].text,
                message_history_step2["choices"][5].parts[0].text,
                aspect=Aspect.RELEVANCE,
                llm_model_name="gpt-4o-mini",
                run_tree_parent_id=run_tree.id,
                langsmith_extra={"tags": [f"{Aspect.RELEVANCE}"]},
            )
        

        return message_history_step1, message_history_step2

    message_history_step1, message_history_step2 = request_emotion_analysis(
        messages=[
            {"role": "user", "content": f"Subject of Analysis is: {user_id}"},
            {"role": "user", "content": f"{context_sphere}"},
        ]
    )
    return message_history_step1, message_history_step2
