"""FastAPI backend for Courier Orders App.

Endpoints:
- POST /api/upload - upload receipt image
- GET /api/orders - list active orders
- GET /api/orders/{id} - order details
- PATCH /api/orders/{id}/close - close order
"""

import io
import logging
import uuid
from typing import Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image

from models import (
    OrderCreate,
    OrderResponse,
    OrderStatus,
    ErrorDetail,
    OrderAddress,
)
from ocr_service import OCRProcessor
from parser import parse_text
from geocoder import geocode_address
from storage import OrderStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Courier Orders API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для локальной разработки и доступа с телефона
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
ocr = OCRProcessor(languages=["ru", "en"])
storage = OrderStorage()


@app.post("/api/upload", response_model=OrderResponse)
async def upload_receipt(
    file: UploadFile = File(..., description="Receipt image (JPEG/PNG)"),
) -> OrderResponse:
    """
    Upload a receipt image, extract text with OCR, parse order data,
    geocode address, and save to storage.
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file",
            )

        # OCR extraction
        ocr_text, confidence = ocr.extract_text(image_bytes)
        if not ocr_text.strip():
            logger.warning("OCR returned empty text")
            ocr_confidence = 0.0
        else:
            ocr_confidence = confidence

        # Parse structured data
        parsed = parse_text(ocr_text)

        # Determine status
        if not parsed.items and not parsed.phone and not parsed.address:
            status_val = OrderStatus.ERROR
        else:
            status_val = OrderStatus.ACTIVE

        # Build order
        order_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"

        # Geocode address if present
        geocoded: Optional[OrderAddress] = None
        if parsed.address:
            geocoded = await geocode_address(parsed.address, countrycodes="by")
            if not geocoded:
                geocoded = OrderAddress(raw=parsed.address)

        order = OrderCreate(
            id=order_id,
            status=status_val,
            phone=parsed.phone,
            address=geocoded,
            items=parsed.items,
            total_sum=parsed.total_sum,
            ocr_text=ocr_text,
            ocr_confidence=round(ocr_confidence, 3),
            raw_image_name=file.filename,
            created_at=now,
            comment=None,
        )

        # Save to storage
        storage.create_order(order)
        logger.info("Order created: %s", order_id)
        return order

    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload error: {str(e)}",
        )


@app.get("/api/orders", response_model=list[OrderResponse])
async def list_orders(active_only: bool = True) -> list[OrderResponse]:
    """
    Get orders. By default returns only active orders.
    Pass active_only=false to get all orders.
    """
    if active_only:
        return storage.get_orders(status=OrderStatus.ACTIVE)
    else:
        # Return all
        return storage.get_orders(status=None)


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str) -> OrderResponse:
    """Get a single order by ID."""
    order = storage.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@app.patch("/api/orders/{order_id}/close", response_model=OrderResponse)
async def close_order(order_id: str) -> OrderResponse:
    """Set order status to closed."""
    order = storage.close_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


# Health check
@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


# Serve static files (optional; not needed for typical use)
# If you want to serve frontend from backend, you'd configure that here.


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
