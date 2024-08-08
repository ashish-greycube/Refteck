// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Statement of Account"] = {
	"filters": [
		// {
		// 	"fieldname": "from_date",
		// 	"label":__("From Date"),
		// 	"fieldtype": "Date",
        //     "default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30),
		// 	"reqd": 1
		// },
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
			"reqd": 1
		},
		{
			"fieldname": "company",
			"label":__("Company"),
			"fieldtype": "Link",
			"options": "Company",
		},
		{
			"fieldname": "customer",
			"label":__("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1
		}
	],
	onload: create_send_email_button,
};

function create_send_email_button(report) {
    report.page.add_inner_button(
		__("Send Email"),
        () => send_email_to_customer(report)
    );
}

function send_email_to_customer(report) {
	frappe.call({
		method: "refteck.refteck.report.statement_of_account.statement_of_account.get_recipients_send_email",
		args: {
			customer : report.get_values().customer,
		},
		callback: function(r) {
			console.log(r.message)
			let recipients = r.message
			frappe.confirm(__("<b>Do You Want To Send Email To :</b> <br> {0}", [recipients]),
				() => {
					frappe.call({
						method: "refteck.refteck.report.statement_of_account.statement_of_account.send_email_to_customer",
						args: {
							to_date: report.get_values().to_date,
            				company: report.get_values().company || '',
							customer : report.get_values().customer,
							data : report.data,
							report_summary : report.raw_data.report_summary,
							columns : report.columns
						},
						callback: function (r) {
							frappe.msgprint(__("<b>Email Sent to Users </b> <br> {0}", [recipients]));
						},
				})
					
				}, () => {
					return
				}
			)
		}
	})
}