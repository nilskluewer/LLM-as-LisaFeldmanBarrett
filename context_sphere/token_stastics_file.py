import json
import os

def load_config(config_path='config.json'):
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def get_token_count_from_filename(filename):
    """
    Extract the token count from the filename assuming the format includes '_{token_count}_tokens'.
    Example filename: "chapter_123_tokens.md"
    """
    parts = filename.split('_')
    try:
        # We assume the token count is directly before 'tokens.md'
        # For instance, in "chapter_123_tokens.md", parts would be ['chapter', '123', 'tokens.md']
        # so we take the element before 'tokens.md'.
        token_index = parts.index('tokens.md') - 1
        token_count = int(parts[token_index])
        return token_count
    except (ValueError, IndexError):
        return None

def adjust_for_tokenization_offset(token_count, offset=0.1):
    """
    Adjust the token count by a pre-defined offset percentage.
    This offset accounts for a simpler tokenizer's discrepancy with the final tokenizer in the pipeline.
    """
    adjusted_count = token_count * (1 - offset)
    return adjusted_count

def calculate_statistics(markdown_folder, offset=0.1):
    """
    Calculate statistics including:
      - Total markdown files (found in the folder)
      - Total files with a valid token count extracted
      - Sum, average, and estimated page ranges (using an assumed 250 words per page)
      - Which markdown file had the most tokens (by raw token count)
      
    The adjusted token counts are calculated to account for the tokenizer offset.
    """
    files = os.listdir(markdown_folder)
    adjusted_token_counts = []
    total_markdown_files_found = 0
    max_raw_tokens = 0
    max_token_file = None

    for filename in files:
        if filename.endswith('.md'):
            total_markdown_files_found += 1
            token_count = get_token_count_from_filename(filename)
            if token_count is not None:
                adjusted_token_count = adjust_for_tokenization_offset(token_count, offset)
                adjusted_token_counts.append(adjusted_token_count)
                if token_count > max_raw_tokens:
                    max_raw_tokens = token_count
                    max_token_file = filename

    total_valid_files = len(adjusted_token_counts)
    total_adjusted_tokens = sum(adjusted_token_counts)
    avg_adjusted_tokens = total_adjusted_tokens / total_valid_files if total_valid_files > 0 else 0

    # Calculate average adjusted word count range per file (using 60%-80% heuristic)
    avg_adjusted_word_count_range = (
        int(avg_adjusted_tokens * 60 // 100),
        int(avg_adjusted_tokens * 80 // 100)
    )
    
    # Assuming 250 words per page, derive the estimated book pages for the average
    words_per_page = 250
    avg_adjusted_page_estimation_range = (
        avg_adjusted_word_count_range[0] // words_per_page,
        avg_adjusted_word_count_range[1] // words_per_page
    )

    # Also calculate adjusted token count for the file with the most raw tokens.
    max_adjusted_tokens = adjust_for_tokenization_offset(max_raw_tokens, offset) if max_token_file else None

    return {
        "total_markdown_files_found": total_markdown_files_found,
        "total_files_with_valid_tokens": total_valid_files,
        "total_adjusted_tokens": total_adjusted_tokens,
        "average_adjusted_tokens_per_file": avg_adjusted_tokens,
        "average_adjusted_word_count_range_per_file": avg_adjusted_word_count_range,
        "estimated_book_pages_range_per_file": avg_adjusted_page_estimation_range,
        "max_token_file": max_token_file,
        "max_raw_tokens": max_raw_tokens,
        "max_adjusted_tokens": max_adjusted_tokens
    }

def save_statistics(statistics, markdown_folder):
    """
    Save the calculated statistics to a JSON file named '00_statistics_tokens.json'.
    """
    filepath = os.path.join(markdown_folder, '00_statistics_tokens.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, indent=2)

def main():
    config = load_config()
    markdown_folder = config['output_folder_markdown_generation']

    # Offset value for token count adjustment is 10%
    offset = 0.1
    print(f"Using a tokenization offset of {offset*100}% to account for discrepancies with the pipeline's tokenizer.")

    statistics = calculate_statistics(markdown_folder, offset)
    save_statistics(statistics, markdown_folder)

    print("\nStatistics calculated and saved:")
    print(f"Total markdown files found in folder: {statistics['total_markdown_files_found']}")
    print(f"Markdown files processed (with valid token count): {statistics['total_files_with_valid_tokens']}")
    print(f"Adjusted total token count: {statistics['total_adjusted_tokens']}")
    print(f"Average tokens per file (adjusted): {statistics['average_adjusted_tokens_per_file']}")
    print(f"Average word count range per file (adjusted): {statistics['average_adjusted_word_count_range_per_file']}")
    print(f"Estimated equivalent book pages range per file (assuming 250 words per page): {statistics['estimated_book_pages_range_per_file']} pages")
    
    if statistics['max_token_file']:
        print(f"\nFile with the most tokens: {statistics['max_token_file']}")
        print(f"  Raw token count: {statistics['max_raw_tokens']}")
        print(f"  Adjusted token count: {statistics['max_adjusted_tokens']}")
    else:
        print("\nNo markdown file with a valid token count was found.")

if __name__ == "__main__":
    main()