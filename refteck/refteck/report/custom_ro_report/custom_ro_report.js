// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Custom RO Report"] = {
	"filters": [
        {
            "fieldname" : "company",
            "label" : __("Company"),
            "fieldtype" : "Link",
            "options" : "Company"
        },
        {
            "fieldname" : "customer",
            "label" : __("Customer"),
            "fieldtype" : "Link",
            "options" : "Customer"
        },
        {
            "fieldname" : "date",
            "label" : __("Date"),
            "fieldtype" : "Date"
        },
        {
            "fieldname" : "status",
            "label" : __("Status"),
            "fieldtype" : "Select",
            "options": [
                        "",
                        "Draft",
                        "Overdue",
                        "Cancelled",
                        "Return",
                        "Credit Note Issued",
                        "Submitted",
                        "Paid",
                        "Unpaid",
                        "Partly Paid"
                    ]
        },
        {
            "fieldname" : "is_ro_set",
            "label" : __("Is RO Set"),
            "fieldtype" : "Select",
            "options": [
                        "",
                        "Set",
                        "Not Set"
                    ]
        }
    ]
};
