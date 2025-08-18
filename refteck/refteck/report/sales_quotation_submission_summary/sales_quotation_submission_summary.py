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
			"fieldname": "procurement_member",
			"label":_("User(Procurement Member)"),
			"fieldtype": "Link",
			"options": "User",
		},
		{
			"fieldname": "total_gbp",
			"fieldtype": "Data",
			"label": _("Total GBP"), 
			"width": 120
		},
		{
			"fieldname": "total_euro",
			"fieldtype": "Data",
			"label": _("Total EURO"), 
			"width": 120
		},
		{
			"fieldname": "total_usd",
			"fieldtype": "Data",
			"label": _("Total USD"), 
			"width": 120
		},
		{
			"fieldname": "total_inr",
			"fieldtype": "Data",
			"label": _("Total INR"), 
			"width": 120
		},
		{
			"fieldname": "total_others",
			"fieldtype": "Data",
			"label": _("Total OTHERS"), 
			"width": 120
		},
		{
			"fieldname": "unified_usd",
			"fieldtype": "Data",
			"label": _("Unified USD"), 
			"width": 150
		},
		{
			"fieldname": "total_no_of_qo",
			"fieldtype": "Data",
			"label": _("Total No. Of Sales Quotation"),
			"width": 180
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

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""SELECT 
		tqi.custom_procurement_member AS procurement_member,
		COUNT(DISTINCT qo.name  ) AS total_no_of_qo,
		GROUP_CONCAT(DISTINCT qo.name SEPARATOR ',') AS qo_list
		FROM `tabQuotation` AS qo 
		INNER JOIN `tabQuotation Item` AS tqi ON tqi.parent = qo.name 
		WHERE {0} and qo.docstatus NOT IN (2, 0) and tqi.custom_procurement_member != ""
		GROUP BY tqi.custom_procurement_member
		""".format(conditions),filters, as_dict=1, debug=1
	)

	if len(data) > 0:
		col_total_gbp = 0
		col_total_euro = 0
		col_total_usd = 0
		col_total_inr = 0
		col_total_others = 0
		col_total_usd_unified = 0

		total_qo = 0
		for row in data:
				if row.qo_list:
					qo_list = row.qo_list.split(',')
					total_qo = total_qo + row.total_no_of_qo

					total_gbp = 0
					total_euro = 0
					total_usd = 0
					total_inr = 0
					total_others = 0

					if len(qo_list) > 0:	
						total_usd_unified = 0

						for qo in qo_list:
							amount_deatils = frappe.db.sql(
												"""SELECT 
													qo.currency as currency,
													sum(tqi.net_amount) as net_total,
													ROUND(SUM(tqi.net_amount * coalesce(fn.exchange_rate, 1)),2) AS unified_usd
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
													WHERE qo.name = "{0}" AND tqi.custom_procurement_member = "{1}"
												""".format(qo, row.procurement_member),filters, as_dict=1, debug=1)
							
							if len(amount_deatils) > 0:
								total_usd_unified = total_usd_unified + flt(((amount_deatils[0].unified_usd or 0)),2)
								col_total_usd_unified = col_total_usd_unified + flt(((amount_deatils[0].unified_usd or 0)),2)

								currency = amount_deatils[0].currency
								total_net_amt = amount_deatils[0].net_total

								if currency == "GBP":
									total_gbp = total_gbp + flt((total_net_amt),2)
									col_total_gbp = col_total_gbp + flt((total_net_amt),2)
								elif currency == "EUR":
									total_euro = total_euro + flt((total_net_amt),2)
									col_total_euro = col_total_euro + flt((total_net_amt),2)
								elif currency == "USD":
									total_usd = total_usd + flt((total_net_amt),2)
									col_total_usd = col_total_usd + flt((total_net_amt),2)
								elif currency == "INR":
									total_inr = total_inr + flt((total_net_amt),2)
									col_total_inr = col_total_inr + flt((total_net_amt),2)
								else:
									total_others = total_others + flt((total_net_amt),2)
									col_total_others = col_total_others + flt((total_net_amt),2)

						row.update({
							"total_gbp":  "£ " + cstr(flt((total_gbp),2)) if total_gbp > 0 else "-", 
							"total_euro": "€ " + cstr(flt((total_euro),2)) if total_euro > 0 else "-", 
							"total_usd": "$ " + cstr(flt((total_usd),2)) if total_usd > 0 else "-", 
							"total_inr" : "₹ " + cstr(flt((total_inr),2)) if total_inr > 0 else "-", 
							"total_others": flt((total_others),2) if total_others > 0 else "-", 
							"unified_usd": "$ " + cstr(flt((total_usd_unified),2))})

		data.append({"procurement_member":"Total", 
			  "total_gbp": "<b>" + "£ " + cstr(flt((col_total_gbp),2)) + "</b>",
			  "total_euro": "<b>" + "€ " + cstr(flt((col_total_euro),2)) + "</b>",
			  "total_usd": "<b>" + "$ " + cstr(flt((col_total_usd),2)) + "</b>",
			  "total_inr": "<b>" + "₹ " + cstr(flt((col_total_inr),2)) + "</b>",
			  "total_others": "<b>" + cstr(flt((col_total_others),2)) + "</b>",
			  "unified_usd": "<b>" + "$ "  + cstr(flt((col_total_usd_unified),2)) + "</b>",
			  "total_no_of_qo":  "<b>" + cstr(total_qo) + "</b>",})

	return data