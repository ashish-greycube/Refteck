// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["SO Procurement Member"] = {
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
		}
	],
	onload: create_daily_so_btn,
};

function create_daily_so_btn(report) {
    report.page.add_inner_button(
		__("Daily SO Report"),
        () => go_to_daily_so_report(report)
    );
}

function go_to_daily_so_report(report) {
	frappe.open_in_new_tab = false;
	frappe.route_options = {
		date: report.get_values().date,
		procurement_member: report.get_values().procurement_member,
	};                    
	frappe.set_route("query-report", "Daily Sales Order");
	console.log("go_to_daily_so_report")
	console.log(report.get_values().date, "-------report", report.get_values().procurement_member,  "-------member")
}