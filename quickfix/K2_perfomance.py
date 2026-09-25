import frappe
job_cards = frappe.get_all(
    "Job Card",
    fields=["name", "assigned_technician"]
)
technician_names = [
    jc.assigned_technician
    for jc in job_cards
    if jc.assigned_technician
]
technicians = frappe.get_all(
    "Technician",
    filters={
        "name": ["in", technician_names]
    },
    fields=[
        "name",
        "technician_name",
        "phone"
    ]
)
technician_map = {
    tech.name: tech
    for tech in technicians
}
for jc in job_cards:
    tech = technician_map.get(jc.assigned_technician)

    if tech:
        print(
            tech.technician_name,
            tech.phone
        )