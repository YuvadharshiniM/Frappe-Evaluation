# Copyright (c) 2026, Yuvadharshini M and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class SparePart(Document):

    def autoname(self):
        if self.part_code:
            self.part_code = self.part_code.upper()

        self.name = make_autoname(f"{self.part_code}-.YYYY.-.####")

    def validate(self):
        if self.selling_price <= self.unit_cost:
            frappe.throw(
                "Selling Price must be greater than Unit Cost."
            )
        
    def on_update(self):
        default_labour_charge = frappe.db.get_value(
            "QuickFix Settings",
            None,
            "default_labour_charge"
        )
        frappe.msgprint(
            f"Default Labour Charge: {default_labour_charge}"
        )