// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["WIP Sourcing Person"] = {
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
			"fieldname": "due_date",
			"label":__("Expected close date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "employee",
			"label":__("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd": 1,
			on_change: function() {
				let employee = this.get_value();
				console.log(employee, "====employee====")
				if(employee){
					frappe.db.get_value("Employee", employee, "user_id").then(res => {
						if(res && res.message.user_id){
							console.log(res.user_id, "====user_id====")
							frappe.query_report.set_filter_value("sourcing_person", res.message.user_id);
							frappe.query_report.refresh();
						}
					})
				}
				else{
						frappe.query_report.set_filter_value("sourcing_person", "");
						frappe.query_report.refresh();
					}
			}
		},
		{
			"fieldname": "sourcing_person",
			"label":__("Sourcing Person"),
			"fieldtype": "Link",
			"options": "User",
			"hidden": 1
		},
		{
			"fieldname": "territory",
			"label":__("Territory"),
			"fieldtype": "Link",
			"options": "Territory",
		},
		{
			"fieldname": "status",
			"label":__("Status"),
			"fieldtype": "Link",
			"options": "Opportunity Item Status"
		},
		{
			"fieldname": "client",
			"label":__("Client"),
			"fieldtype": "Link",
			"options": "Customer",
		},
	],
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname.includes(__("excess_days"))) {
			if(value >= 0){
				value = `<span style="color:green">` + value + `</span>`;
			}
			else{
				value = `<span style="color:red">` + value + `</span>`;
			}
			
		}
        return value;
    },
	onload: set_logged_is_user
};

function set_logged_is_user(frm){
	let logged_user = frappe.session.user;
	console.log(logged_user, "===logged_user===")
	frappe.db.get_value("Employee", {"user_id": logged_user}, "name").then(res => {
		if(res && res.message.name){
			frappe.query_report.set_filter_value("employee", res.message.name);
			frappe.query_report.set_filter_value("sourcing_person", logged_user);
		}
	})
}