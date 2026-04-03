// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["QO Submission Report"] = {
	"filters": [
		{
			"fieldname":"name",
			"fieldtype":"Link",
			"label":__("Quotation"),
			"options":"Quotation"
		},
		{
			"fieldname":"customer",
			"fieldtype":"Link",
			"label":__("Party(Customer)"),
			"options":"Customer"
		},
		{
			"fieldname":"from_date",
			"fieldtype":"Date",
			"label":__("Date"),
			"default":frappe.datetime.add_days(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname":"to_date",
			"fieldtype":"Date",
			"label":__("Date"),
			"default":frappe.datetime.add_days(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname":"order_type",
			"fieldtype":"Select",
			"label":__("Order Type"),
			"options":[
						"",
						"Sales",
						"Maintenance",
						"Shopping Cart"
					]
		}
	]
};
