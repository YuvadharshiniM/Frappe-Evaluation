import frappe
from frappe import _
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary
def get_columns():
    return [
        {
            "label": _("Technician"),
            "fieldname": "technician",
            "fieldtype": "Link",
            "options": "Technician",
            "width": 180
        },
        {
            "label": _("Total Jobs"),
            "fieldname": "total_jobs",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": _("Completed"),
            "fieldname": "completed",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": _("Avg Turnaround Days"),
            "fieldname": "avg_turnaround_days",
            "fieldtype": "Float",
            "width": 160
        },
        {
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": _("Completion Rate %"),
            "fieldname": "completion_rate",
            "fieldtype": "Percent",
            "width": 150
        }
    ]
def get_data(filters):
    conditions = [
        ["Job Card", "creation", ">=", filters.get("from_date")],
        ["Job Card", "creation", "<=", filters.get("to_date") + " 23:59:59"]
    ]
    if filters.get("technician"):
        conditions.append(
            ["Job Card", "assigned_technician", "=", filters.get("technician")]
        )
    jobs = frappe.get_list(
        "Job Card",
        filters=conditions,
        fields=[
            "assigned_technician",
            "status",
            "final_amount",
            "diagnosis_date",
            "delivery_date"
        ],
        limit_page_length=0
    )
    technicians = {}
    for job in jobs:
        technician = job.assigned_technician
        if not technician:
            continue
        if technician not in technicians:
            technicians[technician] = {
                "technician": technician,
                "total_jobs": 0,
                "completed": 0,
                "turnaround_total": 0,
                "turnaround_count": 0,
                "revenue": 0
            }
        row = technicians[technician]
        row["total_jobs"] += 1
        row["revenue"] += float(job.final_amount or 0)
        if job.status == "Delivered":
            row["completed"] += 1
            if job.diagnosis_date and job.delivery_date:
                turnaround = (
                    frappe.utils.getdate(job.delivery_date)
                    - frappe.utils.getdate(job.diagnosis_date)
                ).days
                row["turnaround_total"] += turnaround
                row["turnaround_count"] += 1
    data = []
    for row in technicians.values():
        completion_rate = (
            row["completed"] / row["total_jobs"] * 100
            if row["total_jobs"]
            else 0
        )
        avg_turnaround = (
            row["turnaround_total"] / row["turnaround_count"]
            if row["turnaround_count"]
            else 0
        )
        data.append({
            "technician": row["technician"],
            "total_jobs": row["total_jobs"],
            "completed": row["completed"],
            "avg_turnaround_days": round(avg_turnaround, 2),
            "revenue": row["revenue"],
            "completion_rate": round(completion_rate, 2)
        })
    return data
def get_chart(data):
    labels = [row["technician"] for row in data]
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Total Jobs",
                    "values": [row["total_jobs"] for row in data]
                },
                {
                    "name": "Completed",
                    "values": [row["completed"] for row in data]
                }
            ]
        },
        "type": "bar"
    }
def get_report_summary(data):
    total_jobs = sum(row["total_jobs"] for row in data)
    total_revenue = sum(row["revenue"] for row in data)

    best_technician = None

    if data:
        best_technician = max(
            data,
            key=lambda row: row["completion_rate"]
        )["technician"]

    return [
        {
            "value": total_jobs,
            "indicator": "Blue",
            "label": _("Total Jobs"),
            "datatype": "Int"
        },
        {
            "value": total_revenue,
            "indicator": "Green",
            "label": _("Total Revenue"),
            "datatype": "Currency"
        },
        {
            "value": best_technician or "-",
            "indicator": "Green",
            "label": _("Best Technician"),
            "datatype": "Data"
        }
    ]