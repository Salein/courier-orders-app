"""JSON file storage for orders. Single-user local app."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from models import OrderCreate, OrderResponse, OrderStatus

logger = logging.getLogger(__name__)


class OrderStorage:
    """Simple file-based storage for orders."""

    def __init__(self) -> None:
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "orders.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Create empty orders file if not exists."""
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps([]))

    def _load(self) -> list[dict]:
        """Load raw order dicts from file."""
        try:
            raw = self.file_path.read_text()
            return json.loads(raw) if raw else []
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to load orders: %s", e)
            return []

    def _save(self, orders: list[dict]) -> None:
        """Save order dicts to file."""
        try:
            self.file_path.write_text(json.dumps(orders, indent=2, ensure_ascii=False))
        except OSError as e:
            logger.error("Failed to save orders: %s", e)

    def create_order(self, order: OrderCreate) -> OrderResponse:
        """Add a new order to storage."""
        orders = self._load()
        order_dict = order.model_dump(mode="json")
        orders.append(order_dict)
        self._save(orders)
        return order

    def get_orders(self, status: Optional[OrderStatus] = None) -> list[OrderResponse]:
        """Retrieve orders, optionally filtered by status."""
        orders = self._load()
        result = []
        for o in orders:
            if status is not None and o.get("status") != status:
                continue
            result.append(OrderResponse(**o))
        return result

    def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """Get a single order by ID."""
        orders = self._load()
        for o in orders:
            if o.get("id") == order_id:
                return OrderResponse(**o)
        return None

    def close_order(self, order_id: str) -> Optional[OrderResponse]:
        """Set order status to closed."""
        orders = self._load()
        for i, o in enumerate(orders):
            if o.get("id") == order_id:
                o["status"] = OrderStatus.CLOSED.value
                self._save(orders)
                return OrderResponse(**o)
        return None

    def update_order(self, order_id: str, **updates) -> Optional[OrderResponse]:
        """Update fields of an existing order."""
        orders = self._load()
        for i, o in enumerate(orders):
            if o.get("id") == order_id:
                o.update(updates)
                self._save(orders)
                return OrderResponse(**o)
        return None
