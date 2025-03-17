import pandas as pd
import pickle
import os
import json


class ArticleAnalyzer:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the ArticleAnalyzer with the preprocessed data.

        Args:
            df (pd.DataFrame): The preprocessed data containing article information.
        """
        self.df = df

    def analyze_articles(self):
        """
        Perform analysis on articles to get insights into article count, channels, and resources.
        """
        article_count = self.df['ID_Article'].nunique()
        channel_counts = self.df['ArticleChannel'].value_counts()
        ressort_counts = self.df['ArticleRessortName'].value_counts()

        analysis = {
            'total_articles': article_count,
            'channel_distribution': channel_counts.to_dict(),
            'ressort_distribution': ressort_counts.to_dict()
        }
        
        return analysis

    def filter_and_save_by_ressort(self, ressort_name: str, output_path: str):
        """
        Filter the dataframe to include only entries from the specified ressort and save to a new pickle file.

        Args:
            ressort_name (str): The name of the ressort to filter by.
            output_path (str): The path where the filtered data will be saved.
        """
        filtered_df = self.df[self.df['ArticleRessortName'] == ressort_name]
        
        with open(output_path, 'wb') as f:
            pickle.dump(filtered_df, f)
        
        print(f"Filtered data containing only the '{ressort_name}' ressort saved to {output_path}")


def main():
    preprocessed_file = r"../data/preprocessed/preprocessed_data.pkl"
    preprocessed_file = r"../data/preprocessed/preprocessed_data_inland.pkl"

    if not os.path.exists(preprocessed_file):
        raise FileNotFoundError(f"Preprocessed data not found at {preprocessed_file}. Please ensure the file exists.")
    else:
        print("Loading preprocessed data...")
        with open(preprocessed_file, 'rb') as f:
            df = pickle.load(f)

    analyzer = ArticleAnalyzer(df)
    analysis_result = analyzer.analyze_articles()

    # Save the analysis result to a JSON file
    analysis_output_path = "spheres/article_analysis_inland.json"
    with open(analysis_output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2)
    print(f"Article analysis saved to {analysis_output_path}")

def main_filter():
    preprocessed_file = r"../data/preprocessed/preprocessed_data.pkl"

    if not os.path.exists(preprocessed_file):
        raise FileNotFoundError(f"Preprocessed data not found at {preprocessed_file}. Please ensure the file exists.")
    else:
        print("Loading preprocessed data...")
        with open(preprocessed_file, 'rb') as f:
            df = pickle.load(f)
    # Filter by ressort (e.g., "Inland") and save
    analyzer = ArticleAnalyzer(df)
    analysis_result = analyzer.analyze_articles()

    filtered_output_path = "../data/preprocessed/preprocessed_data_inland.pkl"
    analyzer.filter_and_save_by_ressort("Inland", filtered_output_path)

if __name__ == "__main__":
    main()
    #main_filter()