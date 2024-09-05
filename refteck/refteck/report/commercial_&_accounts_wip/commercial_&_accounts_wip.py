# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt


import frappe
from frappe import msgprint, _
from datetime import datetime
from frappe.utils import fmt_money, get_datetime

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
			"fieldname": "so",
			"fieldtype": "Link",
			"label": _("SO"),
			"options": "Sales Order",
			# "hidden":1,
			"width": 200
		},
		{
			"fieldname": "month",
			"fieldtype": "Data",
			"label": _("MONTH"),
			"width": 100
		},
		{
			"fieldname": "po_received_date",
			"fieldtype": "Date",
			"label": _("PO Received (dd.mm.yyyy)"),
			"width": 110
		},
		{
			"fieldname": "purchase_order_no",
			"fieldtype": "Data",
			"label": _("Purchase Order No."),
			"width": 150
		},
		{
			"fieldname": "client_delivery_date",
			"fieldtype": "Date",
			"label": _("Client Delivery Date"),
			"width": 110
		},
		{
			"fieldname": "client",
			"fieldtype": "Link",
			"label": _("Client"),
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "supplier_po_issue_date",
			"fieldtype": "Date",
			"label": _("Supplier PO Issue Date"),
			"width": 110
		},
		{
			"fieldname": "supplier",
			"fieldtype": "Link", 
			"label": _("Supplier"),
			"options": "Supplier",
			"width": 150
		},
		{
			"fieldname": "po_acknowledgement_status",
			"fieldtype": "Data",
			"label": _("PO Acknowledgement Status"),
			"width": 150
		},
		{
			"fieldname": "date_invoice_received",
			"fieldtype": "Date",
			"label": _("Date Invoice Received"),
			"width": 110
		},
		{
			"fieldname": "usd",
			"fieldtype": "Data",
			"label": _("USD"), 
			"width": 100
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
			"fieldname": "supplier_invoice_number", 
			"fieldtype": "Data",
			"label": _("Supplier Invoice number"),
			"width": 150
		},
		{
			"fieldname": "supplier_invoice_date", 
			"fieldtype": "Date",
			"label": _("Supplier Invoice Date"),
			"width": 110
		},
		{
			"fieldname": "invoice_amount", 
			"fieldtype": "Data",
			"label": _("Invoice Amount"),
			"width": 110
		},
		{
			"fieldname": "ld_applicable",  
			"fieldtype": "Data",
			"label": _("LD Applicable"), 
			"width": 110
		},
		{
			"fieldname": "bank_details",  
			"fieldtype": "Data",
			"label": _("Bank Details"),  
			"width": 110
		},
		{
			"fieldname": "accounts_wip_status", 
			"fieldtype": "Data",
			"label": _("Accounts WIP status"),
			"width": 170
		},
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": _("Company"),
			"options": "Company",
			"width": 230,
		},
		{
			"fieldname": "updated_payment_terms",
			"fieldtype": "Data",
			"label": _("Updated Payment Terms"), 
			"width": 130
		},
		{
			"fieldname": "supplier_delivery_date",
			"fieldtype": "Date",
			"label": _("Supplier delivery date (dd.mm.yyyy)"),
			"width": 110
		},
		{
			"fieldname": "lead_time",
			"fieldtype": "Data",
			"label": _("Current Lead Time / Ship Date"),
			"width": 110
		},
		{
			"fieldname": "commercial_delegation",
			"fieldtype": "Data",
			"label": _("Commercial Delegation"),
			"width": 150
		},
		{
			"fieldname": "invoice_due_date",
			"fieldtype": "Date",
			"label": _("Invoice Due Date"),
			"width": 110
		},
		{
			"fieldname": "payment_status",
			"fieldtype": "Data",
			"label": _("Payment Status"),
			"width": 130
		},
		{
			"fieldname": "finance_remarks", 
			"fieldtype": "Data",
			"label": _("Finance Remarks"),
			"width": 130
		},
		]
	return columns

def get_conditions(filters):
	conditions = []
	conditions.append({"docstatus":1})
	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions.append(["creation","between", [filters.get("from_date"), filters.get("to_date")]])
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	
	if filters.client:
		conditions.append({"customer_name":filters.client})

	if filters.company:
		conditions.append({"company":filters.company})

	return conditions

