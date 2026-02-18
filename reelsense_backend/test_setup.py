"""
Quick test script to verify model structure
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from data.loader import DataLoader
        print("DataLoader imported successfully")
    except Exception as e:
        print(f"DataLoader import failed: {e}")
    
    try:
        from model.collaborative_filter import CollaborativeFilter
        print("CollaborativeFilter imported successfully")
    except Exception as e:
        print(f"CollaborativeFilter import failed: {e}")
    
    try:
        from model.content_filter import ContentBasedFilter
        print("ContentBasedFilter imported successfully")
    except Exception as e:
        print(f"ContentBasedFilter import failed: {e}")
    
    try:
        from model.svd_model import SVDModel
        print("SVDModel imported successfully")
    except Exception as e:
        print(f"SVDModel import failed: {e}")
    
    try:
        from model.novelty_diversity import NoveltyBooster, DiversityOptimizer
        print("NoveltyBooster & DiversityOptimizer imported successfully")
    except Exception as e:
        print(f"Novelty/Diversity import failed: {e}")
    
    try:
        from model.hybrid_recommender import HybridRecommender
        print("HybridRecommender imported successfully")
    except Exception as e:
        print(f"HybridRecommender import failed: {e}")
    
    print("\nAll imports successful! Ready to train models.")

def show_structure():
    """Display project structure"""
    print("\nProject Structure:")
    print("""
reelsense_backend/
├── data/
│   ├── __init__.py
│   └── loader.py
├── model/
│   ├── __init__.py
│   ├── collaborative_filter.py
│   ├── content_filter.py
│   ├── svd_model.py
│   ├── novelty_diversity.py
│   └── hybrid_recommender.py
├── train.py
├── requirements.txt
└── README.md
    """)

if __name__ == "__main__":
    show_structure()
    test_imports()