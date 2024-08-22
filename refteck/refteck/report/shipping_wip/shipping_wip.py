# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from datetime import datetime
from frappe.utils import fmt_money,add_days
from frappe.desk.form.assign_to import get


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data, None, None
	
	return columns, data, None, None

def get_columns(filters):
	columns = [
		{
			"fieldname": "so",
			"fieldtype": "Link",
			"label": _("SO"),
			"options": "Sales Order",
			# "hidden":1,
			"width": 200
		},
		{
			"fieldname": "po_date",
			"fieldtype": "Date",
			"label": _("PO date"),
			"width": 110
		},
		{
			"fieldname": "client",
			"fieldtype": "Data",
			"label": _("Client"),
			# "options": "Customer",
			"width": 200
		},
		{
			"fieldname": "assigned_to",
			"fieldtype": "Link",
			"label": _("Assigned to"),
			"options": "User",
			"width": 200
		},
		{
			"fieldname": "incoterm",
			"fieldtype": "Link",
			"label": _("Incoterm"),
			"options": "Incoterm",
			"width": 90
		},
		{
			"fieldname": "code",
			"fieldtype": "Data",
			"label": _("Code"),
			"width": 110
		},
		{
			"fieldname": "po_no",
			"fieldtype": "Data",
			"label": _("PO No."),
			"width": 140
		},
		{
			"fieldname": "buyer",
			"fieldtype": "Link", 
			"label": _("Buyer"),
			"options": "Contact",
			"width": 220
		},
		{
			"fieldname": "supplier",
			"fieldtype": "Link", 
			"label": _("Supplier"),
			"options": "Supplier",
			"width": 200
		},
		{
			"fieldname": "delivery_date",
			"fieldtype": "Date",
			"label": _("Delivery Date"),
			"width": 110
		},
		{
			"fieldname": "company",
			"fieldtype": "Link", 
			"label": _("UK/US"),
			"options": "Company",
			"width": 240
		},
		{
			"fieldname": "updated_payment_terms",
			"fieldtype": "Data",
			"label": _("Payment Terms"),
			"width": 180
		},
		{
			"fieldname": "current_lead_time_ship_date",
			"fieldtype": "Data",
			"label": _("Lead time"),
			"width": 110
		},
		{
			"fieldname": "gbp",
			"fieldtype": "Data",
			"label": _("GBP"), 
			"width": 100
		},
		{
			"fieldname": "euro",
			"fieldtype": "Data",
			"label": _("EURO"), 
			"width": 100
		},
		{
			"fieldname": "usd",
			"fieldtype": "Data",
			"label": _("USD"), 
			"width": 100
		},
		{
			"fieldname": "inr",
			"fieldtype": "Data",
			"label": _("INR"), 
			"width": 100
		},
		{
			"fieldname": "others",
			"fieldtype": "Data",
			"label": _("OTHERS"), 
			"width": 100
		},
 		{
            "fieldname": "order_total",
            "fieldtype": "Data",
            "label": _("Order Total"),
            "width": 100
        },		
		{
			"fieldname": "comments",
			"fieldtype": "Data",
			"label": _("Comments"),
			"width": 200
		},
		]
	return columns

def get_conditions(filters):
	conditions =""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += " and tso.creation between {0} and {1}".format(
        		frappe.db.escape(filters.get("from_date")),
        		frappe.db.escape(add_days(filters.get("to_date"),1)))		
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	
	if filters.client:
		conditions += " and tso.customer = '{0}'".format(filters.client)

	# conditions.append({"per_delivered": ['<', 100], "status": ['!=', "Closed"]})

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(
		"""SELECT
			tso.name as so,
			tso.po_date,
			tso.customer_name as client,
			tso.owner as assigned_to,
			tso.incoterm,
			tpo.custom_order_code as code,
			tso.po_no,
			tso.contact_person as buyer,
			tpo.supplier,
			tso.delivery_date,
			tso.company,
			tpo.custom_updated_payment_terms as updated_payment_terms,
			tpo.custom_current_lead_time_ship_date as current_lead_time_ship_date,
			IF(tso.currency = 'GBP',
			CONCAT('£ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as gbp,
			IF(tso.currency = 'EUR',
			CONCAT('€ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as euro,
			IF(tso.currency = 'USD',
			CONCAT('$ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as usd,
			IF(tso.currency = 'INR',
			CONCAT('₹ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as inr,
			IF(tso.currency NOT IN ('GBP', 'EUR', 'USD', 'INR'), ROUND(sum(tsoi.net_amount),2), '-') as OTHERS,
			tso.grand_total as order_total,
			tpo.custom_shipping_remarks as comments,
			tso.currency,
			tso.creation
		FROM
			`tabSales Order` tso
		inner join `tabSales Order Item` tsoi 
		on
			tsoi.parent = tso.name
		inner join `tabPurchase Order Item` tpoi 
		on
			tpoi.sales_order = tso.name
		inner join `tabPurchase Order` tpo
		on
			tpo.name = tpoi.parent
			and tpoi.sales_order_item = tsoi.name
		where
			tso.per_billed <100
			and tso.name not in (
			select
				tsii.sales_order
			from
				`tabSales Invoice Item` tsii 
			where tsii.docstatus!=2
			)
			{0}
		group by
			tpo.name
		""".format(conditions),filters,as_dict=1,debug=1
	)

	for d in data:
		d['order_total']=fmt_money(d['order_total'], currency=d['currency'])
	return data

@frappe.whitelist()
def create_dialog_data(sales_order):
	print(sales_order, '----------------sales_order')
	template_path = "templates/report_dialog_data.html"
	# frappe.render_template(template_path,  dict(sales_order=sales_order))  
	return frappe.render_template(template_path,  dict(sales_order=sales_order)) 