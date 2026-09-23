import frappe
@frappe.whitelist()
def share_job_card(job_card_name, user_email):
    frappe.share.add(
        "Job Card",
        job_card_name,
        user_email,
        read=1
    )
    return {
        "message": "Job Card shared successfully",
        "job_card": job_card_name,
        "user": user_email
    }
    
# permissions(D2-dont leak data)
#unsafe version of get_job_cards, returns all job cards regardless of user permissions
@frappe.whitelist()
def unsafe_get_job_cards():
    return frappe.get_all(
        "Job Card",
        fields="*"
    )
    
#safe version of get_job_cards, returns only job cards that the user has permission to view
@frappe.whitelist()
def safe_get_job_cards():
    jobs = frappe.get_list(
        "Job Card",
        fields=[
            "name",
            "customer_name",
            "customer_phone",
            "customer_email",
            "device_type",
            "status",
            "assigned_technician"
        ]
    )
    if "QF Manager" not in frappe.get_roles():
        for job in jobs:
            job.pop("customer_phone", None)
            job.pop("customer_email", None)
    return jobs

#Job ready email
@frappe.whitelist()
    def send_job_ready_email(job_card_name):
        job = frappe.get_doc("Job Card", job_card_name)
        if not job.customer_email:
            return
        frappe.sendmail(
            recipients=[job.customer_email],
            subject=f"Job {job.name} is Ready for Delivery",
            message=f"Your repair job {job.name} is ready for delivery."
        )
        
#rename technician
@frappe.whitelist()
def rename_technician(old_name, new_name):
    return frappe.rename_doc(
        "Technician",
        old_name,
        new_name,
        merge=False
    )