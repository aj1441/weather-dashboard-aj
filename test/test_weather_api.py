from unittest.mock import patch, Mock
from api import fetch_weather

@patch("api.requests.get")
def test_normal_case(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current": {
            "temp_k": 300,
            "condition": {
                "text": "Clear"
            }
        }
    }
    mock_get.return_value = mock_response

    result = fetch_weather("London")

    assert result == {
        "city": "London",
        "temp_c": 26.9,
        "description": "Clear"
    }