import json
import os
import pickle
import tiktoken
from tqdm import tqdm  # Importiere tqdm für Fortschrittsanzeige
from datetime import datetime
import locale
from vertexai.generative_models import (
    GenerativeModel,
)
import vertexai

def format_date(date_string):
    """
    Formats a given date string to include only up to minutes.
    Utilizes a flexible parser to handle various date formats.
    """
    # Setzt die Locale auf Deutsch für macOS
    locale.setlocale(locale.LC_TIME, 'de_AT.UTF-8') 
    
    # Parse den ursprünglichen Datumsstring
    date_object = datetime.strptime(date_string[:16], "%Y-%m-%dT%H:%M")

    # Formatiere das Datum in das gewünschte Format
    formatted_date = date_object.strftime("%-d. %B %Y, %H:%M Uhr")

    return formatted_date

# Token-Zählfunktion definieren
def count_tokens(text):
    """
    Encodes the given text using a specific tokenization model and returns the count of tokens.
    This is useful for understanding the token consumption for text input, particularly 
    in environments where token count might affect computational resources or cost.
    """
    encoder = tiktoken.get_encoding("cl100k_base")  # Verwende das gpt2 Modell-Encoding als Beispiel
    tokens = encoder.encode(text)
    #gemini_model = GenerativeModel("gemini-1.5-pro-002")
    #model_response = gemini_model.count_tokens([text])
    
    #return model_response.total_tokens
    return len(tokens)

# Lade die Konfigurationen
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

input_json_path = config['input_json_path']
output_folder = config['output_folder_markdown_generation']
pkl_path = config['pkl_path_input_build_context']  # Der Pfad zur .pkl-Datei in config.json
metadata = config['metadata_file']

os.makedirs(output_folder, exist_ok=True)

# Öffne und lade die JSON-Eingabedatei
with open(input_json_path, 'r') as f:
    data = json.load(f)

# Hilfsfunktion für die Überprüfung der Benutzeraktivität
def user_in_comment_or_replies(comment, user_id):
    """
    Checks if a specific user_id is either the author of a comment or any of its replies.
    This recursive function helps traverse nested comment-reply structures 
    to locate the presence of the user in any depth level of the conversation.
    """
    if comment['user_id'] == user_id:
        return True
    for reply in comment.get('replies', []):
        if user_in_comment_or_replies(reply, user_id):
            return True
    return False

# Filterfunktion, die nur relevante Kommentare behält
def filter_comments_by_user(comments, user_id, user_id_to_anon_name, anon_user_counter, level=0):
    """
    Filters comments for a specific user and constructs a new list of comments 
    with associated details, maintaining recursive depth structure.
    It captures all comments and replies made by the user 
    and formats them for Markdown conversion while retaining indentation for hierarchy visualization.
    Anonymizes user names while preserving unique identifiers.
    """
    filtered_comments = []
    indent = "  " * level

    for comment in comments:
        if user_in_comment_or_replies(comment, user_id):
            # Determine the anonymous user name
            if comment['user_id'] == user_id:
                anon_username = "Analyse Zielnutzer"
            else:
                if comment['user_id'] not in user_id_to_anon_name:
                    anon_name = f"User {anon_user_counter[0]}"
                    user_id_to_anon_name[comment['user_id']] = anon_name
                    anon_user_counter[0] += 1
                anon_username = user_id_to_anon_name[comment['user_id']]
            
            new_comment = {
                "user_name": anon_username,
                "comment_headline": comment['comment_headline'],
                "comment_text": comment['comment_text'],
                "comment_created_at": comment['comment_created_at'],
                "replies": filter_comments_by_user(
                    comment.get('replies', []), user_id, user_id_to_anon_name, anon_user_counter, level + 1
                )
            }
            filtered_comments.append(new_comment)

    return filtered_comments

