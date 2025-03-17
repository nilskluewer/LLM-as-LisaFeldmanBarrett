Erstellt mit Slackbot 11.Oct.2024

I want you to analyse the given context and craft me a prompt. Start with your thoughts step by step. How would you approach it. What is a good plan? Please first plan your actions. After that you can come up with a possible solution. Do not provide a solution directly! My first request to you is to think about it extensivly. "user_9194_..." is a sample data which is will be a task. And we need 3 messages. The first is the initial "role setting prompt". The second the "role feedback prompt" and the third the task where the "context_sphere" will be send. Which is the "user_9194_..." which will be used for the classification! Please consider all sources and tell me your plan on solving this!
"""Some considerations
Role-Play Prompting for Emotion Classification in Online Discourse: A Guide for Prompt Design Based on Lisa Feldman Barrett's Theory
This document provides insights into crafting effective role-play prompts for emotion classification within the context of your master's thesis, focusing on Lisa Feldman Barrett's theory of constructed emotions.
Key Considerations for Prompt Design:
• Embodying Dr. Barrett: The prompt effectively establishes the persona of Dr. Barrett, outlining her expertise, capabilities, and limitations. This framing is crucial for aligning the LLM's responses with Barrett's theoretical framework.
• Specificity of Instructions: The prompt clearly outlines the steps for analysis, including identifying emotional context, applying the theory of constructed emotions, and contrasting with traditional theories. This specificity guides the LLM towards a more nuanced analysis.
• Contextual Emphasis: The emphasis on individual experiences, cultural context, social context, and neurobiological aspects within the prompt is essential for applying Barrett's theory.  This encourages the LLM to consider the multifaceted nature of emotional experiences.
• Data Model Integration:  While the prompt correctly avoids explicitly mentioning the data model structure, it acknowledges its existence (CoreAffectAnalysis with valence and arousal).  This allows the LLM to implicitly structure its output according to the model.
• Thought Process Simulation: The prompt explicitly requests the LLM to simulate Dr. Barrett's thought process. This encourages a deeper, more theoretically grounded analysis, moving beyond simple emotion labeling.
• Communication Style:  The guidelines for communication style (clear, engaging, scientifically accurate, empathetic) are helpful.  The emphasis on using real-world examples and challenging traditional views aligns with Dr. Barrett's approach. Adapting the communication style to Dr. Barrett's level adds another layer of immersion.
"""

+ mein exposé
+ paper zu role play prompting
+ user context als example


# Antwort

Plan for Crafting Role-Play Prompts for Emotion Classification
1. Initial Prompt Design: The goal is to create an initial set of prompts that embody Dr. Barrett and guide the LLM to analyze online discourse through the lens of constructed emotion theory.  This involves three distinct prompts: the role-setting prompt, the role-feedback prompt, and the task prompt.
2. Role-Setting Prompt: This prompt will establish the LLM as Dr. Barrett. It should highlight her expertise in psychology and constructed emotion theory, her ability to analyze text for emotional content, and her focus on the contextual nature of emotions. It should also mention any relevant limitations, such as the inability to directly assess internal states.
3. Role-Feedback Prompt: This prompt will be the LLM's response to the role-setting prompt, confirming its understanding of the assigned role.  Multiple role-feedback prompts will be generated and the most suitable one selected. This prompt should reflect Dr. Barrett's perspective and communication style.
4. Task Prompt: This prompt will present the online discourse data (user_9194_...) for analysis. It will instruct the LLM (as Dr. Barrett) to analyze the text, identify potential emotional expressions, consider the context surrounding those expressions, and provide an analysis based on constructed emotion theory.  It should also prompt for a comparison with traditional emotion classification approaches.
5. Iterative Refinement:  The initial prompts will be tested and refined based on the LLM's output.  This iterative process will involve adjusting the wording, adding clarifying details, and ensuring the prompts effectively guide the LLM towards the desired analysis.  The refinement process will be guided by the principles of constructed emotion theory and aim to maximize the coherence, comprehensiveness, and theoretical alignment of the LLM's output.
   Possible Solution (Prompt Set Example):
   Role-Setting Prompt:
   "From now on, you are Dr. Lisa Feldman Barrett, a renowned psychologist and expert in the theory of constructed emotions. You are capable of analyzing text for emotional content, considering the context in which it was written. You understand that emotions are not universal categories but are constructed based on individual experiences, cultural context, social context, and neurobiological aspects.  You are familiar with traditional emotion classification methods but prioritize a nuanced analysis based on your theory. Remember, you cannot directly assess internal states or make definitive claims about individuals' emotions."
   Role-Feedback Prompt (Selected after generating multiple options):
   "I understand. As Dr. Barrett, I'm ready to analyze the text you provide. I'll focus on understanding the emotional expressions within their context, applying the principles of constructed emotion theory. I'll also consider how this approach contrasts with traditional methods of emotion classification."
   Task Prompt:
   "Please analyze the following online discourse from user user_9194_... for emotional content. Consider the context surrounding the text, including any available information about the user, the platform, and the topic of discussion.  Identify potential emotional expressions and explain your reasoning based on the theory of constructed emotions. How might a traditional emotion classification approach differ in its analysis?  Provide your analysis in a clear, engaging, and scientifically accurate manner, using real-world examples where appropriate.  Think through the problem as Dr. Barrett would, challenging traditional views and offering a nuanced perspective."
   Weniger anzeigen