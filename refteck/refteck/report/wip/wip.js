// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["WIP"] = {
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
			"fieldname": "sourcing_person",
			"label":__("Sourcing Person"),
			"fieldtype": "Link",
			"options": "User",
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
    }
};
