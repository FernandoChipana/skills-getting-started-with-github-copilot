"""Test suite for activity unregistration functionality"""

import pytest


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_unregister_returns_200(self, client, existing_activity):
        """Test successful unregister returns 200"""
        email = "daniel@mergington.edu"  # Already registered
        response = client.delete(
            f"/activities/{existing_activity}/participants/{email}"
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, existing_activity):
        """Test successful unregister returns confirmation message"""
        email = "olivia@mergington.edu"  # Known to be in Gym Class, not Chess Club
        # First make sure this email is in the target activity
        client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": email}
        )
        
        response = client.delete(
            f"/activities/{existing_activity}/participants/{email}"
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert existing_activity in data["message"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client, nonexistent_activity):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_student_returns_404(self, client, existing_activity):
        """Test unregistering a student not in activity returns 404"""
        email = "notregistered@mergington.edu"
        response = client.delete(
            f"/activities/{existing_activity}/participants/{email}"
        )
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"].lower()

    def test_student_removed_from_participants(self, client, existing_activity):
        """Test that student is actually removed from participants list"""
        email = "michael@mergington.edu"
        
        # Get initial count
        initial = client.get("/activities")
        initial_count = len(initial.json()[existing_activity]["participants"])
        
        # Unregister
        client.delete(
            f"/activities/{existing_activity}/participants/{email}"
        )
        
        # Check new count
        updated = client.get("/activities")
        updated_count = len(updated.json()[existing_activity]["participants"])
        
        assert updated_count == initial_count - 1
        assert email not in updated.json()[existing_activity]["participants"]

    def test_unregister_then_signup_again(self, client, existing_activity):
        """Test that student can sign up again after unregistering"""
        email = "test_signup_again@mergington.edu"
        activity = "Music Band"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
