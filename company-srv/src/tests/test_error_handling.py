import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from typing import Dict

# test_error_handling.py

def test_invalid_company_id(client: TestClient, auth_headers: Dict):
    invalid_id = str(uuid4())
    response = client.get(f"/companies/{invalid_id}", headers=auth_headers)
    assert response.status_code == 404

def test_invalid_auth_token(client: TestClient):
    invalid_headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/companies", headers=invalid_headers)
    assert response.status_code == 401

def test_missing_required_fields(client: TestClient, auth_headers: Dict):
    incomplete_data = {
        "company_name": "Test Company"
        # Missing required fields
    }
    response = client.post("/companies", json=incomplete_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error

def test_duplicate_company_code(client: TestClient, auth_headers: Dict):
    company_data = {
        "company_code": "DUPLICATE",
        "company_name": "Test Company",
        "company_country": "US",
        "company_accounting_standards": "GAAP"
    }
    
    # Create first company
    client.post("/companies", json=company_data, headers=auth_headers)
    
    # Try to create second company with same code
    response = client.post("/companies", json=company_data, headers=auth_headers)
    assert response.status_code in [400, 409]  # Bad request or Conflict