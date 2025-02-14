# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cstr

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
			"width": 170
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
			"width": 200
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
			"width": 180
		},
		{
			"fieldname": "po_no",
			"fieldtype": "Data",
			"label": _("Customer's Purchase Order"),
			"width": 150
		},
		{
			"fieldname": "procurement_member",
			"label":_("User(Procurement Member)"),
			"fieldtype": "Link",
			"options": "User",
			"width": 170
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
			"fieldname": "currency",
			"label":_("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
		},
		{
			"fieldname": "owner",
			"fieldtype": "Data",
			"label": _("Owner"),
			"width": 130
		},
	]
	return columns

def get_conditions(filters):
	conditions =""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "DATE(so.transaction_date) between {0} and {1}".format(
        		frappe.db.escape(filters.get("from_date")),
        		frappe.db.escape(filters.get("to_date")))		
		else:
			frappe.throw(_("To Date should be greater then From Date"))	

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
		IF(so.currency = 'GBP',
			CONCAT('£ ',ROUND(sum(tso.amount),2)),
			'-') as gbp,
			IF(so.currency = 'EUR',
			CONCAT('€ ',ROUND(sum(tso.amount),2)),
			'-') as euro,
			IF(so.currency = 'USD',
			CONCAT('$ ',ROUND(sum(tso.amount),2)),
			'-') as usd,
			IF(so.currency = 'INR',
			CONCAT('₹ ',ROUND(sum(tso.amount),2)),
			'-') as inr,
			IF(so.currency NOT IN ('GBP', 'EUR', 'USD', 'INR'), ROUND(sum(tso.amount),2), '-') as others,
		so.currency as currency,
		so.owner as owner
		From `tabSales Order` as so
		inner join `tabSales Order Item` as tso
		on
			tso.parent = so.name
		inner join `tabCustomer` as cs
		on 
			cs.name = so.customer 
		where {0} and so.docstatus != 2 and cs.custom_is_refteck_customer = 0
			group by tso.custom_procurement_member, so.name
		""".format(conditions),filters, as_dict=1, debug=1
	)

	gbp_total = 0
	euro_total = 0
	usd_total = 0
	inr_total = 0
	other_total = 0
	for row in data:
		gbp_total =  flt((gbp_total + (flt((row.gbp[1:]), 2) or 0)), 2)
		usd_total =  flt((usd_total + (flt((row.usd[1:]), 2) or 0)), 2)
		euro_total =  flt((euro_total + (flt((row.euro[1:]), 2) or 0)),2)
		inr_total =  flt((inr_total + (flt((row.inr[1:]), 2) or 0)), 2)
		other_total =  flt((other_total + (flt((row.others), 2) or 0)), 2)


	data.append({"po_no":"<b>Total</b>", 
			  "gbp": "<b>" + "£ " + cstr(gbp_total) + "</b>",
			  "euro": "<b>" + "€ " + cstr(euro_total) + "</b>",
			  "usd": "<b>" + "$ " + cstr(usd_total) + "</b>",
			  "inr": "<b>" + "₹ " + cstr(inr_total) + "</b>",
			  "others": "<b>" + cstr(other_total) + "</b>"})

	return data
