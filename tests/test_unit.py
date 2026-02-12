import pytest
from pydantic import ValidationError
from api.src.models.product import ProductCreate, Product

def test_product_create_valid():
    """Test creating a valid product."""
    product_data = {
        "name": "Test Product",
        "description": "A description",
        "price": 10.5
    }
    product = ProductCreate(**product_data)
    assert product.name == "Test Product"
    assert product.price == 10.5

def test_product_create_invalid_price_string():
    """Test that a string price raises a validation error."""
    product_data = {
        "name": "Test Product",
        "description": "A description",
        "price": "not-a-number"
    }
    with pytest.raises(ValidationError) as excinfo:
        ProductCreate(**product_data)
    assert "Input should be a valid number" in str(excinfo.value)

def test_product_create_invalid_price_negative():
    """Test that a negative price raises a validation error."""
    product_data = {
        "name": "Test Product",
        "description": "A description",
        "price": -1.0
    }
    with pytest.raises(ValidationError) as excinfo:
        ProductCreate(**product_data)
    assert "Input should be greater than 0" in str(excinfo.value)

def test_product_model_id_generation():
    """Test that the Product model generates a UUID id."""
    product_data = {
        "name": "Test Product",
        "description": "A description",
        "price": 10.5
    }
    product = Product(**product_data)
    assert product.id is not None
    assert len(product.id) == 36 # UUID length