# Funktion zur Generierung einer Markdown-Struktur
def generate_comment_markdown(comments, level=0):
    """
    Generiert einen Markdown-formatierten String aus einer Liste von verschachtelten Kommentaren,
    wobei Blockquotes (" > ") verwendet werden, um die Einrückung darzustellen. Für jede
    Verschachtelungsebene wird ein zusätzliches ">" eingefügt. In jeder Zeile werden zwei Leerzeichen
    am Ende angehängt, um einen Zeilenumbruch in der Markdown-Vorschau zu erzwingen.

    Beispiel:
      - Ebene 0 (Top-Level): Präfix ist "> "
      - Ebene 1 (Antworten): Präfix ist ">> "
      - Ebene 2 (verschachtelte Antworten): Präfix ist ">>> "

    Jede Kommentarzeile wird formatiert als:
      • Benutzername und der Hinweis "schreibt:" (auf Ebene 0) oder "antwortet:" (bei tieferen Ebenen)
      • Die Überschrift (bzw. ein Standardtext, falls keine Überschrift vorhanden)
      • Der Kommentartext sowie das Datum, jeweils mit dem gleichen Blockquote-Präfix.

    Args:
      comments (list): Eine Liste von Kommentar-Dictionaries, die mindestens die folgenden Keys enthalten:
                       - 'user_name'
                       - 'comment_headline'
                       - 'comment_text'
                       - 'comment_created_at'
                       - 'replies' (optional, als Liste weiterer Kommentare)
      level (int): Die aktuelle Verschachtelungsebene (0 für Top-Level-Kommentare).

    Returns:
      str: Ein einzelner Markdown-formattierter String, der den gesamten Kommentarstrang darstellt.
    """
    markdown = ""
    # Erstelle das Blockquote-Präfix: Ebene 0 -> "> ", Ebene 1 -> ">> ", usw.
    blockquote = ">" * (level + 1) + " "

    # Wir verwenden "  \n" um einen harten Zeilenumbruch zu erzwingen
    newline = "  \n"

    for comment in comments:
        if level == 0 and markdown: # Check if markdown is already non-empty AND it's a top-level comment
            markdown += "---\n\n" # Add separator before a new top-level comment
        if level == 0:
            markdown += f"{blockquote}{comment['user_name']} schreibt:{newline}"
        else:
            markdown += f"{blockquote}{comment['user_name']} antwortet:{newline}"

        # Überschrift setzen; falls nicht vorhanden, Standardtext verwenden
        headline = comment.get('comment_headline') or "Keine Überschrift vorhanden"
        markdown += f"{blockquote}**Überschrift**: {headline}{newline}"
        markdown += f"{blockquote}**Kommentar**: {comment['comment_text']}{newline}"
        markdown += f"{blockquote}**Kommentiert am** {format_date(comment['comment_created_at'])}{newline}{newline}"

        if comment.get('replies'):
            markdown += generate_comment_markdown(comment['replies'], level + 1)

    return markdown

