# 🚀 ReelSense API Documentation

Complete REST API for the ReelSense movie recommendation system.

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Authentication](#authentication)
4. [Usage Examples](#usage-examples)
5. [Testing](#testing)

---

## 🚀 Quick Start

### 1. Start the API Server

```bash
cd reelsense_backend

# Make sure models are trained
python train.py  # Skip if already done

# Start the server
python main.py
```

Server will start at: **http://localhost:8000**

### 2. Access Interactive Docs

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "total_movies": 9742,
  "total_users": 610,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 📡 API Endpoints

### Health & Info

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and welcome message |
| `/health` | GET | Health check and system status |
| `/stats` | GET | Detailed statistics and model info |

### Authentication

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/auth/register` | POST | Register new user | No |
| `/api/auth/login` | POST | Login and get JWT token | No |
| `/api/auth/me` | GET | Get current user info | Yes |

### Recommendations

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/recommend` | POST | Get personalized recommendations | No* |
| `/api/explain` | POST | Get explanation for a recommendation | No* |
| `/api/search` | POST | Search movies by title/genre | No |
| `/api/movie/{id}` | GET | Get movie information | No |

### Ratings

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/rate` | POST | Submit a movie rating | No* |
| `/api/user/{id}/ratings` | GET | Get user's rating history | No* |

*Auth optional but recommended for production

---

## 🔐 Authentication

### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

Response:
```json
{
  "user_id": 2,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 2,
  "username": "john_doe"
}
```

### Use Token in Requests

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 💡 Usage Examples

### 1. Get Recommendations

**Simple Request:**
```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "n": 10
  }'
```

**With Explanations:**
```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "n": 5,
    "explain": true,
    "diversify": true,
    "exclude_rated": true
  }'
```

**Response:**
```json
{
  "user_id": 1,
  "recommendations": [
    {
      "movie_id": 68954,
      "title": "Fantastic Mr. Fox (2009)",
      "genres": "Adventure|Animation|Children|Comedy|Crime",
      "score": 0.7701,
      "explanation": {
        "cf_score": 1.0,
        "cf_weight": 0.25,
        "content_score": 0.138,
        "content_weight": 0.25,
        "svd_score": 0.966,
        "svd_weight": 0.35,
        "novelty_score": 0.983,
        "novelty_weight": 0.15,
        "final_score": 0.7701
      }
    }
  ],
  "total": 5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Explain a Recommendation

```bash
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "movie_id": 260
  }'
```

**Response:**
```json
{
  "movie": "Star Wars: Episode IV - A New Hope (1977)",
  "genres": "Action|Adventure|Sci-Fi",
  "overall_score": 0.8234,
  "primary_reason": "collaborative filtering",
  "score_breakdown": {
    "CF": "0.950 (weight: 0.25)",
    "Content": "0.732 (weight: 0.25)",
    "SVD": "0.891 (weight: 0.35)",
    "Novelty": "0.543 (weight: 0.15)"
  },
  "human_explanation": "Users with similar taste to yours loved this movie"
}
```

### 3. Search for Movies

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "star wars",
    "limit": 5
  }'
```

**Response:**
```json
{
  "query": "star wars",
  "results": [
    {
      "movie_id": 260,
      "title": "Star Wars: Episode IV - A New Hope (1977)",
      "genres": "Action|Adventure|Sci-Fi"
    },
    {
      "movie_id": 1196,
      "title": "Star Wars: Episode V - The Empire Strikes Back (1980)",
      "genres": "Action|Adventure|Sci-Fi"
    }
  ],
  "total": 5
}
```

### 4. Submit a Rating

```bash
curl -X POST http://localhost:8000/api/rate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "movie_id": 260,
    "rating": 5.0
  }'
```

**Response:**
```json
{
  "user_id": 1,
  "movie_id": 260,
  "rating": 5.0,
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Rating saved successfully"
}
```

### 5. Get User's Rating History

```bash
curl http://localhost:8000/api/user/1/ratings?limit=10
```

**Response:**
```json
{
  "user_id": 1,
  "ratings": [
    {
      "movie_id": 260,
      "title": "Star Wars: Episode IV - A New Hope (1977)",
      "genres": "Action|Adventure|Sci-Fi",
      "rating": 5.0,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 10
}
```

---

## 🧪 Testing

### Using Python Requests

Create a test file `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# 2. Get recommendations
response = requests.post(
    f"{BASE_URL}/api/recommend",
    json={
        "user_id": 1,
        "n": 5,
        "explain": True
    }
)
print("\nRecommendations:", response.json())

# 3. Search movies
response = requests.post(
    f"{BASE_URL}/api/search",
    json={
        "query": "matrix",
        "limit": 3
    }
)
print("\nSearch results:", response.json())

# 4. Submit rating
response = requests.post(
    f"{BASE_URL}/api/rate",
    json={
        "user_id": 1,
        "movie_id": 260,
        "rating": 5.0
    }
)
print("\nRating submitted:", response.json())
```

Run:
```bash
python test_api.py
```

### Using cURL

See examples above in Usage Examples section.

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"
5. See response below

---

## 🎯 Key Features

✅ **Explainable Recommendations** - See why each movie was suggested  
✅ **Diversity Optimization** - Avoid filter bubbles  
✅ **Cold Start Handling** - Works for new users  
✅ **Real-time Search** - Find movies instantly  
✅ **Rating System** - Users can provide feedback  
✅ **JWT Authentication** - Secure user sessions  
✅ **Auto-generated Docs** - Interactive API documentation  
✅ **CORS Enabled** - Ready for frontend integration  

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
SECRET_KEY=your-super-secret-key-change-this
MODEL_DIR=model/trained
API_HOST=0.0.0.0
API_PORT=8000
```

### Model Weights

Edit in `api/services/recommendation_service.py` or during training:
```python
hybrid = HybridRecommender(
    alpha=0.25,   # CF weight
    beta=0.25,    # Content weight
    gamma=0.35,   # SVD weight
    delta=0.15    # Novelty weight
)
```

---

## 📝 Notes

- **Demo User**: Username `demo`, Password `demo123`
- **User IDs**: Use existing IDs (1-610) or register new users
- **Ratings**: Currently stored in-memory, persist to DB in production
- **Token Expiry**: JWT tokens expire after 7 days

---

## 🚧 Next Steps

- **Phase 3**: Add PostgreSQL database
- **Phase 4**: Build React frontend
- **Phase 5**: Deploy to cloud

---

**Built with FastAPI + ReelSense ML Models** 🎬
