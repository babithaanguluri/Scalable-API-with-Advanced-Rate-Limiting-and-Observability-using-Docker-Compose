import requests
import json

BASE_URL = "http://localhost:8080"

def test_create_product_success():
    print("\n--- Testing Product Creation (Success) ---")
    payload = {
        "name": "Laptop",
        "description": "High-performance gaming laptop",
        "price": 1200.50
    }
    response = requests.post(f"{BASE_URL}/api/products", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_product_validation_error_string():
    print("\n--- Testing Validation Error (Price is a string) ---")
    payload = {
        "name": "Invalid Product",
        "description": "This will fail",
        "price": "number"  # This is what caused the user's error
    }
    response = requests.post(f"{BASE_URL}/api/products", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_product_validation_error_negative():
    print("\n--- Testing Validation Error (Price is negative) ---")
    payload = {
        "name": "Broken Product",
        "description": "Negative price",
        "price": -10.0
    }
    response = requests.post(f"{BASE_URL}/api/products", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_protected_action():
    print("\n--- Testing Protected Action (Rate Limiting) ---")
    payload = {"action": "test", "value": 42}
    response = requests.post(f"{BASE_URL}/api/protected-action", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: { {k: v for k, v in response.headers.items() if 'RateLimit' in k} }")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    try:
        test_create_product_success()
        test_create_product_validation_error_string()
        test_create_product_validation_error_negative()
        test_protected_action()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure it's running (docker-compose up).")
