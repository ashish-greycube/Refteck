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
			"fieldname": "no_of_so",
			"fieldtype": "Data",
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
			"label": _("Existing"), 
			"width": 100
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

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		""" SELECT
		COUNT(DISTINCT so.name) as no_of_so,
		tso.custom_procurement_member as procurement_member,
		CONCAT('$ ',ROUND(SUM(tso.amount * coalesce(fn.exchange_rate, 1)),2)) as total_value_in_usd,
		GROUP_CONCAT(DISTINCT so.name SEPARATOR ',') as unique_so
		From `tabSales Order` as so
		inner join `tabSales Order Item` as tso
		on tso.parent = so.name
		inner join `tabCustomer` as cs
		on cs.name = so.customer
		left outer join `tabCustom Currency Exchange` fn on fn.from_currency = so.currency
    	and fn.to_currency = 'USD'
    	and fn.`date` = (
			    				select `date` 
	    						from `tabCustom Currency Exchange` x
	    						where x.from_currency = so.currency and x.to_currency = 'USD' 
		    						and x.`date` <= so.transaction_date 
									ORDER BY x.date DESC 
		    						LIMIT 1)
		where {0} and so.docstatus != 2 and cs.custom_is_refteck_customer = 0
			GROUP BY tso.custom_procurement_member
			ORDER BY ROUND(SUM(tso.amount * coalesce(fn.exchange_rate, 1)),2) DESC
			""".format(conditions),filters, as_dict=1, debug=1
	)

	# ------old logic------

	# grade_new_count = frappe.db.sql(
	# 	""" SELECT 
	# 	tso.custom_procurement_member as procurement_member,
	# 	COUNT(DISTINCT(so.name)) as new 
	# 	From `tabSales Order` as so
	# 	inner join `tabSales Order Item` as tso
	# 	on tso.parent = so.name
	# 	inner join `tabCustomer` as cs
	# 	on cs.name = so.customer
	# 	where {0} and so.docstatus != 2 and tso.custom_grade = 'NEW' and cs.custom_is_refteck_customer = 0
	# 		GROUP BY tso.custom_procurement_member
	# 	""".format(conditions),filters, as_dict=1, debug=1
	# 	)
	
	# grade_old_count = frappe.db.sql(
	# 	""" SELECT 
	# 	tso.custom_procurement_member as procurement_member,
	# 	COUNT(DISTINCT(so.name)) as old 
	# 	From `tabSales Order` as so
	# 	inner join `tabSales Order Item` as tso
	# 	on tso.parent = so.name
	# 	inner join `tabCustomer` as cs
	# 	on cs.name = so.customer
	# 	where {0} and so.docstatus != 2 and tso.custom_grade = 'Existing' and cs.custom_is_refteck_customer = 0	
	# 		GROUP BY tso.custom_procurement_member
	# 	""".format(conditions),filters, as_dict=1, debug=1)
	
	total_so = 0
	usd_total = 0
	new_total = 0
	old_total = 0
	for d in data:
		# print(d.no_of_so, "=======d.no_of_so---------")
		total_so = (total_so + d.no_of_so)
		usd_total =  flt(usd_total + flt((d.total_value_in_usd[1:])  or 0),2)

		distinct_so = d.unique_so.split(",")
		if len(distinct_so) > 0:

			for so in distinct_so:
				new_brand_count = get_unique_brand_count_based_on_conditions(so, d.procurement_member, "NEW")
				old_brand_count = get_unique_brand_count_based_on_conditions(so, d.procurement_member, "Existing")

				if new_brand_count > 0:
					d.new = (d.new or 0) + new_brand_count
				if old_brand_count > 0:
					d.old = (d.old or 0) + old_brand_count
					
				new_total = (new_total + new_brand_count)
				old_total = (old_total + old_brand_count)


		# print(distinct_so, "=======distinct_so---------", type(distinct_so))


		
		# for new in grade_new_count:
		# 	if d.procurement_member == new.procurement_member:
		# 		d.new = new.new
		# 		new_total = (new_total + (d.new or 0))
		# for old in grade_old_count:
		# 	if d.procurement_member == old.procurement_member:
		# 		d.old = old.old
		# 		old_total = (old_total + (d.old or 0))
	# print(total_so, "-----total_so")

	data.append({
		"no_of_so": "<b>" + cstr(total_so) + "</b>",
		"total_value_in_usd": "<b>" + "$ " + cstr(usd_total) + "</b>",
		"new": "<b>" + cstr(new_total) + "</b>",
		"old": "<b>" + cstr(old_total) + "</b>",
	})

	# print(data, "----data---")

	return data


def get_unique_brand_count_based_on_conditions(so, procurement_member, grade_type):
	brand_count_details = frappe.db.sql("""
							SELECT COUNT(DISTINCT(tso.brand)) as brand_count,
							GROUP_CONCAT(DISTINCT tso.brand SEPARATOR ',') as unique_brand
							From `tabSales Order` as so
								inner join `tabSales Order Item` as tso
								on tso.parent = so.name
								WHERE 
									so.name = "{0}" AND 
									tso.custom_procurement_member = "{1}" AND
									tso.custom_grade = "{2}"
							GROUP BY so.name """.format(so, procurement_member, grade_type), as_dict=1, debug=1)
	
	if len(brand_count_details) > 0:
		return brand_count_details[0].brand_count
	
	return 0