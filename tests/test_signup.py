"""Test suite for activity signup functionality"""

import pytest


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200(self, client, existing_activity, sample_email):
        """Test successful signup returns 200"""
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, existing_activity):
        """Test successful signup returns confirmation message"""
        email = "unique_test_email@mergington.edu"
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": email}
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert existing_activity in data["message"]

    def test_signup_to_nonexistent_activity_returns_404(self, client, nonexistent_activity, sample_email):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_duplicate_signup_returns_400(self, client, existing_activity):
        """Test that duplicate signup returns 400"""
        email = "michael@mergington.edu"  # Already registered in Chess Club
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_student_added_to_participants(self, client, sample_email):
        """Test that student is actually added to participants list"""
        activity = "Tennis Club"
        
        # Get initial count
        initial = client.get("/activities")
        initial_count = len(initial.json()[activity]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": sample_email}
        )
        
        # Check new count
        updated = client.get("/activities")
        updated_count = len(updated.json()[activity]["participants"])
        
        assert updated_count == initial_count + 1
        assert sample_email in updated.json()[activity]["participants"]

    @pytest.mark.parametrize("email", [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ])
    def test_multiple_students_can_signup(self, client, email):
        """Test that multiple different students can sign up"""
        activity = "Art Club"
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
