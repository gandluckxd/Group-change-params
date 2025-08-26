"""
Data models for Group Change Params API
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class BreedChangeRequest(BaseModel):
    """Request model for changing breed (wood type)"""
    order_id: int
    breed_code: str


class ColorChangeRequest(BaseModel):
    """Request model for changing color"""
    order_id: int
    new_color: str
    new_colorgroup: str
    old_colors: List[str]


class BreedOption(BaseModel):
    """Available breed option"""
    id: int
    code: str
    type_id: int


class ColorGroup(BaseModel):
    """Color group model"""
    title: str


class Color(BaseModel):
    """Color model"""
    color_id: int
    title: str
    group_title: str


class OrderColor(BaseModel):
    """Color currently used in order"""
    title: str
    count: int


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
