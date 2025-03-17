from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.utils.json_schema import dereference_refs
from langsmith import traceable


# The following classes are used to define the data model for the output of the emotion analysis pipeline.
# CoreAffectAnalysis captures fluctuations in basic emotional states—valence and arousal—providing a foundational understanding of the user's affective experiences.
class CoreAffectAnalysis(BaseModel):
    """
    Do not be lazy while working on your tasks!
    """
    thought_process: str = Field(
        ...,
        description=(
            "Provide a detailed step-by-step thought process of how you intend to analyze the core affect, *including specific quotes and examples from the user's comments to illustrate your points*, considering both valence (pleasantness) and arousal (activation), and noting any emotional dynamics or changes over time. Reference specific expressions, language, and contextual factors. **Consider how insights from other disciplines like sociology or neuroscience might inform your analysis.**"  
        )
    )
    valence: str = Field(
        ...,
        description=(
            "Classify the valence of the user's emotional state, noting any fluctuations. *Cite specific comments or phrases that indicate the valence.*"
        )
    )
    arousal: str = Field(
        ...,
        description=(
            "Classify the arousal level of the user's emotional state, indicating activation or energy levels, and any changes over time. *Cite specific comments or phrases that indicate the arousal level.*" 
        )
    )
    patterns_observed: str = Field(
        ...,
        description="Document any recurring patterns in the user's core affect across comments, linking them to specific instances."
    )
    anomalous_observations: str = Field(
        ...,
        description="Highlight any comments where the user's core affect deviates from expected patterns based on the context."
    )
    rationale: str = Field(
        ...,
        description=(
            "**Include a clear short rationale explaining how you arrived at your conclusions, *supported by specific examples from the text and your research.* Consider how **external contextual factors** like news events or broader societal trends might contribute to the observed emotional state.**"
        )
    )

# CognitiveAppraisalAndConceptualization examines how the user's interpretations and knowledge shape emotions, reflecting Barrett's concept of constructed emotional experiences.
class CognitiveAppraisalAndConceptualization(BaseModel):
    """
    Do not be lazy while working on your tasks!
    """
    thought_process: str = Field(
        ...,
        description=(
            "Provide a detailed step-by-step thought process of how you intend to analyze the user's cognitive appraisals and conceptualizations. Refer to specific interpretations, judgments, language use, and conceptual knowledge. *Include specific comments and phrases from the user to illustrate these points.* **Consider how insights from other disciplines like psychology or cognitive science might *describe* the observed cognitive appraisals and conceptualizations.**"  
        )
    )
    analysis: str = Field(
        ...,
        description=(
            "Analyze how the user's interpretations and conceptual knowledge contribute to the construction of their emotions. *Support your analysis by illustrating how these cognitive processes shape the user's emotional experiences, citing specific examples from the user's comments.*"
        )
    )
    patterns_observed: str = Field(
        ...,
        description="Document any recurring patterns in the user's cognitive appraisals and conceptualizations across comments, linking them to specific instances."
    )
    anomalous_observations: str = Field(
        ...,
        description="Highlight any comments where the user's cognitive appraisals or conceptualizations deviate from expected patterns based on the context."
    )
    rationale: str = Field(
        ...,
        description=(
            "**Include a clear short rationale explaining how you arrived at your conclusions, *supported by specific examples from the text and your research.* **Consider how external contextual factors like cultural norms or social trends might *relate to* the observed cognitive processes.**"
        )
    )

# CulturalAndSocialContext considers societal and cultural influences on emotions, highlighting the context-dependent nature of emotional experiences.
class CulturalAndSocialContext(BaseModel):
    """
    Do not be lazy while working on your tasks!
    """
    thought_process: str = Field(
        ...,
        description=(
            "Provide a detailed step-by-step thought process of how you want to discuss the situational, cultural, and social contextual factors influencing the user's emotions, including past experiences and expectations. *Reference specific comments that indicate cultural or social influences.* **Consider how insights from other disciplines like sociology or anthropology might *describe* the observed cultural and social influences.**"
        )
    )
    analysis: str = Field(
        ...,
        description=(
            "Analyze how cultural norms, societal values, social interactions, and predictions based on past experiences could influence the user's emotional experiences. *Support your analysis by explaining the impact of these factors on the user's emotions, with supporting observations and specific examples from the user's comments.*"
        )
    )
    patterns_observed: str = Field(
        ...,
        description="Document any recurring patterns in the cultural and social factors influencing the user's emotions across comments, linking them to specific instances."
    )
    anomalous_observations: str = Field(
        ...,
        description="Highlight any comments where the cultural and social factors influencing the user's emotions deviate from expected patterns based on the context."
    )
    rationale: str = Field(
        ...,
        description=(
            "**Include a clear short rationale explaining how you arrived at your conclusions, *supported by specific examples from the text and your research.* **Consider how external contextual factors like political events or historical context might *relate to* the observed cultural and social influences.**"
        )
    )

