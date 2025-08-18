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
			"fieldname": "qo",
			"fieldtype": "Link",
			"label": _("ID"),
			"options": "Quotation",
			"width": 200
		},
		{
			"fieldname": "customer_name",
			"fieldtype": "Link",
			"label": _("Client"),
			"options": "Customer",
			"width": 170
		},
		{
			"fieldname": "transaction_date",
			"fieldtype": "Date",
			"label": _("Date"),
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
			"fieldname": "unified_usd",
			"fieldtype": "Data",
			"label": _("Unified USD"), 
			"width": 150
		},
		{
			"fieldname": "brands",
			"fieldtype": "Data",
			"label": _("Brand"),
			"width": 300
		},
		{
			"fieldname": "procurement_member",
			"label":_("User(Procurement Member)"),
			"fieldtype": "Link",
			"options": "User",
			"width": 170
		},
		{
			"fieldname": "other_charges",
			"fieldtype": "Data",
			"label": _("Charges(Brand wise Charges)"), 
			"width": 150
		},
	]
	return columns


def get_conditions(filters):
	conditions =""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "DATE(qo.transaction_date) between {0} and {1}".format(
        		frappe.db.escape(filters.get("from_date")),
        		frappe.db.escape(filters.get("to_date")))		
		else:
			frappe.throw(_("To Date should be greater then From Date"))	

	if filters.procurement_member:
		conditions += " and tqi.custom_procurement_member = '{0}'".format(filters.procurement_member)

	if filters.customer_name:
		conditions += " and qo.party_name = '{0}'".format(filters.customer_name)

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""SELECT 
			qo.name AS qo, 
			qo.party_name AS customer_name, 
			qo.transaction_date AS transaction_date,
			IF(qo.currency = 'GBP', CONCAT('£ ',ROUND(sum(tqi.net_amount),2)), '-') AS gbp,
			IF(qo.currency = 'EUR', CONCAT('€ ',ROUND(sum(tqi.net_amount),2)), '-') AS euro,
			IF(qo.currency = 'USD', CONCAT('$ ',ROUND(sum(tqi.net_amount),2)), '-') AS usd,
			IF(qo.currency = 'INR', CONCAT('₹ ',ROUND(sum(tqi.net_amount),2)), '-') AS inr,
			IF(qo.currency NOT IN ('GBP', 'EUR', 'USD', 'INR'), ROUND(sum(tqi.net_amount),2), '-') AS others,
			CONCAT('$ ',ROUND(SUM(tqi.net_amount * coalesce(fn.exchange_rate, 1)),2)) AS unified_usd,
			GROUP_CONCAT(DISTINCT tqi.brand SEPARATOR ',') AS brands,
			tqi.custom_procurement_member AS procurement_member
			FROM `tabQuotation` AS qo
			INNER JOIN `tabQuotation Item` AS tqi ON tqi.parent = qo.name
			LEFT OUTER JOIN `tabCustom Currency Exchange` fn ON fn.from_currency = qo.currency
					and fn.to_currency = 'USD'
					and fn.`date` = (
									select `date` 
									from `tabCustom Currency Exchange` x
									where x.from_currency = qo.currency AND x.to_currency = 'USD' 
										and x.`date` <= qo.transaction_date 
										ORDER BY x.date DESC 
										LIMIT 1)
			WHERE {0} AND qo.docstatus != 2
			GROUP BY tqi.custom_procurement_member, qo.name 
			ORDER BY qo.transaction_date DESC, qo.name""".format(conditions),filters, as_dict=1)
	
	if len(data) > 0:
		gbp_total = 0
		euro_total = 0
		usd_total = 0
		inr_total = 0
		other_total = 0
		unified_usd_total = 0
		col_total_other_charges = 0

		for row in data:
			gbp_total =  flt((gbp_total + (flt((row.gbp[1:]), 2) or 0)), 2)
			usd_total =  flt((usd_total + (flt((row.usd[1:]), 2) or 0)), 2)
			euro_total =  flt((euro_total + (flt((row.euro[1:]), 2) or 0)),2)
			inr_total =  flt((inr_total + (flt((row.inr[1:]), 2) or 0)), 2)
			other_total =  flt((other_total + (flt((row.others), 2) or 0)), 2)
			unified_usd_total = flt((unified_usd_total + (flt((row.unified_usd[1:]), 2) or 0)), 2)

			if row.brands:
				brands_list = row.brands.split(',')
				total_other_charger = 0
				if len(brands_list) > 0:
					for b in brands_list:
						other_charges = frappe.db.sql(
							"""SELECT 
								SUM(occ.offer_charges) AS offer_charges 
								FROM `tabOther Charges Comparison` AS occ
								WHERE occ.parent = "{0}" AND occ.brand = "{1}"
								GROUP BY occ.brand
								""".format(row.qo, b), as_dict=1
						)

						# print(other_charges,"=============other_charges====")

						if len(other_charges) > 0:
							total_other_charger = total_other_charger + other_charges[0].offer_charges
							col_total_other_charges = col_total_other_charges + other_charges[0].offer_charges
					# print(total_other_charger, "=================total_other_charger==========")
					
					row.update({"other_charges": total_other_charger})
			# print(row.brands, type(row.brands), "----------------------------------")

		data.append({"customer_name":"Total", 
			  "gbp": "<b>" + "£ " + cstr(gbp_total) + "</b>",
			  "euro": "<b>" + "€ " + cstr(euro_total) + "</b>",
			  "usd": "<b>" + "$ " + cstr(usd_total) + "</b>",
			  "inr": "<b>" + "₹ " + cstr(inr_total) + "</b>",
			  "others": "<b>" + cstr(other_total) + "</b>",
			  "unified_usd": "<b>" + "$ " + cstr(unified_usd_total) + "</b>",
			  "other_charges": "<b>" + cstr(col_total_other_charges) + "</b>"})
		
	return data