# test_company_routes.py
import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from typing import Dict

def test_create_company(client: TestClient, auth_headers: Dict):
    company_data = {
        "company_code": "TEST001",
        "company_name": "Test Company",
        "company_country": "US",
        "company_accounting_standards": "GAAP"
    }
    
    response = client.post("/companies", json=company_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["company_code"] == company_data["company_code"]
    assert data["company_name"] == company_data["company_name"]
    assert "company_id" in data
    assert "created_at" in data
    assert "created_by" in data
    assert data["created_by"] == "test-user"

def test_get_company(client: TestClient, auth_headers: Dict):
    # First create a company
    company_data = {
        "company_code": "TEST002",
        "company_name": "Test Company 2",
        "company_country": "UK",
        "company_accounting_standards": "IFRS"
    }
    create_response = client.post("/companies", json=company_data, headers=auth_headers)
    company_id = create_response.json()["company_id"]
    
    # Then get the company
    response = client.get(f"/companies/{company_id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["company_code"] == company_data["company_code"]
    assert data["company_id"] == company_id

def test_list_companies(client: TestClient, auth_headers: Dict):
    # Create multiple companies
    companies = [
        {
            "company_code": f"TEST{i}",
            "company_name": f"Test Company {i}",
            "company_country": "US",
            "company_accounting_standards": "GAAP"
        }
        for i in range(3)
    ]
    
    for company in companies:
        client.post("/companies", json=company, headers=auth_headers)
    
    response = client.get("/companies?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 3
    assert all(isinstance(company["company_id"], str) for company in data)

def test_update_company(client: TestClient, auth_headers: Dict):
    # First create a company
    company_data = {
        "company_code": "TEST003",
        "company_name": "Test Company 3",
        "company_country": "DE",
        "company_accounting_standards": "IFRS"
    }
    create_response = client.post("/companies", json=company_data, headers=auth_headers)
    company_id = create_response.json()["company_id"]
    
    # Update the company
    update_data = {
        "company_name": "Updated Test Company 3",
        "company_country": "FR"
    }
    response = client.put(
        f"/companies/{company_id}",
        json=update_data,
        headers=auth_headers,
        params={"change_reason": "Testing update"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["company_name"] == update_data["company_name"]
    assert data["company_country"] == update_data["company_country"]
    assert data["company_code"] == company_data["company_code"]  # Unchanged field

def test_delete_company(client: TestClient, auth_headers: Dict):
    # First create a company
    company_data = {
        "company_code": "TEST004",
        "company_name": "Test Company 4",
        "company_country": "ES",
        "company_accounting_standards": "IFRS"
    }
    create_response = client.post("/companies", json=company_data, headers=auth_headers)
    company_id = create_response.json()["company_id"]
    
    # Delete the company
    response = client.delete(
        f"/companies/{company_id}",
        headers=auth_headers,
        params={"change_reason": "Testing deletion"}
    )
    assert response.status_code == 200
    
    # Verify company is deleted
    get_response = client.get(f"/companies/{company_id}", headers=auth_headers)
    assert get_response.status_code == 404

