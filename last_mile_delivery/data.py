import csv
from pathlib import Path

DATA_FILE = Path(__file__).parent / "orders.csv"


# --------------------------------------------------
# LOAD ORDERS
# --------------------------------------------------

def load_orders() -> list[dict]:
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# --------------------------------------------------
# SAVE ORDERS
# --------------------------------------------------

def save_orders(orders: list[dict]) -> None:
    if not orders:
        return

    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)


# --------------------------------------------------
# FIND ORDER BY PHONE (PRIMARY)
# --------------------------------------------------

def find_order_by_phone(phone: str) -> dict | None:
    orders = load_orders()
    for order in orders:
        if order["phone"] == phone:
            return order
    return None


# --------------------------------------------------
# FIND ORDER BY PHONE (ALIAS – DO NOT REMOVE)
# --------------------------------------------------

def get_order_by_phone(phone: str) -> dict | None:
    """
    Alias for find_order_by_phone.
    Exists to keep imports stable across the codebase.
    """
    return find_order_by_phone(phone)


# --------------------------------------------------
# SCHEDULE DELIVERY (CUSTOMER AVAILABLE)
# --------------------------------------------------

def mark_scheduled(order_id: str, scheduled_date: str):
    orders = load_orders()

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "scheduled"
            order["scheduled_date"] = scheduled_date
            order["neighbor_name"] = ""
            order["neighbor_phone"] = ""
            break

    save_orders(orders)


# --------------------------------------------------
# NEIGHBOR / SECURITY DELIVERY
# --------------------------------------------------

def mark_neighbor_delivery(
    order_id: str,
    scheduled_date: str,
    neighbor_name: str,
    neighbor_phone: str = "",
):
    orders = load_orders()

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "scheduled"
            order["scheduled_date"] = scheduled_date
            order["neighbor_name"] = neighbor_name
            order["neighbor_phone"] = neighbor_phone
            break

    save_orders(orders)


# --------------------------------------------------
# CANCEL DELIVERY
# --------------------------------------------------

def cancel_delivery(order_id: str):
    orders = load_orders()

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "cancelled"
            order["scheduled_date"] = ""
            order["neighbor_name"] = ""
            order["neighbor_phone"] = ""
            break

    save_orders(orders)


# --------------------------------------------------
# MARK FAILED
# --------------------------------------------------

def mark_failed(order_id: str):
    orders = load_orders()

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "failed"
            break

    save_orders(orders)
