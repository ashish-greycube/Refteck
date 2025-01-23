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
		# 	"fieldname": "currency",
		# 	"label":_("Currency"),
		# 	"fieldtype": "Link",
		# 	"options": "Currency",
		# },
		# {
		# 	"fieldname": "exchange_currency",
		# 	"fieldtype": "Data",
		# 	"label": _("Exchange CUrrency"), 
		# 	"width": 100
		# },
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

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "DATE(so.creation) between {0} and {1}".format(
        		frappe.db.escape(filters.get("from_date")),
        		frappe.db.escape(filters.get("to_date")))		
		else:
			frappe.throw(_("To Date should be greater then From Date"))	

	if filters.procurement_member:
		conditions += " and tso.custom_procurement_member = '{0}'".format(filters.procurement_member)

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		""" SELECT
		COUNT(DISTINCT so.name) as no_of_so,
		tso.custom_procurement_member as procurement_member,
		ROUND(SUM(tso.amount * coalesce(fn.exchange_rate, 1)),2) as total_value_in_usd
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
			ORDER BY total_value_in_usd DESC
			""".format(conditions),filters, as_dict=1
	)

	grade_new_count = frappe.db.sql(
		""" SELECT 
		tso.custom_procurement_member as procurement_member,
		COUNT(DISTINCT(so.name)) as new 
		From `tabSales Order` as so
		inner join `tabSales Order Item` as tso
		on tso.parent = so.name
		where {0} and so.docstatus = 1 and so.custom_grade = 'NEW'	
			GROUP BY tso.custom_procurement_member
		""".format(conditions),filters, as_dict=1
		)
	
	grade_old_count = frappe.db.sql(
		""" SELECT 
		tso.custom_procurement_member as procurement_member,
		COUNT(DISTINCT(so.name)) as old 
		From `tabSales Order` as so
		inner join `tabSales Order Item` as tso
		on tso.parent = so.name
		where {0} and so.docstatus = 1 and so.custom_grade = 'OLD'		
			GROUP BY tso.custom_procurement_member
		""".format(conditions),filters, as_dict=1)
	

	for d in data:
		for new in grade_new_count:
			if d.procurement_member == new.procurement_member:
				d.new = new.new
		for old in grade_old_count:
			if d.procurement_member == old.procurement_member:
				d.old = old.old

	print(data, "----data---")

	return data
