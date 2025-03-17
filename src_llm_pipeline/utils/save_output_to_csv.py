from utils.data_models import HolisticEmotionAnalysis
import csv
from pathlib import Path

def clean_text(text: str) -> str:
    """Clean text by removing line breaks and escaping semicolons"""
    if text is None:
        return ""
    return str(text).replace('\n', ' ').replace('\r', ' ').replace(';', ',').strip()

def main(
    emotion_analysis_input: str,
    emotion_analysis: HolisticEmotionAnalysis, 
    model_temperature: float, 
    top_p: float,
    batch_id: str, 
    user_id: str, 
    run_id: str,
    timestamp: str, 
    model_name: str,
    prompt_template_version: str
) -> str:
    
    # Create Analysis_Output directory if it doesn't exist
    output_dir = Path("./outputs/csv_batch_results")
    output_dir.mkdir(exist_ok=True)
    
    # Create filename with batch_id
    filename = output_dir / f"emotion_analysis_batch_{batch_id}.csv"
    
    file_exists = filename.exists()

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='"')

        if not file_exists:
            header = [
                "Timestamp", 
                "Run ID", 
                "User ID", 
                "Batch ID", 
                "Model Name", 
                "Prompt Template Version",
                # Model Parameters
                "Model Temperature",
                "Top P",
                # Core Affect Analysis
                "Core Affect Thought Process",
                "Valence",
                "Arousal",
                "Core Affect Rationale",
                # Cognitive Appraisal
                "Cognitive Appraisal Thought Process",
                "Cognitive Analysis",
                "Cognitive Rationale",
                # Cultural and Social Context
                "Cultural Context Thought Process",
                "Cultural Discussion",
                "Cultural Rationale",
                # Emotion Construction
                "Emotion Construction Analysis",
                "Emotion Construction Rationale",
                # Emotional Dynamics
                "Emotional Dynamics Analysis",
                "Emotional Dynamics Rationale",
                # Holistic Profile
                "Holistic Description",
                "Nuanced Classification",
                "Holistic Rationale"
            ]
            writer.writerow(header)

        row = [
            clean_text(timestamp),
            clean_text(run_id),
            clean_text(user_id),
            clean_text(batch_id),
            clean_text(model_name),
            clean_text(prompt_template_version),
            # Model Parameters
            model_temperature,
            top_p,
            # Core Affect Analysis
            clean_text(emotion_analysis.core_affect_analysis.thought_process),
            clean_text(emotion_analysis.core_affect_analysis.valence),
            clean_text(emotion_analysis.core_affect_analysis.arousal),
            clean_text(emotion_analysis.core_affect_analysis.rationale),
            # Cognitive Appraisal
            clean_text(emotion_analysis.cognitive_appraisal_and_conceptualization.thought_process),
            clean_text(emotion_analysis.cognitive_appraisal_and_conceptualization.analysis),
            clean_text(emotion_analysis.cognitive_appraisal_and_conceptualization.rationale),
            # Cultural and Social Context
            clean_text(emotion_analysis.cultural_and_social_context.thought_process),
            clean_text(emotion_analysis.cultural_and_social_context.discussion),
            clean_text(emotion_analysis.cultural_and_social_context.rationale),
            # Emotion Construction
            clean_text(emotion_analysis.emotion_construction_analysis.analysis),
            clean_text(emotion_analysis.emotion_construction_analysis.rationale),
            # Emotional Dynamics
            clean_text(emotion_analysis.emotional_dynamics_and_changes.analysis),
            clean_text(emotion_analysis.emotional_dynamics_and_changes.rationale),
            # Holistic Profile
            clean_text(emotion_analysis.holistic_emotional_profile.description),
            clean_text(emotion_analysis.holistic_emotional_profile.nuanced_classification),
            clean_text(emotion_analysis.holistic_emotional_profile.rationale)
        ]
        writer.writerow(row)

    return str(filename)