def get_data(filters):

	data = []
	conditions = get_conditions(filters)
	
	so_list = frappe.db.get_list(
			"Sales Order", fields=["name",
						"transaction_date", 
						"po_no",
						"delivery_date", 
						"customer_name",
						"rounded_total",
						"advance_paid",
						"custom_ld_applicable",
						"company"
						],
						filters=conditions,)

	for so in so_list:
		transaction_month = so.transaction_date	

		# purchase order	
			
		po_items = frappe.db.get_list(
			"Purchase Order Item", 
			parent_doctype='Purchase Order',fields=["parent"],filters={"sales_order": so.name})

		unique_po = []
		for item in po_items:
			if item.parent not in unique_po:
				unique_po.append(item.parent)	
		
		if (len(po_items) > 0):
			for po_name in unique_po:
				po_list = frappe.db.get_list(
				"Purchase Order", fields=["name",
							"modified",
							"supplier", 
							"custom_po_acknowledgement_status",
							"custom_date_invoice_received", 
							"currency",
							"net_total",
							"custom_updated_payment_terms",
							"schedule_date",
							"custom_current_lead_time_ship_date",
							"custom_commercial_delegation_status",
							"custom_bank_details",
							"status",
							"custom_finance_remarks",
							"advance_paid",
							"rounded_total"
							],
							filters={"name":po_name,"docstatus":1})
				# print(po_list[0].name, '--------po_name')
				
				usd = ""
				gbp = ""
				euro = ""
				inr = ""
				others = "" 

				for po in po_list:

					if po.currency == "USD":
						usd = fmt_money(po.net_total, currency=po.currency)
					else: usd = " - "
					
					if po.currency == "GBP":
						gbp = fmt_money(po.net_total, currency=po.currency)
					else: gbp = " - "
					
					if po.currency == "EUR":
						euro = fmt_money(po.net_total, currency=po.currency)
					else: euro = " - "

					if po.currency == "INR":
						inr = fmt_money(po.net_total, currency=po.currency)
					else: inr = " - "

					if po.currency != "USD" and  po.currency != "GBP" and po.currency != "EUR" and po.currency != "INR":
						others = fmt_money(po.net_total, currency=po.currency)
					else: others = " - "

					# purchase invoice

					pi_items = frappe.db.get_list(
						"Purchase Invoice Item", 
						parent_doctype='Purchase Invoice',fields=["parent"],filters={"purchase_order": po.name})
					
					payment_status = ""
					invoice_due_date = ""
					supplier_invoice_number = ""
					supplier_invoice_date = ""
					supplier_invoice_amount = ""
					if (len(pi_items) > 0):
							
						pi_list = frappe.db.get_list(
						"Purchase Invoice", fields=["name","bill_no","bill_date", "currency","docstatus", "total_advance", "rounded_total", "due_date"],
									filters={"name":pi_items[0].parent})
						# print(pi_list[0].name, '---------pi_list')

						invoice_due_date = pi_list[0].due_date or ''
						supplier_invoice_number = pi_list[0].bill_no or ''
						supplier_invoice_amount =  fmt_money( pi_list[0].rounded_total, currency=pi_list[0].currency)
						supplier_invoice_date = pi_list[0].bill_date or ''
	
					if(len(pi_items) > 0 and pi_list[0].docstatus == 1):
						if pi_list[0].total_advance == 0:
							payment_status = "Unpaid"
						
						if pi_list[0].rounded_total != pi_list[0].total_advance and pi_list[0].total_advance != 0:
							payment_status = "Partly Paid"
						
						if pi_list[0].rounded_total == pi_list[0].total_advance and pi_list[0].total_advance != 0:
							payment_status = "Paid"
					
					else:
						if po.advance_paid == 0:
							payment_status = "Unpaid"
						
						if po.rounded_total != po.advance_paid and po.advance_paid != 0:
							payment_status = "Partly Paid"
						
						if po.rounded_total == po.advance_paid and po.advance_paid != 0:
							payment_status = "Paid"

					row = {
						"so": so.name,
						"month": transaction_month.strftime('%b'),
						"po_received_date": so.transaction_date,
						"purchase_order_no": so.po_no,
						"client_delivery_date": so.delivery_date,
						"client": so.customer_name,
						"supplier_po_issue_date": po.modified,
						"supplier": po.supplier,
						"po_acknowledgement_status": po.custom_po_acknowledgement_status,
						"date_invoice_received": po.custom_date_invoice_received,
						"supplier_invoice_number": supplier_invoice_number,
						"supplier_invoice_date": supplier_invoice_date,
						"invoice_amount":supplier_invoice_amount,
						"ld_applicable": so.custom_ld_applicable,
						"bank_details": po.custom_bank_details,
						"accounts_wip_status": po.custom_po_acknowledgement_status,
						"company": so.company,
						"usd": usd,
						"gbp": gbp,
						"euro": euro,
						"inr": inr,
						"others": others,
						"updated_payment_terms": po.custom_updated_payment_terms,
						"supplier_delivery_date": po.schedule_date,
						"lead_time": po.custom_current_lead_time_ship_date,
						"commercial_delegation": po.custom_commercial_delegation_status,
						"invoice_due_date": invoice_due_date,
						"payment_status": payment_status,
						"finance_remarks":po.custom_finance_remarks
					}
					data.append(row)

	return data