# Copyright (c) 2026, Yuvadharshini M and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class JobCard(Document):
    def validate(self):
        if not self.customer_phone or not self.customer_phone.isdigit() or len(self.customer_phone) != 10:
            frappe.throw("Customer phone must contain exactly 10 digits.")
            
        status_order = [
            "Draft", 
            "Pending Diagnosis", 
            "Awaiting Customer Approval", 
            "In Repair", 
            "Ready for Delivery", 
            "Delivered", 
            "Cancelled"
        ]
        
        if self.status in status_order[3:6] and not self.assigned_technician:
            frappe.throw("Assigned Technician is required for this status.")
            
        self.parts_total = 0
        for row in self.parts_used:
            quantity = float(row.quantity or 0)
            unit_price = float(row.unit_price or 0)
            row.total_price = quantity * unit_price
            self.parts_total += row.total_price
            
        if not self.labour_charge:
            self.labour_charge = frappe.db.get_single_value(
                "QuickFix Settings", "default_labour_charge"
            ) or 0
            
        self.final_amount = self.parts_total + float(self.labour_charge or 0)

    def before_submit(self):
        if self.status != "Ready for Delivery":
            frappe.throw(
                "Job Card can only be submitted when status is Ready for Delivery."
            )
            
        for row in self.parts_used:
            stock_qty = frappe.db.get_value(
                "Spare Part", row.part, "stock_qty"
            )
            if stock_qty < row.quantity:
                frappe.throw(
                    f"Insufficient stock for {row.part}. Available: {stock_qty}, Required: {row.quantity}."
                )

    def on_submit(self):
        for row in self.parts_used:
            stock_qty = frappe.db.get_value(
                "Spare Part",
                row.part,
                "stock_qty"
            )

            frappe.db.set_value(
                "Spare Part",
                row.part,
                "stock_qty",
                stock_qty - row.quantity,
                update_modified=False
            )

        invoice = frappe.new_doc("Service Invoice")
        invoice.job_card = self.name
        invoice.customer_name = self.customer_name
        invoice.invoice_date = frappe.utils.today()
        invoice.labour_charge = self.labour_charge
        invoice.parts_total = self.parts_total
        invoice.total_amount = self.final_amount
        invoice.payment_status = "Unpaid"
        invoice.insert(ignore_permissions=True)
        
        frappe.enqueue(
            "quickfix.api.send_job_ready_email",
            job_card_name=self.name
        )
        
    def on_cancel(self):
        self.db_set("status", "Cancelled")

        for row in self.parts_used:
            stock_qty = frappe.db.get_value(
                "Spare Part",
                row.part,
                "stock_qty"
            )

            frappe.db.set_value(
                "Spare Part",
                row.part,
                "stock_qty",
                stock_qty + row.quantity,
                update_modified=False
            )

        invoice = frappe.db.get_value(
            "Service Invoice",
            {"job_card": self.name},
            "name"
        )

        if invoice:
            frappe.get_doc("Service Invoice", invoice).cancel()
            
    # def on_trash(self):
    #     if self.status not in ["Draft", "Cancelled"]:
    #         frappe.throw(
    #             "Job Card can only be deleted when status is Draft or Cancelled."
    #         )
    
    def on_update(self):
        pass