# EmotionConstructionAnalysis synthesizes how affect, cognition, and context interact to construct emotions, embodying a holistic view of emotional dynamics.
class EmotionConstructionAnalysis(BaseModel):
    """
    Do not be lazy while working on your tasks!
    """
    thought_process: str = Field(
        ...,
        description=(
            "Provide a detailed step-by-step thought process on how you want to analyze the user's emotion construction process through the interplay of emotional core affect, cognitive appraisals, conceptualization, and contextual factors. *Integrate the insights you gained during the generation of the previous analysis parts, referencing specific examples from the user's comments.* **Consider how insights from other disciplines like neuroscience or psychology might *describe* the observed emotion construction process.**"
        )
    )
    analysis: str = Field(
        ...,
        description=(
            "Provide your analysis planned in the thought_process on how the user's emotions are constructed through the interplay of core affect, cognitive appraisals, conceptualization, and contextual factors. *Integrate the insights you gained during the generation of the previous analysis parts, and support your points with specific examples from the user's comments.*"  # Added instruction to integrate insights and support analysis with specific examples.
        )
    )
    patterns_observed: str = Field(
        ...,
        description="Document any recurring patterns in the user's emotion construction process across comments, linking them to specific instances."
    )
    anomalous_observations: str = Field(
        ...,
        description="Highlight any comments where the user's emotion construction process deviates from expected patterns based on the context."
    )
    rationale: str = Field(
        ...,
        description=(
            "**Include a clear short rationale explaining how you arrived at your conclusions, *supported by specific examples from the text and your research.* **Consider how external contextual factors like individual experiences or social media trends might *relate to* the observed emotion construction process.**"
        )
    )

# EmotionalDynamicsAndChanges tracks emotional shifts over time, illustrating the fluid and process-oriented nature of emotions in response to user interactions.
class EmotionalDynamicsAndChanges(BaseModel):
    """
    Do not be lazy while working on your tasks!
    """
    thought_process: str = Field(
        ...,
        description=(
            "Provide a step-by-step thought process on how you want to identify these shifts/dynamic changes in the user's emotionality. Are these shifts already visible through the already generated analysis of core affect, cognitive appraisals, conceptualization, and contextual factors? *Explain how these emotional dynamics reflect the user's emotional processing and construction over time, citing specific examples from the user's comments.* **Consider how insights from other disciplines like developmental psychology or social psychology might *describe* the observed emotional dynamics.**"
        )
    )
    analysis: str = Field(
        ...,
        description=(
            "Analyze if there are any changes or fluctuations in the user's emotions throughout their interactions. Shifts such as in valence and arousal or in behavior towards other users. *Use examples to display these shifts, citing specific comments that illustrate changes over time.*"
        )
    )
    patterns_observed: str = Field(
        ...,
        description="Document any recurring patterns in the user's emotional dynamics across comments, linking them to specific instances."
    )
    anomalous_observations: str = Field(
        ...,
        description="Highlight any comments where the user's emotional dynamics deviate from expected patterns based on the context."
    )
    rationale: str = Field(
        ...,
        description=(
            "**Include a clear short rationale explaining how you arrived at your conclusions, *supported by specific examples from the text and your research.* **Consider how external contextual factors like the topic of discussion or the online community's culture might *relate to* the observed emotional dynamics.**"
        )
    )

class HolisticEmotionAnalysis(BaseModel):
    core_affect_analysis: CoreAffectAnalysis
    cognitive_appraisal_and_conceptualization: CognitiveAppraisalAndConceptualization
    cultural_and_social_context: CulturalAndSocialContext
    emotion_construction_analysis: EmotionConstructionAnalysis
    emotional_dynamics_and_changes: EmotionalDynamicsAndChanges

def add_specific_property_ordering(schema: Dict[str, Any]) -> Dict[str, Any]:
    # Root level ordering
    schema["propertyOrdering"] = [
        "core_affect_analysis",
        "cognitive_appraisal_and_conceptualization",
        "cultural_and_social_context",
        "emotion_construction_analysis",
        "emotional_dynamics_and_changes",
 #       "holistic_emotional_profile"
    ]

    # Core affect analysis ordering
    schema["properties"]["core_affect_analysis"]["propertyOrdering"] = [
        "thought_process",
        "valence",
        "arousal",
        "patterns_observed",
        "anomalous_observations",
        "rationale"
    ]

    # Cognitive appraisal ordering
    schema["properties"]["cognitive_appraisal_and_conceptualization"]["propertyOrdering"] = [
        "thought_process",
        "analysis",
        "patterns_observed",
        "anomalous_observations",
        "rationale"
    ]

    # Cultural and social context ordering
    schema["properties"]["cultural_and_social_context"]["propertyOrdering"] = [
        "thought_process",
        "analysis",
        "patterns_observed",
        "anomalous_observations",
        "rationale"
    ]

    # Emotion construction analysis ordering
    schema["properties"]["emotion_construction_analysis"]["propertyOrdering"] = [
        "thought_process",
        "analysis",
        "patterns_observed",
        "anomalous_observations",
        "rationale"
    ]

    # Emotional dynamics and changes ordering
    schema["properties"]["emotional_dynamics_and_changes"]["propertyOrdering"] = [
        "thought_process",
        "analysis",
        "patterns_observed",
        "anomalous_observations",
        "rationale"
    ]
    return schema

def add_property_ordering_single_class(schema: Dict[str, Any]) -> Dict[str, Any]:
    # Ordering for HolisticEmotionalProfile fields
    schema["propertyOrdering"] = [
        "thought_process",
        "nuanced_analysis",
        "patterns_observed",
        "anomalous_observations",
        "discussion_behaviour"
    ]
    return schema