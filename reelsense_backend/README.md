# 🎬 ReelSense Backend

Production-ready hybrid movie recommendation system with explainability.

## 📁 Project Structure

```
reelsense_backend/
├── data/
│   └── loader.py              # Data loading utilities
├── model/
│   ├── collaborative_filter.py    # User-based CF
│   ├── content_filter.py          # TF-IDF content similarity
│   ├── svd_model.py               # Matrix factorization
│   ├── novelty_diversity.py       # Long-tail promotion
│   └── hybrid_recommender.py      # Main hybrid system
├── train.py                   # Training pipeline
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Data

Download MovieLens data and place CSV files in `data/raw/`:

```
data/raw/
├── ratings.csv
├── movies.csv
├── tags.csv
└── links.csv
```

### 3. Train Models

```bash
python train.py --data-dir data/raw --model-dir model/trained
```

This will:
- Load MovieLens data
- Train CF, Content, SVD, and Novelty models
- Save trained models to `model/trained/`
- Show test recommendations

### 4. Use the Models

```python
from model.hybrid_recommender import HybridRecommender

# Load trained model
recommender = HybridRecommender.load("model/trained/hybrid_recommender.pkl")

# Get recommendations
recommendations = recommender.recommend(
    user_id=1,
    n=10,
    explain=True
)

# Get explanation for specific movie
explanation = recommender.get_explanation(user_id=1, movie_id=260)
```

## 🧩 Model Components

### Hybrid Score Formula

```
Score(u,i) = α·CF + β·Content + γ·SVD + δ·Novelty
```

Default weights:
- **α = 0.25** (Collaborative Filtering)
- **β = 0.25** (Content-based)
- **γ = 0.35** (SVD Matrix Factorization)
- **δ = 0.15** (Novelty Boost)

### Components

1. **Collaborative Filter** (`collaborative_filter.py`)
   - User-based cosine similarity
   - K=30 nearest neighbors
   - Predicts ratings based on similar users

2. **Content Filter** (`content_filter.py`)
   - TF-IDF on genres + tags
   - Item-item similarity
   - Recommends similar content to liked movies

3. **SVD Model** (`svd_model.py`)
   - Matrix factorization via Surprise
   - 100 latent factors
   - Captures latent user-item patterns

4. **Novelty Booster** (`novelty_diversity.py`)
   - Promotes lesser-known movies
   - Inverse popularity scoring
   - Improves catalog coverage

5. **Diversity Optimizer** (`novelty_diversity.py`)
   - Reduces filter bubbles
   - Genre-based diversity maximization
   - Ensures varied recommendations

## 📊 Features

✅ **Explainable recommendations** - See why each movie was suggested  
✅ **Diversity optimization** - Avoid filter bubbles  
✅ **Long-tail discovery** - Surface hidden gems  
✅ **Modular architecture** - Easy to extend/modify  
✅ **Production-ready** - Clean code, error handling, serialization  

## 🔧 Configuration

Edit model weights in `train.py` or when initializing:

```python
hybrid = HybridRecommender(
    alpha=0.3,   # More CF influence
    beta=0.2,    # Less content influence
    gamma=0.4,   # More SVD influence
    delta=0.1    # Less novelty boost
)
```

## 🧪 Testing Models

```python
# Test single prediction
result = recommender.predict(user_id=1, movie_id=260, explain=True)
print(result['score'])
print(result['explanation'])

# Test recommendations with diversity
recs = recommender.recommend(
    user_id=1,
    n=10,
    diversify=True,
    explain=True
)
```

## 📈 Next Steps

This is **Step 1** of the end-to-end system. Next phases:

- **Phase 2**: FastAPI backend with REST endpoints
- **Phase 3**: PostgreSQL + Redis for persistence
- **Phase 4**: React frontend
- **Phase 5**: User auth & personalization
- **Phase 6**: Docker deployment

## 📝 Notes

- Models are trained on full MovieLens dataset
- First run will take ~5-10 minutes to train all models
- Trained models are saved as pickle files for fast loading
- Update weights based on your evaluation metrics

## 🤝 Contributing

This codebase is modular and extensible. To add new components:

1. Create new model file in `model/`
2. Implement `fit()`, `predict()`, `save()`, `load()` methods
3. Integrate into `hybrid_recommender.py`
4. Update `train.py` pipeline

---

Built with ❤️ for ReelSense Hackathon
