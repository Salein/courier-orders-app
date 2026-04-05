"""Parse Belarusian receipt OCR text into structured order data.

Focus: phone, address, items (name + qty/price), total_sum.
"""

import logging
import re
from typing import NamedTuple, List

from models import OrderAddress, OrderItem, OrderStatus

logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(
    r"""
    (?:
        \+?375                # country code
        [\s\-]?
        (?:29|25|44|33|17)   # Belarus operator codes
        [\s\-]?
        \d{3}                # first three
        [\s\-]?
        \d{2,3}?             # optional separator, 2-3 digits
        [\s\-]?
        \d{2,3}?             # optional
        [\s\-]?
        \d{2,3}
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Total sum keywords (Russian/Belarusian)
TOTAL_KEYWORDS = [
    "итог",
    "сумма",
    "всего",
    "авсього",
    "усяго",
    "разом",
]

TOTAL_REGEX = re.compile(
    r"(?:%s)[^\d]*([\d]+(?:[.,]\d{2})?)" % "|".join(TOTAL_KEYWORDS),
    re.IGNORECASE,
)

# Belarusian street names (common)
STREET_NAMES = [
    r"пр\.?",
    r"вул\.?",
    r"пер\.?",
    r"пр-кт\.?",
    r"площа?д?",
]

# Simple item pattern: name (words) + quantity (digit or float) + optional price
ITEM_REGEX = re.compile(
    r"""
    ^\s*
    (.+?)                # item name (lazy)
    \s+
    ([\d,.]+)            # quantity or amount
    (?:\s+([\d,.]+))?    # optional price
    \s*$
    """,
    re.VERBOSE,
)


class ParseResult(NamedTuple):
    """Structured data extracted from OCR text."""
    phone: str | None
    address: str | None
    items: List[OrderItem]
    total_sum: float | None


def normalize_number(num_str: str) -> float:
    """Convert '1,234.56' or '1.234,56' to float."""
    cleaned = num_str.strip().replace(" ", "")
    if "," in cleaned and "." in cleaned:
        # Mixed? Assume comma is thousand sep if both present
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        # Could be decimal or thousand; heuristic: if >2 digits after comma -> thousand sep
        if len(cleaned.split(",")[-1]) > 2:
            cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_items(lines: List[str]) -> List[OrderItem]:
    """Extract items from lines that match item pattern."""
    items: List[OrderItem] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = ITEM_REGEX.match(line)
        if match:
            name, qty, price = match.groups()
            name = name.strip()
            try:
                qty_val = normalize_number(qty)
                if price:
                    price_val = normalize_number(price)
                    items.append(OrderItem(name=name, quantity=qty_val, price=price_val))
                else:
                    items.append(OrderItem(name=name, quantity=qty_val))
            except ValueError:
                continue
    return items


def parse_text(ocr_text: str) -> ParseResult:
    """
    Parse OCR text using regex heuristics.

    Args:
        ocr_text: Full OCR output

    Returns:
        ParseResult with structured fields
    """
    lines = [ln.strip() for ln in ocr_text.split("\n") if ln.strip()]

    # Phone: first match
    phone = None
    for line in lines:
        m = PHONE_REGEX.search(line)
        if m:
            phone = m.group(0).strip()
            break

    # Address: look for lines with street keywords or house number patterns
    address = None
    for line in lines:
        low = line.lower()
        if any(re.search(pat, low) for pat in STREET_NAMES) or re.search(r"\d+\s*(?:к\.?|корп\.?|кв\.?)?", low):
            address = line
            break

    # Items: find all item-like lines
    items = parse_items(lines)

    # Total: search all lines for sum
    total_sum = None
    for line in lines:
        m = TOTAL_REGEX.search(line)
        if m:
            total_sum = normalize_number(m.group(1))
            break

    # If we have total and items but items lack individual prices, distribute evenly
    if total_sum and items and all(it.price is None for it in items):
        total_qty = sum(it.quantity for it in items)
        if total_qty > 0:
            for it in items:
                it.price = (it.quantity / total_qty) * total_sum

    return ParseResult(
        phone=phone,
        address=address,
        items=items,
        total_sum=total_sum,
    )
