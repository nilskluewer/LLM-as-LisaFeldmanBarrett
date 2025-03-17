from enum import Enum
#https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-filters#unsafe_responses

FINISH_REASON_MAP = {
    0: "FINISH_REASON_UNSPECIFIED",
    1: "STOP",
    2: "MAX_TOKENS",
    3: "SAFETY",
    4: "RECITATION",
    5: "OTHER",
    6: "BLOCKLIST",
    7: "PROHIBITED_CONTENT",
    8: "SPII",
    9: "MALFORMED_FUNCTION_CALL",
}


#https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-filters#configurable-filters
CATEGORY_MAP = {
    0: "HARM_UNSPECIFIED",
    1: "HARM_HATE_SPEECH",
    2: "HARM_DANGEROUS_CONTENT",
    3: "HARM_HARASSMENT",
    4: "HARM_SEXUALLY_EXPLICIT",
    # Add other categories as necessary
}

PROBABILITY_MAP = {
    0: "PROBABILITY_UNSPECIFIED",
    1: "VERY_UNLIKELY",
    2: "UNLIKELY",
    3: "NEGLIGIBLE",
    4: "LIKELY",
    5: "VERY_LIKELY",
    # Add other probability levels if there are any
}

SEVERITY_MAP = {
    0: "SEVERITY_UNSPECIFIED",
    1: "HARM_SEVERITY_NEGLIGIBLE",
    2: "HARM_SEVERITY_MINOR",
    3: "HARM_SEVERITY_SERIOUS",
    4: "HARM_SEVERITY_EXTREME",
    # Add other severity levels if there are any
}

MESSAGE_MAP = {
    0: "Role-Setting-Prompt",
    1: "Role-Feedback-Prompt",
    2: "Classification_Prompt",
    3: "Step 1: Classification",
    4: "Summarization_Prompt",
    5: "Step 2: Summarization",
    6: "Feedback_Prompt",
    7: "Step 3: Revised Summarization"
}

class Aspect(Enum):
    COHERENCE = (
        "Coherence",
        "Incoherence",
        "the logical flow and clarity within the passage. Consider whether the passage maintains a logical sequence, clear connections between ideas, and an overall sense of understanding."
    )
    RELEVANCE = (
        "Relevance",
        "Irrelevance",
        "how well the summarized emotion classification relates to the original in-depth classification. Does the summary accurately reflect the key emotional categories and their relationships identified in the classification?"
    )
    CONSISTENCY = (
        "Consistency",
        "Inconsistency",
        "whether the emotional categories and their assigned probabilities in the summary are consistent with the findings of the original in-depth classification. Are there any contradictions or inconsistencies between the two?"
    )
    HELPFULNESS = (
        "Helpfulness",
        "Unhelpfulness",
        "how useful the summarized emotion classification is for understanding the overall emotional tone of the text. Does it provide a clear and concise representation of the key emotions and their intensities?"
    )
    COMPREHENSIVENESS = (
        "Comprehensiveness",
        "Incompleteness",
        "whether the summary captures all the significant emotional categories and nuances identified in the original in-depth classification. Are there any important emotions or details missing from the summary?"
    )
    
    # Potentially add more aspects like:
    #  -  Bias (Fairness/Neutrality of the emotion classification)
    #  -  Confidence (Certainty expressed by the LLM in its classification)
    #  -  Specificity/Granularity (Level of detail in the emotion classification)