import frappe
def job_card_query(user):
    if not user:
        user = frappe.session.user
    if "QF Technician" not in frappe.get_roles(user):
        return ""
    technician = frappe.db.get_value(
        "Technician",
        {"user": user},
        "name"
    )
    if not technician:
        return "1=0"
    
    return f"`tabJob Card`.`assigned_technician` = {frappe.db.escape(technician)}"