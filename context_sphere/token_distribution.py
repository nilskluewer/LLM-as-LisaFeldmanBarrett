import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_tokens_from_json(directory):
    total_tokens_list = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):  # Ensure we process only JSON files
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                total_tokens = data.get("total_tokens", 0)
                total_tokens_list.append(total_tokens)
    
    return total_tokens_list

def analyze_tokens(tokens):
    tokens_array = np.array(tokens)

    mean = np.mean(tokens_array)
    median = np.median(tokens_array)
    quantile_25 = np.quantile(tokens_array, 0.25)
    quantile_50 = np.quantile(tokens_array, 0.50)
    quantile_75 = np.quantile(tokens_array, 0.75)
    quantile_95 = np.quantile(tokens_array, 0.95)
    std_dev = np.std(tokens_array)

    # Identifying outliers using z-score
    z_scores = (tokens_array - mean) / std_dev
    outliers = tokens_array[abs(z_scores) > 3]  # More than 3 standard deviations from the mean
    tokens_no_outliers = tokens_array[abs(z_scores) <= 3]

    print(f'Mean: {mean}')
    print(f'Median: {median}')
    print(f'25th Quantile: {quantile_25}')
    print(f'50th Quantile (Median): {quantile_50}')
    print(f'75th Quantile: {quantile_75}')
    print(f'95th Quantile: {quantile_95}')
    print(f'Outliers: {outliers}')

    return tokens_array, tokens_no_outliers, quantile_95

def plot_distributions(tokens, tokens_no_outliers, output_directory):
    sns.set(style="whitegrid")

    # Histogram with Outliers
    plt.figure(figsize=(12, 6))
    sns.histplot(tokens, bins=30, kde=True, color='skyblue')
    plt.title('Distribution of Total Tokens (with Outliers)')
    plt.xlabel('Total Tokens')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(output_directory, 'distribution_with_outliers.png'))
    plt.close()

    # Histogram without Outliers
    plt.figure(figsize=(12, 6))
    sns.histplot(tokens_no_outliers, bins=30, kde=True, color='salmon')
    plt.title('Distribution of Total Tokens (without Outliers)')
    plt.xlabel('Total Tokens')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(output_directory, 'distribution_without_outliers.png'))
    plt.close()

def calculate_percentage_in_ranges(tokens, max_value, step=1000):
    total_files = len(tokens)
    ranges = [(i, i + step) for i in range(0, int(max_value), step)]
    filtered_results = []

    for lower_bound, upper_bound in ranges:
        count_in_range = sum(lower_bound <= t < upper_bound for t in tokens)
        percentage = (count_in_range / total_files) * 100
        if percentage > 1.0:  # Only include ranges with more than 1% of files
            filtered_results.append((lower_bound, upper_bound, count_in_range, percentage))

    return filtered_results

def plot_range_distribution(results, output_directory):
    labels = [f"{lb}-{ub}" for lb, ub, _, _ in results]
    percentages = [percentage for _, _, _, percentage in results]

    plt.figure(figsize=(14, 7))
    plt.bar(labels, percentages, color='slateblue')
    plt.xticks(rotation=90)
    plt.title('Percentage of Files by Token Range (>1% of Total)')
    plt.xlabel('Token Range')
    plt.ylabel('Percentage of Total Files')
    plt.tight_layout()
    plt.savefig(os.path.join(output_directory, 'token_range_distribution.png'))
    plt.close()

if __name__ == "__main__":
    directory_path = './Input_Output/Markdown'
    output_directory = './Documentation'
    os.makedirs(output_directory, exist_ok=True)
    
    tokens = load_tokens_from_json(directory_path)
    tokens_with_outliers, tokens_without_outliers, quantile_95 = analyze_tokens(tokens)
    
    plot_distributions(tokens_with_outliers, tokens_without_outliers, output_directory)

    # Analyze percentage distribution within calculated ranges
    range_results = calculate_percentage_in_ranges(tokens, quantile_95, step=1000)
    
    # Print range results
    print("\nToken Range Analysis (>1%):")
    for lower_bound, upper_bound, count, percentage in range_results:
        print(f"Range {lower_bound} - {upper_bound} tokens: {count} files, {percentage:.2f}% of total")

    # Plot token range distribution
    plot_range_distribution(range_results, output_directory)