# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cstr

def execute(filters=None):
	if not filters : filters = {}
	columns, data = [], []
	
	columns = get_columns()
	data = get_data(filters)
	
	if not data :
		frappe.msgprint('No Records Found')
		return columns, data

	return columns, data


def get_columns():
	columns = [
		{
			"fieldname" :"name",
			"fieldtype" :"Link",
			"label" :_("ID"),
			"options" : "Quotation",
			"width" :210
		},
		{
			"fieldname" :"docstatus",
			"fieldtype" :"docstatus",
			"label" :_("Docstatus"),
			"width" :100
		},
		{
			"fieldname" :"company",
			"fieldtype" :"Link",
			"label" :_("Company"),
			"options":"Company",
			"width" :240
		},
		{
			"fieldname" :"customer",
			"fieldtype" :"Link",
			"label" :_("Customer"),
			"options":"Customer",
			"width" :240
		},
		{
			"fieldname" :"customer_name",
			"fieldtype" :"Data",
			"label" :_("Customer Name"),
			"width" :250
		},
		{
			"fieldname" :"customer_ref",
			"fieldtype" :"Data",
			"label" :_("Customer Opportunity Reference"),
			"width" :120
		},
		{
			"fieldname" :"refteck_ref",
			"fieldtype" :"Data",
			"label" :_("Refteck Opportunity Reference"),
			"width" :120
		},
		{
			"fieldname" :"grand_total",
			"fieldtype" :"Data",
			"label" :_("Grand Total"),
			"width" :120
		},
  		{
			"fieldname" :"currency",
			"fieldtype" :"Link",
			"label" :_("Currency"),
			"options":"Currency",
			"width" :100
		},
		{
			"fieldname" :"base_grand_total",
			"fieldtype" :"Data",
			"label" :"Grand Total (Company Currency)",
			"width" :150
		},
		{
			"fieldname" :"value_in_usd",
			"fieldtype" :"Data",
			"label" :_("Total Value in USD"),
			"width" :130
		},
		{
			"fieldname" :"supplier_payment_terms",
			"fieldtype" :"Link",
			"label" :_("Supplier Payment Terms"),
			"options":"Payment Term",
			"width" :200
		},
		{
			"fieldname" :"amended_from",
			"fieldtype" :"Link",
			"label" :_("Amended From"),
			"options":"Quotation",
			"width" :220
		},
		{
			"fieldname" :"valid_till",
			"fieldtype" :"Date",
			"label" :_("Valid Till"),
			"width" :120
		},
		{
			"fieldname" :"owner",
			"fieldtype" :"Link",
			"label" :_("owner"),
			"options": "User",
			"width" :230
		},
	]
	return columns


def get_data(filters):
	conditions = get_conditions(filters)
	data = frappe.db.sql("""
		SELECT 
			qo.name as name,
			qo.docstatus as docstatus,
			qo.company as company,
			qo.party_name as customer,
			qo.customer_name as customer_name,
			qo.custom_customer_opportunity_reference as customer_ref,
			qo.custom_refteck_opportunity_reference as refteck_ref,
			qo.grand_total as grand_total,
			qo.currency as currency,
			qo.base_grand_total as base_grand_total,
			ROUND((qo.base_grand_total * coalesce(fn.exchange_rate, 1)),2) as value_in_usd,
			qo.custom_supplier_payment_terms as supplier_payment_terms,
			qo.amended_from as amended_from,
			qo.valid_till as valid_till,
			qo.owner as owner,
			qo.transaction_date as tr_date
		FROM `tabQuotation` AS qo 
		LEFT OUTER JOIN `tabCustom Currency Exchange` fn 
					ON fn.from_currency = qo.currency
						and fn.to_currency = 'USD'
						and fn.`date` = (
										select `date` 
										from `tabCustom Currency Exchange` x
										where x.from_currency = qo.currency AND x.to_currency = 'USD' 
											and x.`date` <= qo.transaction_date 
											ORDER BY x.date DESC 
											LIMIT 1)
		WHERE qo.grand_total != 0 
			AND qo.status Not IN ("Draft", "Cancelled") {0}
		""".format(conditions),as_dict=1,debug=1)
	
	grand_total = 0
	base_grand_total = 0
	total = 0
	for row in data:
		symbol = frappe.db.get_value("Currency",row["currency"],"symbol")
		grand_total += flt((row["grand_total"]),2)
		base_grand_total += flt((row["base_grand_total"]),2)
		total += flt((row["value_in_usd"]),2)

		row["grand_total"] = cstr(symbol) + " " + cstr(row["grand_total"])
		row["base_grand_total"] = cstr(symbol) + " " + cstr(row["base_grand_total"])
		row["value_in_usd"] = "$ " + cstr(row["value_in_usd"])
		
	data.append({"name":"Total", "grand_total": flt(grand_total, 2), "base_grand_total": flt(base_grand_total, 2),"value_in_usd":"$ " + cstr(flt(total,2)) })
	
	return data

def get_conditions(filters):
	conditions = ""

	if filters.get("name"):
		conditions += " AND qo.name = '{0}'".format(filters["name"])

	if filters.get("customer"):
		conditions += " AND qo.party_name ='{0}'".format(filters["customer"])
		
	if filters.get("date"):
		conditions += " AND qo.transaction_date ='{0}'".format(filters["date"])
	
	if filters.get("order_type"):
		conditions += " AND qo.order_type ='{0}'".format(filters["order_type"])
		
	return conditions