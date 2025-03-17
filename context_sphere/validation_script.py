import pickle
import pandas as pd
import json
from tqdm import tqdm

# Configuration loading
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

markdown_folder = config['output_folder_markdown_generation']
pkl_path = config['input_pkl_path']
json_path = config['input_json_path']

# Step 1: Load the PKL file and extract unique user names
def load_unique_user_names():
    # Load the PKL data
    with open(pkl_path, 'rb') as file:
        pkl_data = pickle.load(file)

    # Ensure the necessary column is present
    if 'UserCommunityName' not in pkl_data.columns:
        raise KeyError("The 'UserCommunityName' column is missing from the DataFrame.")

    # Get unique user names
    unique_user_names = pkl_data['UserCommunityName'].unique()
    print(f"Unique user names from PKL: {unique_user_names}")

    return unique_user_names, pkl_data

unique_user_names, pkl_data = load_unique_user_names()

# Step 2: Count how often each user name appears in the PKL file
def count_user_occurrences_in_pkl(unique_user_names, pkl_data):
    pkl_user_counts = {}

    for user_name in tqdm(unique_user_names, desc="Counting in PKL"):
        count = (pkl_data['UserCommunityName'] == user_name).sum()
        pkl_user_counts[user_name] = count

    return pkl_user_counts

pkl_user_counts = count_user_occurrences_in_pkl(unique_user_names, pkl_data)

# Step 3: Count how often each user name appears in the JSON file using recursion
def count_user_in_json(json_data, target_user_name):
    count = 0

    for article_id, article_data in json_data.items():
        count += count_user_in_threads(article_data.get('comment_threads', []), target_user_name)

    return count

def count_user_in_threads(threads, target_user_name):
    count = 0

    for thread in threads:
        # Check the current comment
        if thread['user_name'] == target_user_name:
            count += 1
        
        # Recursively search replies
        count += count_user_in_threads(thread.get('replies', []), target_user_name)

    return count

def count_user_occurrences_in_json(unique_user_names):
    # Load the JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    json_user_counts = {}

    # Traverse the JSON data and count occurrences using recursion
    for user_name in tqdm(unique_user_names, desc="Counting in JSON"):
        count = count_user_in_json(json_data, user_name)
        json_user_counts[user_name] = count

    return json_user_counts

json_user_counts = count_user_occurrences_in_json(unique_user_names)

# Step 4: Validate counts between PKL and JSON and provide a summary
def validate_user_name_counts(pkl_user_counts, json_user_counts):
    successful_validations = 0
    failed_validations = 0
    discrepancies = []

    for user_name in pkl_user_counts.keys():
        pkl_count = pkl_user_counts.get(user_name, 0)
        json_count = json_user_counts.get(user_name, 0)

        if pkl_count == json_count:
            successful_validations += 1
        else:
            failed_validations += 1
            discrepancies.append(f"Discrepancy for User '{user_name}': PKL={pkl_count}, JSON={json_count}")

    print("\nValidation Summary:")
    print(f"Successful validations: {successful_validations}")
    print(f"Failed validations: {failed_validations}")

    if discrepancies:
        print("\nDiscrepancies:")
        for discrepancy in discrepancies:
            print(discrepancy)

validate_user_name_counts(pkl_user_counts, json_user_counts)
