"""
API Client for Group Change Params
"""

import requests
from typing import List, Dict, Any, Optional


class GroupChangeParamsAPIClient:
    """Client for Group Change Params API"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Request failed: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._make_request("GET", "/health")
    
    def get_breeds(self) -> List[Dict[str, Any]]:
        """Get available breed options"""
        return self._make_request("GET", "/api/breeds")
    
    def get_color_groups(self) -> List[Dict[str, Any]]:
        """Get color groups"""
        return self._make_request("GET", "/api/color-groups")
    
    def get_colors_by_group(self, group_title: str) -> List[Dict[str, Any]]:
        """Get colors by group"""
        print(f"🔄 API: Запрос цветов для группы '{group_title}'")
        result = self._make_request("GET", f"/api/colors/{group_title}")
        print(f"🔄 API: Получено {len(result)} цветов для группы '{group_title}'")
        return result
    
    def get_order_colors(self, order_id: int) -> List[Dict[str, Any]]:
        """Get colors used in order"""
        return self._make_request("GET", f"/api/orders/{order_id}/colors")
    
    def get_order_info(self, order_id: int) -> Dict[str, Any]:
        """Get order information"""
        return self._make_request("GET", f"/api/orders/{order_id}/info")
    
    def change_breed(self, order_id: int, breed_code: str) -> Dict[str, Any]:
        """Change breed in order"""
        data = {
            "order_id": order_id,
            "breed_code": breed_code
        }
        return self._make_request("POST", "/api/change-breed", json=data)
    
    def change_color(self, order_id: int, new_color: str, new_colorgroup: str, old_colors: List[str]) -> Dict[str, Any]:
        """Change color in order"""
        data = {
            "order_id": order_id,
            "new_color": new_color,
            "new_colorgroup": new_colorgroup,
            "old_colors": old_colors
        }
        return self._make_request("POST", "/api/change-color", json=data)


# Global API client instance
_api_client = None


def get_api_client(base_url: str = "http://localhost:8002") -> GroupChangeParamsAPIClient:
    """Get API client instance"""
    global _api_client
    if _api_client is None:
        _api_client = GroupChangeParamsAPIClient(base_url)
    return _api_client
