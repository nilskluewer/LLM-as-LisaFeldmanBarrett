import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import os
import json
from typing import List, Dict


# Lade die Konfigurationen
with open('config.json', 'r') as config_file:
    config = json.load(config_file)


class DataPreprocessor:
    def __init__(self, file_path: str):
        """
        Initialize the DataPreprocessor with the file path.

        Args:
            file_path (str): The path to the CSV file containing the data.
        """
        self.file_path = file_path
        self.df = None

    def process(self):
        """
        Process the data by loading it from the CSV file and applying various preprocessing steps.
        """
        self.df = pd.read_csv(self.file_path)
        self._convert_dates()
        self._handle_missing_values()
        self._convert_id_columns()
        self._create_new_features()

    def _convert_dates(self):
        """
        Convert date columns to datetime format.
        """
        date_columns = ['PostingCreatedAt', 'ArticlePublishingDate', 'UserCreatedAt']
        for col in date_columns:
            self.df[col] = pd.to_datetime(self.df[col])

    def _handle_missing_values(self):
        """
        Handle missing values in the data by filling them with appropriate values.
        """
        self.df['PostingHeadline'] = self.df['PostingHeadline'].fillna('Keine Überschrift im Datensatz vorhanden')
        self.df['PostingComment'] = self.df['PostingComment'].fillna('Kein Kommentar im Datensatz vorhanden')
        self.df['UserGender'] = self.df['UserGender'].fillna('Unknown')
        self.df['UserCommunityName'] = self.df['UserCommunityName'].fillna('Unknown')

    def _convert_id_columns(self):
        """
        Convert ID columns to integer type.
        """
        id_columns = ['ID_Posting', 'ID_Posting_Parent', 'ID_CommunityIdentity', 'ID_Article']
        for col in id_columns:
            self.df[col] = self.df[col].fillna(0).astype(int)

    def _create_new_features(self):
        """
        Create new features based on existing columns.
        """
        self.df['CommentLength'] = self.df['PostingComment'].str.len()
        self.df['DaysSinceUserCreation'] = (self.df['PostingCreatedAt'] - self.df['UserCreatedAt']).dt.days
        self.df['IsReply'] = self.df['ID_Posting_Parent'] != 0
        self.df['PostingHour'] = self.df['PostingCreatedAt'].dt.hour
        self.df['PostingDayOfWeek'] = self.df['PostingCreatedAt'].dt.dayofweek

    def save_preprocessed_data(self, output_path: str):
        """
        Save the preprocessed data to a pickle file.

        Args:
            output_path (str): The path where the preprocessed data will be saved.
        """
        with open(output_path, 'wb') as f:
            pickle.dump(self.df, f)
        print(f"Preprocessed data saved to {output_path}")

    @classmethod
    def load_preprocessed_data(cls, input_path: str):
        """
        Load the preprocessed data from a pickle file.

        Args:
            input_path (str): The path to the pickle file containing the preprocessed data.

        Returns:
            DataPreprocessor: An instance of DataPreprocessor with the loaded data.
        """
        with open(input_path, 'rb') as f:
            df = pickle.load(f)
        preprocessor = cls(None)
        preprocessor.df = df
        print(f"Preprocessed data loaded from {input_path}")
        return preprocessor

class CommentThreadManager:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the CommentThreadManager with the preprocessed data.

        Args:
            df (pd.DataFrame): The preprocessed data containing comment information.
        """
        self.df = df

    def build_comment_thread(self, comments: pd.DataFrame, parent_id: int) -> List[Dict]:
        """
        Build a hierarchical structure of comments and their replies.

        Args:
            comments (pd.DataFrame): The comments data for a specific article.
            parent_id (int): The ID of the parent comment.

        Returns:
            List[Dict]: A list of dictionaries representing the comment thread.
        """
        replies = comments[comments['ID_Posting_Parent'] == parent_id]
        return [{
            'id': int(reply['ID_Posting']),
            'parent_id': int(reply['ID_Posting_Parent']) if pd.notnull(reply['ID_Posting_Parent']) else None,
            'user_id': int(reply['ID_CommunityIdentity']),
            'user_name': reply['UserCommunityName'],
            'user_gender': reply['UserGender'],
            'user_created_at': reply['UserCreatedAt'].isoformat() if pd.notnull(reply['UserCreatedAt']) else None,
            'comment_headline': reply['PostingHeadline'],
            'comment_text': reply['PostingComment'],
            'comment_created_at': reply['PostingCreatedAt'].isoformat() if pd.notnull(reply['PostingCreatedAt']) else None,
            'comment_length': int(reply['CommentLength']),
            'article_id': int(reply['ID_Article']),
            'article_publish_date': reply['ArticlePublishingDate'].isoformat() if pd.notnull(reply['ArticlePublishingDate']) else None,
            'article_title': reply['ArticleTitle'],
            'article_channel': reply['ArticleChannel'],
            'article_ressort_name': reply['ArticleRessortName'],
            'replies': self.build_comment_thread(comments, int(reply['ID_Posting']))
        } for _, reply in replies.iterrows()]

    def get_article_threads(self) -> Dict[int, Dict]:
        """
        Get the comment threads for all articles.

        Returns:
            Dict[int, Dict]: A dictionary where keys are article IDs and values are dictionaries representing the article's comment threads.
        """
        articles = {}
        for article_id, article_df in self.df.groupby('ID_Article'):
            root_comments = article_df[article_df['ID_Posting_Parent'].isnull() | (article_df['ID_Posting_Parent'] == 0)]
            threads = self.build_comment_thread(article_df, 0)
            article_meta = article_df.iloc[0]

            articles[int(article_id)] = {
                'article_id': int(article_id),
                'article_title': article_meta['ArticleTitle'],
                'article_publish_date': article_meta['ArticlePublishingDate'].isoformat() if pd.notnull(article_meta['ArticlePublishingDate']) else None,
                'article_channel': article_meta['ArticleChannel'],
                'article_ressort_name': article_meta['ArticleRessortName'],
                'total_comments': len(article_df),
                'root_comments': len(root_comments),
                'comment_threads': threads
            }
        return articles

def main():
    # Main execution
    preprocessed_pkl_path = config["input_pkl_path"]
    input_csv_path = config["input_csv_path"]
    output_path_json = config["output_path_build_json"]

    if not os.path.exists(preprocessed_pkl_path):
        print("Preprocessed data not found. Preprocessing...")
        preprocessor = DataPreprocessor(input_csv_path)
        preprocessor.process()
        preprocessor.save_preprocessed_data(preprocessed_pkl_path)
    else:
        print("Loading preprocessed data...")
        preprocessor = DataPreprocessor.load_preprocessed_data(preprocessed_pkl_path)

    thread_manager = CommentThreadManager(preprocessor.df)
    articles_with_threads = thread_manager.get_article_threads()

    # Save the comprehensive data structure to a JSON file
    
    with open(output_path_json, 'w', encoding='utf-8') as f:
        json.dump(articles_with_threads, f, indent=2)
    print(f"Comprehensive data structure saved to {output_path_json}")

if __name__ == "__main__":
    main()