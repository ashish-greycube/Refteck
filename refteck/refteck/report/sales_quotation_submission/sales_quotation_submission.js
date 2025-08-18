// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Quotation Submission"] = {
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
			"fieldname": "customer_name",
			"label":__("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "procurement_member",
			"label":__("Procurement Member"),
			"fieldtype": "Link",
			"options": "User",
		},
	],

	onload: create_sales_quotation_submission_summary_btn,
};

function create_sales_quotation_submission_summary_btn(report) {
    report.page.add_inner_button(
		__("Summary Report"),
        () => go_to_sales_quotation_submission_summary(report)
    );
}

function go_to_sales_quotation_submission_summary(report) {
	frappe.open_in_new_tab = false;
	frappe.route_options = {
		from_date: report.get_values().from_date,
		to_date: report.get_values().to_date,
		procurement_member: report.get_values().procurement_member,
	};                    
	frappe.set_route("query-report", "Sales Quotation Submission Summary");
	// console.log("go_to_procurement_member_summary")
	// console.log(report.get_values().date, "-------report", report.get_values().procurement_member,  "-------member", report.get_values().customer_name, "-------customer")
}