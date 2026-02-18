"""
Test script for ReelSense API
Run this to verify all endpoints are working
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_response(response):
    """Pretty print JSON response"""
    if response.status_code >= 400:
        print(f"❌ Error {response.status_code}: {response.text}")
    else:
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


def test_health():
    """Test health check endpoint"""
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200


def test_root():
    """Test root endpoint"""
    print_section("2. Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    return response.status_code == 200


def test_stats():
    """Test stats endpoint"""
    print_section("3. System Statistics")
    response = requests.get(f"{BASE_URL}/stats")
    print_response(response)
    return response.status_code == 200


def test_recommendations():
    """Test recommendation endpoint"""
    print_section("4. Get Recommendations (User 1)")
    
    payload = {
        "user_id": 1,
        "n": 5,
        "explain": True,
        "diversify": True,
        "exclude_rated": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/recommend",
        json=payload
    )
    print_response(response)
    return response.status_code == 200


def test_explanation():
    """Test explanation endpoint"""
    print_section("5. Get Explanation")
    
    payload = {
        "user_id": 1,
        "movie_id": 260  # Star Wars
    }
    
    response = requests.post(
        f"{BASE_URL}/api/explain",
        json=payload
    )
    print_response(response)
    return response.status_code == 200


def test_search():
    """Test movie search"""
    print_section("6. Search Movies")
    
    payload = {
        "query": "star wars",
        "limit": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload
    )
    print_response(response)
    return response.status_code == 200


def test_get_movie():
    """Test get movie info"""
    print_section("7. Get Movie Info")
    
    movie_id = 260
    response = requests.get(f"{BASE_URL}/api/movie/{movie_id}")
    print_response(response)
    return response.status_code == 200


def test_submit_rating():
    """Test submitting a rating"""
    print_section("8. Submit Rating")
    
    payload = {
        "user_id": 1,
        "movie_id": 260,
        "rating": 5.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/rate",
        json=payload
    )
    print_response(response)
    return response.status_code == 200


def test_user_ratings():
    """Test getting user ratings"""
    print_section("9. Get User Ratings")
    
    user_id = 1
    response = requests.get(f"{BASE_URL}/api/user/{user_id}/ratings?limit=5")
    print_response(response)
    return response.status_code == 200


def test_auth_register():
    """Test user registration"""
    print_section("10. Register New User")
    
    # Generate unique username
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    payload = {
        "username": f"test_user_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "test123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=payload
    )
    print_response(response)
    return response.status_code == 200


def test_auth_login():
    """Test user login"""
    print_section("11. Login (Demo User)")
    
    payload = {
        "username": "demo",
        "password": "demo123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=payload
    )
    print_response(response)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        return test_auth_me(token)
    
    return False


def test_auth_me(token):
    """Test getting current user with token"""
    print_section("12. Get Current User")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    print_response(response)
    return response.status_code == 200


def run_all_tests():
    """Run all API tests"""
    print("\n" + "🎬" * 35)
    print("  ReelSense API Test Suite")
    print("🎬" * 35)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("System Stats", test_stats),
        ("Recommendations", test_recommendations),
        ("Explanation", test_explanation),
        ("Movie Search", test_search),
        ("Get Movie Info", test_get_movie),
        ("Submit Rating", test_submit_rating),
        ("User Ratings", test_user_ratings),
        ("User Registration", test_auth_register),
        ("User Login", test_auth_login),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "-"*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n⚠️  Make sure the API server is running at http://localhost:8000")
    print("   Run: python main.py")
    input("\nPress Enter to start tests...")
    
    run_all_tests()
