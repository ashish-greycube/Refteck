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
			"fieldname": "opportunity",
			"fieldtype": "Link",
			"label": _("Opportunity"),
			"options": "Opportunity",
			"hidden":1,
			"width": 200
		},
		{
			"fieldname": "customer_opportunity_reference",
			"fieldtype": "Data",
			"label": _("Customer Opportunity Reference"),
			"width": 200
		},
		{
			"fieldname": "customer_name",
			"fieldtype": "Link",
			"label": _("Customer Name"),
			"options": "Customer",
			"width": 300
		},
		{
			"fieldname": "oem",
			"fieldtype": "Data",
			"label": _("OEM"),
			"width": 450
		},
	]
	return columns

def get_data(filters):
	data = []
	
	data = frappe.db.sql(
		"""SELECT 
		op.name as opportunity, 
		op.custom_customer_opportunity_reference as customer_opportunity_reference,
		op.party_name as customer_name, 
		GROUP_CONCAT(DISTINCT oi.brand) as oem 
		FROM `tabOpportunity` as op 
		INNER JOIN `tabOpportunity Item` as oi ON op.name = oi.parent
		INNER JOIN `tabSupplier Quotation` as sq ON sq.opportunity = op.name
		WHERE NOT EXISTS (
    		SELECT 1 FROM `tabQuotation` AS qo WHERE qo.opportunity = op.name
		) AND sq.docstatus = 1
		GROUP BY op.name
		ORDER BY op.creation DESC
		""", as_dict=1, debug=1)

	return data
