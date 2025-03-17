from vertexai.generative_models import GenerationResponse
from .enums import FINISH_REASON_MAP, CATEGORY_MAP


def send_generation_response_feedback_to_trace(
    response: GenerationResponse, client, run_tree
):
    candidate = response.candidates[0]
    finish_reason_str = FINISH_REASON_MAP.get(candidate.finish_reason, "NOT DEFINED")
    client.create_feedback(
        run_tree.id,
        key="finishReason",
        value=finish_reason_str,
        feedback_source_type="model",
    )

    # Iterate over the safty_ratings
    for idx, safety_rating in enumerate(candidate.safety_ratings):
        category_str = CATEGORY_MAP.get(safety_rating.category, "UNKNOWN_CATEGORY")

        # Create feedback
        # Additionally, send feedback for scores
        client.create_feedback(
            run_tree.id,
            key="prob_" + category_str,
            score=round(safety_rating.probability_score, 4),
            comment="Score for how probable the Harm is.  0 to 1. Low to High",
            feedback_source_type="model",
        )
        client.create_feedback(
            run_tree.id,
            key="severity_" + category_str,
            score=round(safety_rating.severity_score, 4),
            comment="Score for how severe the Harm is. 0 to 1. Low to High",
            feedback_source_type="model",
        )

    client.create_feedback(run_tree.id, key="avgLogprobs", score=round(candidate.avg_logprobs, 4))

    # Feedback for Usage Metadata
    usage_metadata = response.usage_metadata
    client.create_feedback(
        run_tree.id,
        key="promptTokenCount",
        score=usage_metadata.prompt_token_count,
        feedback_source_type="model",
    )
    client.create_feedback(
        run_tree.id,
        key="responseTokenCount",
        score=usage_metadata.candidates_token_count,
        feedback_source_type="model",
    )
    client.create_feedback(
        run_tree.id,
        key="totalTokenCount",
        score=usage_metadata.total_token_count,
        feedback_source_type="model",
    )

    if finish_reason_str != "STOP":
        raise ValueError(
            "Model could not finish successfully due to reason: ", finish_reason_str
        )
