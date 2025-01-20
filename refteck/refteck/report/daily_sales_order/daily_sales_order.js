// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Sales Order"] = {
	"filters": [
		{
			"fieldname": "date",
			"label":__("Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"reqd": 1
		},
		{
			"fieldname": "procurement_member",
			"label":__("Procurement Member"),
			"fieldtype": "Link",
			"options": "User",
		},
		{
			"fieldname": "customer_name",
			"label":__("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer",
		},
	],
	onload: create_procurement_member_summary_btn,
};

function create_procurement_member_summary_btn(report) {
    report.page.add_inner_button(
		__("Summary Report"),
        () => go_to_procurement_member_summary(report)
    );
}

function go_to_procurement_member_summary(report) {
	frappe.open_in_new_tab = false;
	frappe.route_options = {
		date: report.get_values().date,
		procurement_member: report.get_values().procurement_member,
	};                    
	frappe.set_route("query-report", "SO Procurement Member");
	console.log("go_to_procurement_member_summary")
	console.log(report.get_values().date, "-------report", report.get_values().procurement_member,  "-------member", report.get_values().customer_name, "-------customer")
}