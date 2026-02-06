"""Tests for authentication endpoints"""

import pytest
from fastapi import status


class TestAuthEndpoints:
    """测试认证相关端点"""
    
    def test_register_success(self, client, sample_user_data):
        """测试成功注册"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be in response
    
    def test_register_duplicate_username(self, client, sample_user_data):
        """测试重复用户名"""
        # First registration
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Duplicate registration
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client, sample_user_data):
        """测试重复邮箱"""
        # First registration
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Same email, different username
        response = client.post("/api/v1/auth/register", json={
            **sample_user_data,
            "username": "different_user"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, client, sample_user_data):
        """测试成功登录"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, sample_user_data):
        """测试错误密码"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with wrong password
        response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """测试不存在的用户"""
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        assert response.status_code == 401
    
    def test_get_current_user_without_auth(self, client):
        """测试未授权访问用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_with_auth(self, client, sample_user_data):
        """测试授权访问用户信息"""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Get current user info
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
    
    def test_create_health_profile(self, client, sample_user_data):
        """测试创建健康档案"""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Create health profile
        profile_data = {
            "age": 30,
            "gender": "male",
            "weight": 75.5,
            "height": 175.0,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "medical_conditions": ["hypertension"],
            "allergies": ["penicillin"]
        }
        response = client.post(
            "/api/v1/auth/health-profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["age"] == 30
        assert data["gender"] == "male"
        assert "id" in data
    
    def test_create_duplicate_health_profile(self, client, sample_user_data):
        """测试重复创建健康档案"""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Create first profile
        profile_data = {"age": 30}
        client.post(
            "/api/v1/auth/health-profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Try to create again (should fail)
        response = client.post(
            "/api/v1/auth/health-profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
    
    def test_update_health_profile(self, client, sample_user_data):
        """测试更新健康档案"""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Create profile
        client.post(
            "/api/v1/auth/health-profile",
            json={"age": 30},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Update profile
        response = client.put(
            "/api/v1/auth/health-profile",
            json={"age": 31, "weight": 70.0},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 31
        assert data["weight"] == 70.0
