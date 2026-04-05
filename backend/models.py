"""Pydantic models for the Courier Orders API."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"


class OrderItem(BaseModel):
    """A single line item from a receipt."""
    name: str = Field(..., min_length=1)
    quantity: float = 1.0
    price: Optional[float] = None


class OrderAddress(BaseModel):
    """Geocoded address."""
    raw: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    display_name: Optional[str] = None


class OrderCreate(BaseModel):
    """Response after upload/parse."""
    id: str
    status: OrderStatus
    phone: Optional[str] = None
    address: Optional[OrderAddress] = None
    items: List[OrderItem] = Field(default_factory=list)
    total_sum: Optional[float] = None
    ocr_text: Optional[str] = None
    ocr_confidence: float = 0.0
    raw_image_name: Optional[str] = None
    created_at: str
    comment: Optional[str] = None


class OrderResponse(OrderCreate):
    """Same as OrderCreate but used for GET endpoints."""
    pass


class ErrorDetail(BaseModel):
    """Error response."""
    detail: str
