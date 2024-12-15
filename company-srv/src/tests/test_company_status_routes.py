import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from typing import Dict

# test_company_status_routes.py

def test_create_company_status(client: TestClient, auth_headers: Dict):
    status_data = {
        "status_code": "ACTIVE",
        "status_name": "Active",
        "status_description": "Company is active",
        "is_active": True
    }
    
    response = client.post("/company-statuses", json=status_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status_code"] == status_data["status_code"]
    assert data["status_name"] == status_data["status_name"]
    assert "status_id" in data

def test_list_company_statuses(client: TestClient, auth_headers: Dict):
    # Create multiple statuses
    statuses = [
        {
            "status_code": f"STATUS{i}",
            "status_name": f"Status {i}",
            "status_description": f"Description {i}",
            "is_active": True
        }
        for i in range(3)
    ]
    
    for status in statuses:
        client.post("/company-statuses", json=status, headers=auth_headers)
    
    response = client.get("/company-statuses", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 3
    assert all(isinstance(status["status_id"], str) for status in data)

def test_update_company_status(client: TestClient, auth_headers: Dict):
    # First create a status
    status_data = {
        "status_code": "TEST_STATUS",
        "status_name": "Test Status",
        "status_description": "Test Description",
        "is_active": True
    }
    create_response = client.post("/company-statuses", json=status_data, headers=auth_headers)
    status_id = create_response.json()["status_id"]
    
    # Update the status
    update_data = {
        "status_name": "Updated Test Status",
        "status_description": "Updated Description"
    }
    response = client.put(f"/company-statuses/{status_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status_name"] == update_data["status_name"]
    assert data["status_description"] == update_data["status_description"]
    assert data["status_code"] == status_data["status_code"]  # Unchanged field
