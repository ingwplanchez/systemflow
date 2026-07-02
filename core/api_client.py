import requests
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=5, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None

    # --- Projects ---
    def get_projects(self) -> List[Dict]:
        return self._request("GET", "/projects") or []

    def create_project(self, name: str, description: str = None, color: str = None) -> Dict:
        return self._request("POST", "/projects", json={"name": name, "description": description, "color": color})

    # --- Tasks ---
    def get_tasks(self, project_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:
        params = {}
        if project_id: params["project_id"] = project_id
        if status: params["status"] = status
        return self._request("GET", "/tasks", params=params) or []

    def create_task(self, task_data: Dict) -> Dict:
        return self._request("POST", "/tasks", json=task_data)

    def update_task(self, task_id: int, updates: Dict) -> Dict:
        return self._request("PATCH", f"/tasks/{task_id}", json=updates)

    # --- Focus Sessions ---
    def start_focus_session(self, project_id: int) -> Dict:
        return self._request("POST", "/focus-sessions", json={"project_id": project_id})

    def get_active_session(self) -> Optional[Dict]:
        return self._request("GET", "/focus-sessions/active")

    def stop_focus_session(self, session_id: int) -> Dict:
        return self._request("PATCH", f"/focus-sessions/{session_id}/stop")

    # --- Settings ---
    def get_settings(self) -> Dict:
        return self._request("GET", "/settings") or {"daily_goal": 4}

    def update_settings(self, daily_goal: int) -> Dict:
        return self._request("PUT", "/settings", json={"daily_goal": daily_goal})

# Singleton instance
api = APIClient()
