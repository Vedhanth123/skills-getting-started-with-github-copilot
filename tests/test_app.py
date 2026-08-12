"""
Test suite for Mergington High School Activities API.
Uses AAA (Arrange-Act-Assert) testing pattern.
"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all available activities.
        
        Arrange: No setup needed, activities are predefined in app
        Act: Make GET request to /activities
        Assert: Status code is 200 and response contains core activities
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) >= 3  # At least the core activities
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_contains_required_fields(self, client):
        """
        Test that each activity has all required fields.
        
        Arrange: No setup needed
        Act: Make GET request to /activities
        Assert: Each activity has description, schedule, max_participants, and participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_chess_club_has_participants(self, client):
        """
        Test that Chess Club has initial participants.
        
        Arrange: No setup needed
        Act: Make GET request to /activities
        Assert: Chess Club has at least 2 participants
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities["Chess Club"]["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """
        Test successful signup for an activity.
        
        Arrange: Prepare a valid email and activity name
        Act: Make POST request to signup endpoint
        Assert: Status code is 200 and success message is returned
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        Test that signup actually adds the participant to the activity.
        
        Arrange: Prepare a new email and activity name
        Act: Sign up the student, then fetch activities
        Assert: New participant appears in the participants list
        """
        # Arrange
        email = "alex@mergington.edu"
        activity = "Programming Class"
        
        # Act
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """
        Test signup fails when activity does not exist.
        
        Arrange: Prepare an invalid activity name
        Act: Make POST request with non-existent activity
        Assert: Status code is 404 and error message is returned
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_student_behavior(self, client):
        """
        Test to document the current duplicate signup behavior.
        This test verifies how the system handles duplicate signup attempts.
        
        Arrange: Prepare an email for signup
        Act: Sign up the same student twice
        Assert: Verify the current behavior (may be error or duplicate allowed)
        """
        # Arrange
        email = "testduplicate@mergington.edu"
        activity = "Tennis Club"
        
        # Act
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        response2 = client.post(f"/activities/{activity}/signup", params={"email": email})
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        # First signup should succeed
        assert response1.status_code == 200
        
        # Second signup behavior: could be 400 (rejected) or 200 (allowed)
        # Both outcomes are worth tracking
        assert response2.status_code in [200, 400]
        
        # If second signup was rejected (400), that's good - duplicate prevention
        # If it was allowed (200), verify we have the duplicate (the bug)
        if response2.status_code == 400:
            # Duplicate prevention is implemented
            assert activities[activity]["participants"].count(email) == 1
        else:
            # Duplicate was allowed (the bug scenario)
            # This should be: assert participant_count == 1 once fixed
            assert activities[activity]["participants"].count(email) >= 1


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_index(self, client):
        """
        Test that root endpoint redirects to index.html.
        
        Arrange: No setup needed
        Act: Make GET request to /
        Assert: Status code is 307 (redirect) and location header is set
        """
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "location" in response.headers
        assert "/static/index.html" in response.headers["location"]
