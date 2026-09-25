frappe.query_reports["Technician Performance"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "technician",
            label: __("Technician"),
            fieldtype: "Link",
            options: "Technician"
        }
    ],
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "completion_rate" && data) {
            if (data.completion_rate < 70) {
                value = `<span style="color:red">${value}</span>`;
            } else if (data.completion_rate >= 90) {
                value = `<span style="color:green">${value}</span>`;
            }
        }

        return value;
    }
};