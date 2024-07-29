# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from frappe.utils import date_diff, today, getdate

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
		
	return columns, data


def get_columns(filters):
	columns = [
		{
			"fieldname": "purchase_order_number",
			"fieldtype": "Data",
			"label": _("Purchase Order Number"),
			"width": 140
		},
		{
			"fieldname": "client_name",
			"fieldtype": "Link",
			"label": _("Client Name"),
			"options": "Contact",
			"width": 170
		},
		{
			"fieldname": "customer",
			"fieldtype": "Link",
			"label": _("Customer"),
			"options": "Customer",
			"width": 170,
			"hidden": 1
		},
		{
			"fieldname": "invoice_number",
			"fieldtype": "Link",
			"label": _("Invoice Number"),
			"options": "Sales Invoice",
			"width": 170
		},
		{
			"fieldname": "invoice_date",
			"fieldtype": "Date",
			"label": _("Invoice Date"),
			"width": 110
		},
		{
			"fieldname": "awb_date",
			"fieldtype": "Date",
			"label": _("AWB Date"),
			"width": 110
		},
		{
			"fieldname": "due_date",
			"fieldtype": "Date",
			"label": _("Due Date"),
			"width": 110
		},
		{
			"fieldname": "days_late",
			"fieldtype": "Data",
			"label": _("Days Late"),   # Today - SI.due_date
			"width": 100
		},
		{
			"fieldname": "invoice_amount",
			"fieldtype": "Data", 
			"label": _("Invoice Amount"),
			"width": 150
		},
		]
	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("to_date") >= filters.get("from_date"):
			conditions += " and posting_date between '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))
	else:
		frappe.throw(_("To Date should be greater then From Date"))

	if filters.customer:
		conditions += " and customer = %(customer)s"
	
	return conditions


def get_data(filters):

	conditions = get_conditions(filters)

	data = frappe.db.sql(""" SELECT name as invoice_number, po_no as purchase_order_number, contact_display as client_name,
					  customer as customer,
					  custom_airway_bill_date as awb_date, posting_date as invoice_date, due_date as due_date, grand_total as invoice_amount
					  FROM `tabSales Invoice` 
					  WHERE outstanding_amount > 0
					  {0}
					 """.format(conditions), filters, as_dict=1)
	
	to_date = getdate(today())
	for row in data:
		row['days_late'] =  date_diff(to_date, row['due_date'])

	# data = []
	



	# si_list = frappe.db.get_list('Sales Invoice',
	# 			fields=['name', 'po_no', 'contact_display', 'posting_date', 'posting_date', 'due_date', 'grand_total'],
	# 			filters=conditions,
	# 			# group_by='contact_display'
	# )
	
	# for si in si_list:
	# 	to_date = getdate(today())
	# 	# print(to_date, '---todate')
	# 	# print(type(to_date))
	# 	# print(type(si.due_date) ,'----------si.due_date')
	# 	# print(date_diff(to_date, si.due_date) ,'------days', si.name)

	# 	days_late = date_diff(to_date, si.due_date)
	# 	# print(type(days_late), '-----days_late')

	# 	row = {
	# 			"purchase_order_number": si.po_no,
	# 			"client_name":  si.contact_display,
	# 			"invoice_number":  si.name,
	# 			"invoice_date":  si.posting_date,
	# 			"awb_date":  si.custom_airway_bill_date,
	# 			"due_date":  si.due_date,
	# 			"days_late":   days_late,
	# 			"invoice_amount":  si.grand_total,
	# 	}
	# 	data.append(row)

	print(data)

	return data
