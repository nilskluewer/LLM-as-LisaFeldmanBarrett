Score the following '{task-ins}' with respect to '{aspect}' on a continuous scale from 0 to 100,
where a score of zero means '{ant-aspect}' and score of one hundred means '{aspect}'.
Note that '{aspect}' measures '{aspect-inst}'.

<in_depth_classification>
{step_1_classification}
</in_depth_classification>

<summary>
{step_2_classification_summary}
</summary>


Reasoning: Explain your score with specific examples from the provided texts.  Clearly state which parts of the <summary> support your evaluation, and if applicable, mention any inconsistencies or shortcomings.

Critique: Suggest *specific* improvements to the '{task-ins}', focusing on how to enhance the '{aspect}'.  Provide concrete examples of how these improvements could be implemented in the <summary>. The summary should be maximally information-dense and user-centric, providing a concise and comprehensive picture of the user's emotional state. Each sentence should contain exclusively relevant information about *this specific user*, ideally revealing a new, insightful aspect. Avoid redundancy and general statements.  Prioritize a high information density per sentence for a deep understanding of the individual user profile. Provide concrete examples of how these improvements could be implemented in the <summary>.

Think step by step and take a deep breath. 