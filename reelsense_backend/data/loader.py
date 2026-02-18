"""
Data loading utilities for ReelSense
"""
import pandas as pd
import pickle
from pathlib import Path


class DataLoader:
    """Handles loading and preprocessing of MovieLens data"""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.ratings = None
        self.movies = None
        self.tags = None
        self.links = None
        
    def load_all(self):
        """Load all MovieLens datasets"""
        self.ratings = pd.read_csv(self.data_dir / "ratings.csv")
        self.movies = pd.read_csv(self.data_dir / "movies.csv")
        self.tags = pd.read_csv(self.data_dir / "tags.csv")
        self.links = pd.read_csv(self.data_dir / "links.csv")
        
        print(f"Loaded {len(self.ratings)} ratings")
        print(f"Loaded {len(self.movies)} movies")
        print(f"Loaded {len(self.tags)} tags")
        
        return self
    
    def get_movie_metadata(self):
        """Merge movies with tags for content-based filtering"""
        # Aggregate tags by movie
        movie_tags = self.tags.groupby('movieId')['tag'].apply(
            lambda x: ' '.join(x.astype(str))
        ).reset_index()
        
        # Merge with movies
        movie_data = self.movies.merge(movie_tags, on='movieId', how='left')
        movie_data['tag'] = movie_data['tag'].fillna('')
        
        # Combine genres and tags for content features
        movie_data['content_features'] = (
            movie_data['genres'].str.replace('|', ' ') + ' ' + movie_data['tag']
        )
        
        return movie_data
    
    def get_user_item_matrix(self):
        """Create user-item rating matrix"""
        return self.ratings.pivot_table(
            index='userId', 
            columns='movieId', 
            values='rating'
        ).fillna(0)
    
    def save_processed(self, output_dir: str = "data/processed"):
        """Save processed data for quick loading"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / "loader.pkl", "wb") as f:
            pickle.dump(self, f)
        
        print(f"Saved processed data to {output_path}")
    
    @staticmethod
    def load_processed(path: str = "data/processed/loader.pkl"):
        """Load pre-processed data"""
        with open(path, "rb") as f:
            return pickle.load(f)
