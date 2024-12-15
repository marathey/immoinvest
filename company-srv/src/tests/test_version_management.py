import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from typing import Dict

# test_version_management.py

def test_get_company_versions(client: TestClient, auth_headers: Dict):
    # Create a company
    company_data = {
        "company_code": "TEST005",
        "company_name": "Test Company 5",
        "company_country": "IT",
        "company_accounting_standards": "IFRS"
    }
    create_response = client.post("/companies", json=company_data, headers=auth_headers)
    company_id = create_response.json()["company_id"]
    
    # Make some updates to create versions
    updates = [
        {"company_name": "Updated Name 1"},
        {"company_name": "Updated Name 2"},
        {"company_country": "FR"}
    ]
    
    for update in updates:
        client.put(
            f"/companies/{company_id}",
            json=update,
            headers=auth_headers,
            params={"change_reason": "Testing versions"}
        )
    
    # Get versions
    response = client.get(
        f"/companies/{company_id}/versions",
        headers=auth_headers,
        params={"skip": 0, "limit": 10}
    )
    assert response.status_code == 200
    
    versions = response.json()
    assert len(versions) >= 4  # Initial version + 3 updates
    assert all("version_number" in version for version in versions)
    assert all("change_type" in version for version in versions)

def test_restore_company_version(client: TestClient, auth_headers: Dict):
    # Create a company
    company_data = {
        "company_code": "TEST006",
        "company_name": "Original Name",
        "company_country": "IT",
        "company_accounting_standards": "IFRS"
    }
    create_response = client.post("/companies", json=company_data, headers=auth_headers)
    company_id = create_response.json()["company_id"]
    
    # Make an update
    update_data = {"company_name": "Updated Name"}
    client.put(
        f"/companies/{company_id}",
        json=update_data,
        headers=auth_headers,
        params={"change_reason": "Testing restore"}
    )
    
    # Restore to version 1
    response = client.post(
        f"/companies/{company_id}/restore/1",
        headers=auth_headers,
        params={"change_reason": "Testing restore"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["company_name"] == company_data["company_name"]  # Original name