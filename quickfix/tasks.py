import frappe
from frappe.utils import today

def check_low_stock():
    last_run = frappe.db.get_value(
        "Audit Log",
        {
            "action": "low_stock_check",
            "date": today()
        },
        "name"
    )
    if last_run:
        return
    parts = frappe.get_all(
        "Spare Part",
        filters={
            "is_active": 1
        },
        fields=[
            "name",
            "part_name",
            "stock_qty",
            "reorder_level"
        ]
    )
    for part in parts:
        if part.stock_qty <= part.reorder_level:
            pass
    frappe.get_doc({
        "doctype": "Audit Log",
        "action": "low_stock_check",
        "date": today()
    }).insert(ignore_permissions=True)
    frappe.db.commit()