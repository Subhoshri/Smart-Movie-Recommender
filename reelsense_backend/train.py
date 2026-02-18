"""
Training pipeline for ReelSense
Trains all component models and saves them
"""
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data.loader import DataLoader
from model.collaborative_filter import CollaborativeFilter
from model.content_filter import ContentBasedFilter
from model.svd_model import SVDModel
from model.novelty_diversity import NoveltyBooster, DiversityOptimizer
from model.hybrid_recommender import HybridRecommender


def train_all_models(data_dir: str = "data/raw", model_dir: str = "model/trained"):
    """
    Complete training pipeline
    
    Args:
        data_dir: Directory containing MovieLens CSV files
        model_dir: Directory to save trained models
    """
    print("="*70)
    print("ReelSense Training Pipeline")
    print("="*70)
    
    # Create model directory
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Load data
    print("\n[1/6] Loading MovieLens data...")
    loader = DataLoader(data_dir)
    loader.load_all()
    
    # Get processed data
    movie_data = loader.get_movie_metadata()
    ratings_df = loader.ratings
    movies_df = loader.movies
    
    # Step 2: Train Collaborative Filter
    print("\n[2/6] Training Collaborative Filter...")
    cf_model = CollaborativeFilter(k_neighbors=30)
    cf_model.fit(ratings_df)
    cf_model.save(f"{model_dir}/cf_model.pkl")
    
    # Step 3: Train Content-Based Filter
    print("\n[3/6] Training Content-Based Filter...")
    content_model = ContentBasedFilter()
    content_model.fit(movie_data)
    content_model.save(f"{model_dir}/content_model.pkl")
    
    # Step 4: Train SVD Model
    print("\n[4/6] Training SVD Model...")
    svd_model = SVDModel(n_factors=100, n_epochs=20)
    svd_model.fit(ratings_df)
    svd_model.save(f"{model_dir}/svd_model.pkl")
    
    # Step 5: Train Novelty Booster
    print("\n[5/6] Training Novelty Booster...")
    novelty_booster = NoveltyBooster(alpha=0.3)
    novelty_booster.fit(ratings_df)
    novelty_booster.save(f"{model_dir}/novelty_booster.pkl")
    
    # Step 6: Initialize Hybrid Recommender
    print("\n[6/6] Creating Hybrid Recommender...")
    diversity_optimizer = DiversityOptimizer(movies_df)
    
    hybrid = HybridRecommender(
        alpha=0.25,  # CF
        beta=0.25,   # Content
        gamma=0.35,  # SVD
        delta=0.15   # Novelty
    )
    
    hybrid.fit(
        cf_model=cf_model,
        content_model=content_model,
        svd_model=svd_model,
        novelty_booster=novelty_booster,
        diversity_optimizer=diversity_optimizer,
        ratings_df=ratings_df,
        movies_df=movies_df
    )
    
    hybrid.save(f"{model_dir}/hybrid_recommender.pkl")
    
    # Save data references for API
    ratings_df.to_csv(f"{model_dir}/ratings.csv", index=False)
    movies_df.to_csv(f"{model_dir}/movies.csv", index=False)
    
    print("\n" + "="*70)
    print("Training complete! All models saved to:", model_dir)
    print("="*70)
    
    # Test recommendations
    print("\nTesting recommendations for user 1:")
    recommendations = hybrid.recommend(user_id=1, n=5, explain=True)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Score: {rec['score']}")
        print(f"   Genres: {rec['genres']}")
        if 'explanation' in rec:
            exp = rec['explanation']
            print(f"   CF: {exp['cf_score']:.3f} | Content: {exp['content_score']:.3f} | "
                  f"SVD: {exp['svd_score']:.3f} | Novelty: {exp['novelty_score']:.3f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train ReelSense models")
    parser.add_argument("--data-dir", default="data/raw", help="Path to MovieLens data")
    parser.add_argument("--model-dir", default="model/trained", help="Path to save models")
    
    args = parser.parse_args()
    
    train_all_models(args.data_dir, args.model_dir)
