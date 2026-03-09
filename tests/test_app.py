# tests/test_app.py
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture
def reset_activities():
    """Fixture to reset the activities dict to its original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)

def test_root_redirect():
    """Test that GET / redirects to /static/index.html."""
    # Arrange
    # (No special setup needed)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307  # RedirectResponse uses 307 by default
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(reset_activities):
    """Test GET /activities returns the activities dict."""
    # Arrange
    # (Activities are already set up via fixture)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == activities

def test_signup_success(reset_activities):
    """Test successful signup for an activity."""
    # Arrange
    email = "test@example.com"
    activity = "Art Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

def test_signup_duplicate(reset_activities):
    """Test duplicate signup raises an error."""
    # Arrange
    email = "test@example.com"
    activity = "Art Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})  # First signup
    
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})  # Attempt duplicate
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity]["participants"].count(email) == 1  # Ensure only one instance

def test_signup_invalid_activity(reset_activities):
    """Test signup for a non-existent activity raises 404."""
    # Arrange
    email = "test@example.com"
    invalid_activity = "Invalid Activity"
    
    # Act
    response = client.post(f"/activities/{invalid_activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_success(reset_activities):
    """Test successful unregistration from an activity."""
    # Arrange
    email = "test@example.com"
    activity = "Art Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})  # Signup first
    
    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]

def test_unregister_not_signed_up(reset_activities):
    """Test unregistration when not signed up raises an error."""
    # Arrange
    email = "test@example.com"
    activity = "Art Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"

def test_unregister_invalid_activity(reset_activities):
    """Test unregistration for a non-existent activity raises 404."""
    # Arrange
    email = "test@example.com"
    invalid_activity = "Invalid Activity"
    
    # Act
    response = client.delete(f"/activities/{invalid_activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"