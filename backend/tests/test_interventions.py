"""Tests for intervention endpoints"""

import pytest
from fastapi import status


class TestInterventionEndpoints:
    """测试干预措施端点"""
    
    def test_create_intervention_success(self, client, sample_intervention_data):
        """测试成功创建干预措施"""
        response = client.post("/api/v1/interventions/", json=sample_intervention_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_intervention_data["name"]
        assert data["category"] == sample_intervention_data["category"]
        assert "id" in data
    
    def test_list_interventions(self, client, sample_intervention_data):
        """测试获取干预措施列表"""
        # Create an intervention first
        client.post("/api/v1/interventions/", json=sample_intervention_data)
        
        # List interventions
        response = client.get("/api/v1/interventions/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_list_interventions_by_category(self, client):
        """测试按分类获取干预措施"""
        # Create interventions in different categories
        client.post("/api/v1/interventions/", json={
            "name": "Test Exercise",
            "category": "exercise",
            "evidence_level": 2
        })
        client.post("/api/v1/interventions/", json={
            "name": "Test Nutrition",
            "category": "nutrition",
            "evidence_level": 1
        })
        
        # List only exercises
        response = client.get("/api/v1/interventions/?category=exercise")
        assert response.status_code == 200
        data = response.json()
        assert all(item["category"] == "exercise" for item in data)
    
    def test_get_intervention_detail(self, client, sample_intervention_data):
        """测试获取单个干预措施详情"""
        # Create intervention
        create_response = client.post("/api/v1/interventions/", json=sample_intervention_data)
        intervention_id = create_response.json()["id"]
        
        # Get detail
        response = client.get(f"/api/v1/interventions/{intervention_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == intervention_id
        assert data["name"] == sample_intervention_data["name"]
    
    def test_get_nonexistent_intervention(self, client):
        """测试获取不存在的干预措施"""
        response = client.get("/api/v1/interventions/99999")
        assert response.status_code == 404
    
    def test_update_intervention(self, client, sample_intervention_data):
        """测试更新干预措施"""
        # Create intervention
        create_response = client.post("/api/v1/interventions/", json=sample_intervention_data)
        intervention_id = create_response.json()["id"]
        
        # Update intervention
        update_data = {
            "name": "Updated Name",
            "evidence_level": 1
        }
        response = client.put(f"/api/v1/interventions/{intervention_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["evidence_level"] == 1
        # Original fields should remain
        assert data["category"] == sample_intervention_data["category"]
    
    def test_delete_intervention(self, client, sample_intervention_data):
        """测试删除干预措施"""
        # Create intervention
        create_response = client.post("/api/v1/interventions/", json=sample_intervention_data)
        intervention_id = create_response.json()["id"]
        
        # Delete intervention
        response = client.delete(f"/api/v1/interventions/{intervention_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/interventions/{intervention_id}")
        assert get_response.status_code == 404
    
    def test_search_interventions_by_name(self, client):
        """测试按名称搜索干预措施"""
        # Create interventions
        client.post("/api/v1/interventions/", json={
            "name": "维生素D补充剂",
            "category": "supplement",
            "evidence_level": 1
        })
        client.post("/api/v1/interventions/", json={
            "name": "维生素C补充剂",
            "category": "supplement",
            "evidence_level": 1
        })
        
        # Search
        response = client.get("/api/v1/interventions/search/by-name?query=维生素")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "维生素" in data[0]["name"]
    
    def test_get_interventions_by_evidence_level(self, client):
        """测试按证据等级获取干预措施"""
        # Create interventions with different evidence levels
        client.post("/api/v1/interventions/", json={
            "name": "High Evidence",
            "category": "supplement",
            "evidence_level": 1
        })
        client.post("/api/v1/interventions/", json={
            "name": "Low Evidence",
            "category": "supplement",
            "evidence_level": 4
        })
        
        # Get level 1 interventions
        response = client.get("/api/v1/interventions/by-evidence-level/1")
        assert response.status_code == 200
        data = response.json()
        assert all(item["evidence_level"] == 1 for item in data)
