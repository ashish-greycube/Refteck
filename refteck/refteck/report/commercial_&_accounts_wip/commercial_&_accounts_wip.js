// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Commercial & Accounts WIP"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"reqd": 1
		},
		{
			"fieldname": "client",
			"label":__("Client"),
			"fieldtype": "Link",
			"options": "Customer",
		},
	]
};
