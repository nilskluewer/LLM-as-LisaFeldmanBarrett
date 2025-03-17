import json
import os 
import shutil 
import glob 
import random 
import re 
from tqdm import tqdm 
from datetime import datetime


with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
def create_sample_from_files():
    markdown_folder = config.get('output_folder_markdown_generation')
    output_sample_folder = config.get('output_folder_samples')
    min_token_count = config.get('MIN_TOKEN_COUNT')
    max_token_count = config.get('MAX_TOKEN_COUNT')
    sample_size = config.get('SAMPLE_SIZE')

    if not all([markdown_folder, output_sample_folder, min_token_count, max_token_count, sample_size]):
        print("Error: Missing configuration parameters in config.json.")
        return

    # Create a timestamped directory for the sample output
    now = datetime.now()
    timestamp = now.strftime("%y_%m_%d__%H_%M")

    sample_output_dir = os.path.join(
        output_sample_folder,
        f"sample_size_{sample_size}_tokens_{min_token_count}_to_{max_token_count}_{timestamp}"
    )
    print(f"Creating sample output directory: {sample_output_dir}")
    os.makedirs(sample_output_dir, exist_ok=True)

    metadata_files = glob.glob(os.path.join(markdown_folder, "*_metadata.json"))
    markdown_files_with_tokens = glob.glob(os.path.join(markdown_folder, "*_tokens.md"))

    eligible_files = []

    if metadata_files:
        print(f"Found {len(metadata_files)} metadata files. Processing them.")
        for metadata_file in tqdm(metadata_files, desc="Filtering Files (Metadata)"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                token_count = metadata.get('total_tokens', 0)
                user_id = metadata.get('user_id')

                if user_id is not None and min_token_count <= token_count <= max_token_count:
                    print(f"File eligible: user_id={user_id}, token_count={token_count}")
                    eligible_files.append({"user_id": str(user_id)})
                else:
                    print(f"File not eligible: user_id={user_id}, token_count={token_count}, requires between {min_token_count} and {max_token_count}")
            except Exception as e:
                print(f"Error processing metadata file {metadata_file}: {e}")
    elif markdown_files_with_tokens:
        print(f"No metadata files found. Processing {len(markdown_files_with_tokens)} markdown files based on filename.")
        for md_file in tqdm(markdown_files_with_tokens, desc="Filtering Files (Markdown)"):
            try:
                filename = os.path.basename(md_file)
                match = re.search(r"user_(\d+)_.*_(\d+)_tokens\.md", filename)
                if match:
                    user_id = match.group(1)
                    token_count = int(match.group(2))
                    if min_token_count <= token_count <= max_token_count:
                        print(f"File eligible: user_id={user_id}, token_count={token_count}")
                        eligible_files.append({"user_id": str(user_id)})
                    else:
                        print(f"File not eligible: user_id={user_id}, token_count={token_count}, requires between {min_token_count} and {max_token_count}")
                else:
                    print(f"Could not parse token count from filename: {filename}")
            except Exception as e:
                print(f"Error processing markdown file {md_file}: {e}")
    else:
        print("No metadata files or markdown files with token information found.")
        return

    # Remove duplicates based on user_id
    eligible_files_unique = list({item['user_id']: item for item in eligible_files}.values())
    print(f"Found {len(eligible_files_unique)} unique eligible files.")

    # Randomize eligible files
    random.shuffle(eligible_files_unique)

    # Limit results to specified sample size
    selected_files = eligible_files_unique[:sample_size]
    print(f"Selected {len(selected_files)} files for sampling.")

    for item in tqdm(selected_files, desc="Copying Files"):
        user_id = item['user_id']

        # Find Markdown file for user
        md_file_pattern = os.path.join(markdown_folder, f"user_{user_id}_comments_*_tokens.md")
        md_files = glob.glob(md_file_pattern)

        # Copy Markdown files
        for md_file in md_files:
            try:
                shutil.copy(md_file, sample_output_dir)
                print(f"Copied {md_file} to {sample_output_dir}")
            except Exception as e:
                print(f"Failed to copy {md_file}: {e}")

        # Copy metadata JSON file (if it exists)
        metadata_file = os.path.join(markdown_folder, f"user_{user_id}_metadata.json")
        if os.path.exists(metadata_file):
            try:
                shutil.copy(metadata_file, sample_output_dir)
                print(f"Copied {metadata_file} to {sample_output_dir}")
            except Exception as e:
                print(f"Failed to copy {metadata_file}: {e}")

    print(f"Sample generated in {sample_output_dir}")

# Example invocation of the function
create_sample_from_files()