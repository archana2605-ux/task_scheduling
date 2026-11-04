"""Integration tests for the FastAPI endpoints (using TestClient)."""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_raincast.db"

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_response_structure(self):
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "ecmwf_accessible" in data
        assert "cache_entries" in data

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "RainCast AI"


class TestForecastEndpoints:
    def test_latest_cycle_ifs(self):
        response = client.get("/api/forecasts/latest-cycle?model=ifs")
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "IFS"
        assert "latest_date" in data
        assert "latest_cycle" in data
        assert data["latest_cycle"] in [0, 6, 12, 18]

    def test_latest_cycle_aifs(self):
        response = client.get("/api/forecasts/latest-cycle?model=aifs")
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "AIFS"

    def test_available_steps_ifs(self):
        response = client.get("/api/forecasts/available-steps?model=ifs&cycle=0&max_step=72")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) > 0
        assert all(s <= 72 for s in data["steps"])

    def test_available_parameters(self):
        response = client.get("/api/forecasts/available-parameters?model=ifs")
        assert response.status_code == 200
        data = response.json()
        assert "parameters" in data
        # tp must always be available for IFS
        param_names = [p["shortname"] for p in data["parameters"]]
        assert "tp" in param_names

    def test_cache_endpoint(self):
        response = client.get("/api/forecasts/cache")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["forecasts"], list)

    def test_forecast_summary_ifs(self):
        response = client.get("/api/forecasts/summary?model=ifs")
        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "data_available" in data

    def test_invalid_model_rejected(self):
        response = client.get("/api/forecasts/latest-cycle?model=invalid")
        assert response.status_code == 422  # Validation error


class TestLocationEndpoints:
    def test_search_mumbai(self):
        response = client.get("/api/locations/search?q=mumbai")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        names = [r["name"].lower() for r in data["results"]]
        assert any("mumbai" in n for n in names)

    def test_search_empty_returns_empty(self):
        response = client.get("/api/locations/search?q=zzzznosuchwhere")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0

    def test_states_list(self):
        response = client.get("/api/locations/states")
        assert response.status_code == 200
        data = response.json()
        assert len(data["states"]) > 20
        assert "Maharashtra" in data["states"]

    def test_cities_list(self):
        response = client.get("/api/locations/cities?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0

    def test_cities_by_state(self):
        response = client.get("/api/locations/cities?state=Maharashtra")
        assert response.status_code == 200
        data = response.json()
        # All results should be in Maharashtra
        for c in data["cities"]:
            assert c["state"] == "Maharashtra"


class TestAnalyticsEndpoints:
    def test_rainfall_categories(self):
        response = client.get("/api/analytics/rainfall-categories")
        assert response.status_code == 200
        data = response.json()
        cats = data["categories"]
        assert len(cats) == 7
        # Verify correct threshold order
        assert cats[0]["label"] == "No rainfall"
        assert cats[-1]["label"] == "Extremely heavy"

    def test_india_regions(self):
        response = client.get("/api/analytics/india-regions")
        assert response.status_code == 200
        data = response.json()
        assert len(data["regions"]) == 7
        region_names = [r["name"] for r in data["regions"]]
        assert "South India" in region_names
        assert "North India" in region_names


class TestModelComparison:
    def test_model_info(self):
        response = client.get("/api/comparison/info")
        assert response.status_code == 200
        data = response.json()
        assert "IFS" in data["models"]
        assert "AIFS" in data["models"]
        assert data["models"]["IFS"]["type"] == "Numerical Weather Prediction (NWP)"
        assert data["models"]["AIFS"]["type"] == "Machine Learning Weather Model"
