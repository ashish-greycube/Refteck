# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)
	
	if not data:
		frappe.msgprint(_("No records found"))
		return columns, data
		
	return columns, data

def get_columns(filters):
	columns = [
		{
			"fieldname": "so",
			"fieldtype": "Link",
			"label": _("ID"),
			"options": "Sales Order",
			# "hidden":1,
			"width": 200
		},
		{
			"fieldname": "customer_name",
			"fieldtype": "Link",
			"label": _("Customer Name"),
			"options": "Customer",
			"width": 110
		},
		{
			"fieldname": "date",
			"fieldtype": "Date",
			"label": _("Date"),
			"width": 110
		},
		{
			"fieldname": "contact_person",
			"fieldtype": "Link",
			"label": _("Contact Person"),
			"options": "Contact",
			"width": 110
		},
		{
			"fieldname": "grade",
			"fieldtype": "Data",
			"label": _("Grade"),
			"width": 110
		},
		{
			"fieldname": "industry_vertical",
			"fieldtype": "Link",
			"label": _("Industry Vertical"),
			"options": "Industry Vertical",
			"width": 110
		},
		{
			"fieldname": "industry_vertical",
			"fieldtype": "Link",
			"label": _("Customer's Purchase Order"),
			"options": "Industry Vertical",
			"width": 110
		},
		{
			"fieldname": "po_no",
			"fieldtype": "Data",
			"label": _("PO No."),
			"width": 140
		},
		{
			"fieldname": "procurement_member",
			"label":_("User(Procurement Member)"),
			"fieldtype": "Link",
			"options": "User",
		},
		{
			"fieldname": "grand_total",
			"fieldtype": "Data",
			"label": _("Grand Total"), 
			"width": 100
		},
		{
			"fieldname": "currency",
			"label":_("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
		},
		{
			"fieldname": "owner", # pending
			"fieldtype": "Data",
			"label": _("Owner"),
			"width": 110
		},
	]
	return columns

def get_conditions(filters):
	conditions =""

	if filters.get("date"):
		conditions += "DATE(so.creation) = '{0}'".format(filters.date)	

	if filters.procurement_member:
		conditions += " and tso.custom_procurement_member = '{0}'".format(filters.procurement_member)

	if filters.customer_name:
		conditions += " and so.customer = '{0}'".format(filters.customer_name)

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""SELECT 
		so.name as so,
		so.customer	as customer_name,
		so.transaction_date as date,
		so.contact_person as contact_person,
		so.custom_grade as grade,
		so.custom_industry_vertical as industry_vertical,
		so.po_no as po_no,
		tso.custom_procurement_member as procurement_member,
		SUM(tso.amount) as grand_total,
		so.currency as currency
		From `tabSales Order` as so
		inner join `tabSales Order Item` as tso
		on
			tso.parent = so.name
		where {0} and so.docstatus = 1
			group by tso.custom_procurement_member
		""".format(conditions),filters, as_dict=1, debug=1
	)

	return data
