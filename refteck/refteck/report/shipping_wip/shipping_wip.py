# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from datetime import datetime
from frappe.utils import fmt_money


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data, report_summary = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
	
	return columns, data, None, None, report_summary

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
			"fieldtype": "Link",
			"label": _("Client"),
			"options": "Customer",
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
			"label": _("po_no"),
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
			"fieldname": "comments",
			"fieldtype": "Data",
			"label": _("Comments"),
			"width": 200
		},
		]
	return columns

def get_conditions(filters):
	conditions = []

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions.append(["creation","between", [filters.get("from_date"), filters.get("to_date")]])
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	
	if filters.client:
		conditions.append({"customer_name":filters.client})

	if filters.order_status == "Open":
		conditions.append({"custom_is_order_ready": 0})

	if filters.order_status == "Pipeline":
		conditions.append({"custom_is_order_ready": 1})

	conditions.append({"per_delivered": ['<', 100], "status": ['!=', "Closed"]})

	return conditions

def get_data(filters):

	data = []
	conditions = get_conditions(filters)
	
	so_list = frappe.db.get_list(
			"Sales Order", fields=["name",
						"po_date",
						"customer_name",
						"incoterm", 
						"po_no",
						"contact_person",
						"delivery_date", 
						"company",
						"grand_total",
						"currency",
						"custom_is_order_ready"
						],
						filters=conditions,)
	
	usd = ""
	gbp = ""
	euro = ""
	inr = ""
	others = ""
	for so in so_list:
		# print(so.name, so.grand_total, so.customer_name)
		if so.currency == "USD":
			usd = fmt_money(so.grand_total, currency=so.currency)
		else: usd = " - "
		
		if so.currency == "GBP":
			gbp = fmt_money(so.grand_total, currency=so.currency)
		else: gbp = " - "
		
		if so.currency == "EUR":
			euro = fmt_money(so.grand_total, currency=so.currency)
		else: euro = " - "

		if so.currency == "INR":
			inr = fmt_money(so.grand_total, currency=so.currency)
		else: inr = " - "

		if so.currency != "USD" and  so.currency != "GBP" and so.currency != "EUR" and so.currency != "INR":
			others = fmt_money(so.grand_total, currency=so.currency)
		else: others = " - "

		po_items = frappe.db.get_list(
			"Purchase Order Item", 
			parent_doctype='Purchase Order',fields=["parent"],filters={"sales_order": so.name})
		
		if (len(po_items) > 0):
			for item in po_items:
				po_list = frappe.db.get_list(
				"Purchase Order", fields=["supplier_name",
							"custom_updated_payment_terms",
							"custom_current_lead_time_ship_date",
							"custom_order_code",
							"custom_shipping_remarks"
							],
							filters={"name":item.parent})
			
				for po in po_list:
	
					row = {
							"so":  so.name,
							"po_date": so.po_date,
							"client": so.customer_name,
							"incoterm": so.incoterm,
							"code": po.custom_order_code,
							"po_no": so.po_no,
							"buyer": so.contact_person,
							"supplier": po.supplier_name,
							"delivery_date": so.delivery_date,
							"company": so.company,
							"updated_payment_terms": po.custom_updated_payment_terms,
							"current_lead_time_ship_date": po.custom_current_lead_time_ship_date,
							"gbp": gbp,
							"euro": euro,
							"usd": usd,
							"inr": inr,
							"others": others,
							"comments": po.custom_shipping_remarks
						}
					data.append(row)

		if so.custom_is_order_ready == 0:
			report_summary=[
				{'label':_('<h3 style="color:#A02334">Order Status is Open</h3>')}
				]
		elif so.custom_is_order_ready == 1:
			report_summary=[
				{'label':_('<h3 style="color: #6F4E37">Order Status is Pipeline</h3>')}	
				]
	
	return data, report_summary