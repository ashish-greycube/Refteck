# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from datetime import datetime

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
			"fieldname": "name",
			"label": _("Name"),
			"fieldtype": "Link",
			"options": "User",
			"width": 170
		},
		{
			"fieldname": "rfq_no",
			"fieldtype": "Data",
			"label": _("RFQ No."),
			"width": 130
		},
		{
			"fieldname": "buyer",
			"label": _("Buyer"),
			"fieldtype": "Link",
			"options": "Contact",
			"width": 150
		},
		{
			"fieldname": "recpt_dt",
			"fieldtype": "Date",
			"label": _("Recpt DT"),
			"width": 110
		},
		{
			"fieldname": "due_date",
			"fieldtype": "Date",
			"label": _("Due Date"),
			"width": 110
		},
		{
			"fieldname": "refteck_ref_no",
			"fieldtype": "Data",
			"label": _("Refteck Ref No"),
			"width": 120
		},
		{
			"fieldname": "erp_ref_no", 
			"label": _("Erp Ref No"),
			"fieldtype": "Link",
			"options": "Opportunity",
			"width": 190
		},
		{
			"fieldname": "client_name",
			"label": _("Client Name"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "oems",
			"fieldtype": "Data",
			"label": _("OEM'S"),
			"width": 150
		},
		{
			"fieldname": "comments",
			"fieldtype": "Small Text",
			"label": _("Comments"),
			"width": 200,
		}
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.from_date:
		conditions += "  date(creation) >= %(from_date)s"
	if filters.to_date:
		conditions += " and date(creation) <= %(to_date)s"
	print('conditions----',conditions)
	return conditions
	# conditions = {}

	# if filters.get("from_date") and filters.get("to_date"):
	# 	# print(filters)
	# 	from_date=filters.get("from_date")+' 00:00:00.000000'
	# 	to_date=filters.get("to_date")+' 00:00:00.000000'
	# 	print(from_date, "----from_date", to_date, "----to_date")
	# 	# conditions["creation"] = ("between", [from_date, to_date])
	# 	conditions["creation"] <= from_date
	# 	conditions["creation"] >= to_date 	 

	# 	# return date
	# print(conditions, '-----conditions')
	# return conditions

def get_data(filters):
	 
	data = []
	conditions = get_conditions(filters)
	print('conditions',conditions,filters)
	opportunity_list = frappe.db.get_list(
			"Opportunity", fields=["custom_customer_opportunity_reference",
						"contact_person", 
						"creation",
						"expected_closing", 
						"custom_refteck_opportunity_reference",
						"name", 
						"party_name"],
						limit=5
						
	)
	  
	for op in opportunity_list:

		# print(op.creation,"------date")

		items = frappe.db.get_list(
			"Opportunity Item", fields=["qty","custom_sourcing_person", "parent","custom_refteck_item_comment", "doctype", "brand"], 
			filters={"parent":op.name},
		) 

		
		unique_sourcing_persons = []
		
		for item in items:
			if item.custom_sourcing_person not in unique_sourcing_persons:
				unique_sourcing_persons.append(item.custom_sourcing_person)	
		
		# dulicate_items = item

		# print(dulicate_items.parent, "----parent")	
		
		for sourcing_person in unique_sourcing_persons:
			unique_brands = []
			comments = []
			for values in items:
				if sourcing_person == values.custom_sourcing_person and values.brand not in unique_brands:
					unique_brands.append(values.brand)

				if sourcing_person == values.custom_sourcing_person and values.custom_refteck_item_comment:
					comments.append(values.custom_refteck_item_comment)
			
			brands = ", ".join(ele for ele in unique_brands)
			comments = ", ".join(ele for ele in comments)

			row = {
					"name": sourcing_person,
					"rfq_no": op.custom_customer_opportunity_reference,
					"buyer": op.contact_person,
					"recpt_dt": op.creation,
					"due_date": op.expected_closing,
					"refteck_ref_no": op.custom_refteck_opportunity_reference,
					"erp_ref_no": op.name,
					"client_name": op.party_name,
					"oems": brands,
					"comments": comments
			}
			data.append(row)
		
	return data