# Funktion zur Erstellung der Metadatendatei für einen Benutzer
def create_metadata_file(user_id, user_name, user_gender, user_created_at, total_tokens, comments_extracted):
    """
    Creates a JSON metadata file for a user, encapsulating user details 
    and statistics about their commenting activity. 
    This function supports tracking user engagement and data analysis by 
    logging structured profile data and comment history.
    """
    # Overwrite user_name to anonymize
    user_name = "Analyse Zielnutzer"
    metadata = {
        "user_id": int(user_id),
        "user_name": user_name,
        "user_gender": user_gender,
        "user_created_at": user_created_at,
        "total_tokens": int(total_tokens),
        "comments_extracted": int(comments_extracted)
    }

    metadata_filename = os.path.join(output_folder, f"user_{user_id}_metadata.json")
    with open(metadata_filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata file '{metadata_filename}' created.")

# Prozessiert Kommentare eines bestimmten Benutzers
def process_user_comments(data, target_user_id):
    """
    Processes comments for a designated user by finding, filtering, and 
    formatting user-specific comments and replies. Utilizes recursive 
    strategies to fully explore thread structures and collates user detail 
    and engagement information for Markdown generation.
    """
    all_user_comments = ""
    target_user_name, target_gender, target_created_at = "Unbekannt", "Unbekannt", "Unbekannt"

    # Initialize the mapping from user_id to anonymous names
    user_id_to_anon_name = {}
    anon_user_counter = [1]  # Using a list to make it mutable in recursion

    for article_id, article in data.items():
        user_details = find_user_details_in_comments(article.get('comment_threads', []), target_user_id)
        if user_details:
            target_user_name, target_gender, target_created_at = user_details

        header = f"## Artikel: {article['article_title']}\n\n"
        # ID itself has no meaning for classification
        #header += f"- Artikel ID: {article['article_id']}\n"
        header += f"- Veröffentlicht am: {format_date(article['article_publish_date'])}\n"
        header += f"- Kanal: {article['article_channel']}\n"
        header += f"- Ressort: {article['article_ressort_name']}\n"
        header += f"- Gesamtanzahl Kommentare: {article['total_comments']}\n\n"
        header += "### Kommentare\n\n"

        comments = article.get('comment_threads', [])
        user_comments = filter_comments_by_user(
            comments, target_user_id, user_id_to_anon_name, anon_user_counter
        )
        body = generate_comment_markdown(user_comments)

        if body:
            all_user_comments += header + body

    if all_user_comments:
        target_user_name = "Analyse Zielnutzer"  # Overwrite for anonymity
        intro = f"# Context Sphere von: {target_user_name} (Anonymisiert)\n\n"
        intro += "Dies ist eine anonymisierte Übersicht der Aktivitäten des Analyse Zielnutzers im österreichischen Online-Forum „Der Standard“ vom 01.05.2019 bis 31.05.2019. Die Kommentare sind sortiert nach Artikeln – es werden nur Artikel gezeigt, bei denen der Analyse Zielnutzer kommentiert hat, während Threads ohne seinen Beitrag ausgelassen werden. \n\n"
        intro += "Meta-Details wie Veröffentlichungszeit, Kanal und Diskussionsstruktur sind enthalten. Das “>” markiert top-level Kommentare, und jede Antwort erhält einen weiteren “>”. So signalisiert „>>“, „>>>“ usw., dass es sich um direkte Antworten und weiter verschachtelte Kommentare handelt. Wenn der Analyse Zielnutzer mehrere separate Kommentare unter demselben Artikel verfasst hat (d.h. an unterschiedlichen Diskussionssträngen teilgenommen hat), werden diese einzelnen Kommentar-Threads durch eine horizontale Linie (---) voneinander getrennt, um die Übersichtlichkeit zu gewährleisten. \n\n"
        #intro += "## Benutzerdetails\n\n"
        #intro += f"- Benutzername: {target_user_name}\n"
        # Has no relevance for classification
        #intro += f"- Benutzer-ID: {target_user_id}\n"
        #intro += f"- Geschlecht: {target_gender}\n"
        #intro += f"- Konto erstellt am: {format_date(target_created_at)}\n\n---\n\n"

        complete_content = intro + all_user_comments
        token_count = count_tokens(complete_content)
        comments_count = complete_content.count('schreibt:') 

        filename = os.path.join(
            output_folder, f"user_{target_user_id}_comments_{token_count}_tokens.md"
        )
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(complete_content)
        if metadata:
            create_metadata_file(
                target_user_id, target_user_name, target_gender, target_created_at,
                token_count, comments_count)
        
        
def find_user_details_in_comments(comments, target_user_id):
    """
    Searches for user information within a collection of comments, 
    employing recursion to navigate nested replies. This approach 
    ensures that no matter how deeply nested the user's comments are, 
    their details are successfully extracted.
    """
    for comment in comments:
        if comment['user_id'] == target_user_id:
            return comment['user_name'], comment['user_gender'], comment['user_created_at']
        
        # Recursively search in replies
        user_details = find_user_details_in_comments(comment.get('replies', []), target_user_id)
        if user_details:
            return user_details
    
    return None

# Prozessiert alle Benutzer aus der .pkl Datei
def process_all_users():
    """
    Loads a list of user IDs from a provided .pkl file and processes 
    each user's comments and metadata. Utilizes multiprocessing and 
    progress tracking to efficiently handle and monitor large datasets 
    during user data extraction.
    """
    with open(pkl_path, 'rb') as file:
        user_data = pickle.load(file)
        
    if 'ID_CommunityIdentity' not in user_data.columns:
        raise KeyError("The key 'ID_CommunityIdentity' is not found in the DataFrame. Available keys: ", user_data.columns)

    user_ids = user_data['ID_CommunityIdentity'].unique()

    for user_id in tqdm(user_ids, desc="Processing Users"):
        process_user_comments(data, user_id)


# Hauptaufruf
process_all_users()



"""
# %%
import json
with open('./input_output/JSON/articles_with_threads copy.json', 'r') as articles_with_threads:
    threads = json.load(articles_with_threads)
    
vertexai.init(project="rd-ri-genai-dev-2352", location="europe-west1")
gemini_model = GenerativeModel("gemini-1.5-pro-002")

# %%
model_response = gemini_model.count_tokens([f"{threads}"])

# %%
model_response
# %%
"""