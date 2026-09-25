import frappe

def after_install():
    create_default_device_types()
    create_default_settings()
    frappe.msgprint("QuickFix installed successfully!")

def create_default_device_types():
    device_types = ["Smartphone", "Laptop", "Tablet"]

    for device_type in device_types:
        if not frappe.db.exists("Device Type", device_type):
            doc = frappe.new_doc("Device Type")
            doc.device_type = device_type
            doc.insert(ignore_permissions=True)

def create_default_settings():
    settings = frappe.get_single("QuickFix Settings")

    if not settings.shop_name:
        settings.shop_name = "QuickFix"

    if not settings.manager_email:
        settings.manager_email = "manager@example.com"

    if not settings.default_labour_charge:
        settings.default_labour_charge = 500

    settings.low_stock_alert_enabled = 1

    settings.save(ignore_permissions=True)