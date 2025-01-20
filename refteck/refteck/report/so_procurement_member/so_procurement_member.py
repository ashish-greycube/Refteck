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
			"fieldname": "no_of_so",
			"fieldtype": "Int",
			"label": _("No Of SO"),
			# "hidden":1,
			"width": 100
		},
		{
			"fieldname": "procurement_member",
			"label":_("User(Procurement Member)"),
			"fieldtype": "Link",
			"options": "User",
		},
		# {
		# 	"fieldname": "grand_total",
		# 	"fieldtype": "Data",
		# 	"label": _("Grand Total"), 
		# 	"width": 100
		# },
		{
			"fieldname": "currency",
			"label":_("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
		},
		{
			"fieldname": "exchange_currency",
			"fieldtype": "Data",
			"label": _("Exchange CUrrency"), 
			"width": 100
		},
		{
			"fieldname": "total_value_in_usd",
			"fieldtype": "Data",
			"label": _("Total Value In USD"), 
			"width": 150
		},
		{
			"fieldname": "new",
			"fieldtype": "Data",
			"label": _("New"), 
			"width": 100
		},
		{
			"fieldname": "old",
			"fieldtype": "Data",
			"label": _("Old"), 
			"width": 100
		},
	]
	return columns

def get_conditions(filters):
	conditions =""

	if filters.get("date"):
		conditions += "DATE(so.creation) = '{0}'".format(filters.date)	

	if filters.procurement_member:
		conditions += " and tso.custom_procurement_member = '{0}'".format(filters.procurement_member)

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""SELECT
		COUNT(so.name) as no_of_so,
		tso.custom_procurement_member as procurement_member,
		so.currency as currency,
		fn.exchange_rate as exchange_currency,
		(SUM(tso.amount * fn.exchange_rate)) as total_value_in_usd,
		COUNT(CASE WHEN so.custom_grade = 'NEW' THEN 1 END) as new,
		COUNT(CASE WHEN so.custom_grade = 'OLD'THEN 1 END) as old
		From `tabSales Order` as so
		inner join `tabSales Order Item` as tso
		on tso.parent = so.name
		left outer join `tabCustom Currency Exchange` fn on fn.from_currency = so.currency
    	and fn.to_currency = 'USD'
    	and fn.`date` = (
			    				select `date` 
	    						from `tabCustom Currency Exchange` x
	    						where x.from_currency = so.currency and x.to_currency = 'USD' 
		    						and x.`date` <= so.transaction_date 
									ORDER BY x.date DESC 
		    						LIMIT 1)
		where {0} and so.docstatus = 1
			GROUP BY tso.custom_procurement_member
			""".format(conditions),filters, as_dict=1, debug=1
	)

	return data
