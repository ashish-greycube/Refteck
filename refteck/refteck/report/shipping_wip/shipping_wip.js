// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Shipping-WIP"] = {
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
		{
			"fieldname": "order_status",
			"label":__("Order Status"),
			"fieldtype": "Select",
			"options": ['Open', 'Pipeline'],
			"default": 'Open'
		},
	],
	// formatter: function (value, row, column, data, default_formatter) {
	// 	value = default_formatter(value, row, column, data);

	// 	if (column.fieldname.includes(__("so"))) {
	// 		// console.log(row[1].content, '--row')
	// 		console.log(value ,'---fieldname')
	// 		value = `<a class="custom-link" data-value="${value}">` + value + `</a>`;
	// 	}
	// 	// console.log(value, '---value')

	// 	return value;
	// },
};

$(document).on("click", ".custom-link", function () {
	const so = $(this).data("value");
	// console.log(document, '---document')
	var s = new frappe.ui.Dialog({
		title: __("Sales Order"),
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "sales_order",
			},
		],
	})
	s.fields_dict.sales_order.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
	s.show();
	frappe.call({
		method: "refteck.refteck.report.shipping_wip.shipping_wip.create_dialog_data",
		args: {
			sales_order:so
		},
		callback: function (v) {
			console.log(v)
			s.set_df_property('sales_order', 'options',v.message)
			// s.hide();
		},
	});
	s.hide();
});