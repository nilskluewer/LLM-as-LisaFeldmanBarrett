
# Learnings: 
# -- man muss immer alle felder einsehen können am enden für volle transparenz! 


# URGENT ------ URGENT


# OFFEN ------ OFFEN

# TODO: Add cycle for improvment taking the critique from the evaluation and then improve summary
# TODO: Wenn richtig evaluiert muss man die llm as a judge auch evaluieren, + few shot examples für gut oder schlechte classifications für max alignment. Eher boolean classification. 
# TODO: mindest token grenze für pipeline -> bring nichts einen satz zu analyisren. 
# TODO: RUN Pipeline on LLama3 -> Server RecSys L40 GPU?
# TODO Use greedy decoding

# ERLEDIGT ----- ERLEDIGT #

# TODO: Mathias Pre-Study

# TODO: Benutzername "unbekannt" ersetzten durch random name oder unbekannt nummer X und dann iterrieren oder so.
# TODO: Cohere, OpenAi, Anthropic, Google anbinden

# OFFset für tokenizer counting, da gemini langsam und teuer und ist clk100 ca. 10% höher zählt als gemini. 
# TOOD: Von "No Comment" und "No Headline" zu descriptiven optionen wechseln wie "Keine Überschrift angegeben" 
# # TODO: Evaluator bauen -> Dataset abspeichern zu den jeweiligen Categorien also einmal core und einmal
#  emotiona anylsis extend. Input ist thought / output ist dann die classfication. Dann evaluieren wie auch
#  in der survey, mit den gleichen fragne???
# TODO: https://platform.openai.com/docs/guides/evals
# TODO: OneShot prompting - TASK, THOUGHT, CLASSFICATION - statt - TASK, THOUGHT; ACTION

# TODO Use Cases: Einbinden das es auch für Terror detection genutzt werden könnte

# TODO: Evaluation des **Inner Monoglogue** dann immer Inner monologue vs. analyse -> HumanEval
# TODO: Write a very bad first summary and then improve it with the model
# TODO SUrvey finden - Survey items bauen!
# TODO: Summary auch strukturieren wie die initial zusammenfassung
# TODO: Added examples to summary call 
# TODO: Classification attributes festlegen durch papers
# TODO: auch auf parameter evaluieren wie: factuality, valid JSON, text quality? Mit OPENAI Evaluators?
    # store: true parameter für evaluation https://platform.openai.com/docs/guides/evals
# TODO: Latence, einfach als metric aufnehmen für evaluation!
# TODO **So, is Role-Play Prompting essentially CoT?** -> It's not quite the same, but rather a potential trigger for it.
# TODO: Labels für die classification: Erregung, Valenz, soziale Verbundenheit, Polarization, Emotionality, Polarization
# TODO: Self-consitentcy implemtneiren wie in SELF-CONSISTENCY IMPROVES CHAIN OF THOUGHT REASONING IN LANGUAGE MODELS beschrieben,
#  aber mit similarity über embeddings statt über paths & wahrscehinlichkeiten,
#  weil wir die log probs nicht für alle modell bekommen. ( 40 request pro model machen -> dann majority voting)
#  ähnlich zu More Agents is all you need
#  ODER
#  **Ensemble-Methoden:**  Hier werden mehrere Modelle mit unterschiedlichen Parametern oder Architekturen kombiniert.
#  Aus Paper Self-Consistency Improves Chain of Thought Reasoning in Language Models

# TODO: Reihenfolge im datamodel ändern das classification immer am ende kommt wegen autoregressiv
# TODO: Vereinfachung vom Data model und nur auf concept von feldmann barrett konzentrieren. FOKUS
# TOOD: Batch processing der anfragen geht schenller und ist günstiger!
# TODO: Prompt herausfinden für Lisa Feldmann Barrett
# TODO: Zero-Shot Role play prompting mit SC (Self consitency) )(Beweis Table 9, paper: Better Zero-Shot Reasoning through Role play prompting)
# TODO: Reasoning step pro attribute
# TODO: Validierungs script 
# TODO: Reworked completly the creation of commen threadss to reduce token count by approaximatly 20% - 25%
# TODO: Recursive emthod for markdown creation work much better as bevore


