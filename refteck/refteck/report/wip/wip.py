# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from datetime import datetime
from frappe.utils import getdate, date_diff, nowdate
from operator import itemgetter

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
			"fieldtype": "Link",
			"label": _("Name"),
			"options": "User",
			"width": 160
		},
		{
			"fieldname": "rfq_no",
			"fieldtype": "Data",
			"label": _("RFQ No."),
			"width": 110
		},
		{
			"fieldname": "buyer",
			"label": _("Buyer"),
			"fieldtype": "Link",
			"options": "Contact",
			"width": 120
		},
		{
			"fieldname": "recpt_dt",
			"fieldtype": "Date",
			"label": _("Opp DT"),
			"width": 110
		},
		{
			"fieldname": "due_date",
			"fieldtype": "Date",
			"label": _("Due Date"),
			"width": 110
		},
		{
			"fieldname": "revised_due_date",
			"fieldtype": "Date",
			"label": _("Revised Due Date"),
			"width": 110
		},
		{
			"fieldname": "excess_days",
			"fieldtype": "Data",
			"label": _("Excess Days"),
			"width": 110
		},
		{
			"fieldname": "refteck_ref_no",
			"fieldtype": "Data",
			"label": _("Refteck Ref No"),
			"width": 110
		},
		{
			"fieldname": "erp_ref_no", 
			"label": _("Erp Ref No"),
			"fieldtype": "Link",
			"options": "Opportunity",
			"width": 190
		},
		{
			"fieldname": "territory",
			"fieldtype": "Data",
			"label": _("territory"),
			"fieldtype": "Link",
			"options": "Territory",
			"width": 100
		},
		{
			"fieldname": "status",
			"fieldtype": "Data",
			"label": _("Status"),
			"width": 80
		},
		{
			"fieldname": "client_name",
			"label": _("Client Name"),
			"fieldtype": "Data",
			"options": "Customer",
			"width": 180
		},
		{
			"fieldname": "oems",
			"fieldtype": "Data",
			"label": _("OEM'S"),
			"width": 200
		},
		{
			"fieldname": "comments",
			"fieldtype": "Small Text",
			"label": _("Comments"),
			"width": 230,
		}
	]

	return columns

def get_conditions(filters):
	conditions = []

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions.append(["creation","between", [filters.get("from_date"), filters.get("to_date")]])
		else:
			frappe.throw(_("To Date should be greater then From Date"))
		
	if filters.due_date:
		conditions.append({"expected_closing":filters.due_date})

	if filters.territory:
		conditions.append({"territory":filters.territory})

	# if filters.status:
	# 	conditions.append({"status":filters.status})

	if filters.client:
		conditions.append({"party_name":filters.client})

	return conditions

def get_child_conditions(filters, op_parent):
	conditions = []

	conditions.append({"parent": op_parent})

	if filters.sourcing_person:
		conditions.append({"custom_sourcing_person":filters.sourcing_person})

	if filters.status:
		conditions.append({"custom_item_status":filters.status})

	return conditions


def get_data(filters):
	 
	data = []
	conditions = get_conditions(filters)
	
	opportunity_list = frappe.db.get_list(
			"Opportunity", fields=["custom_customer_opportunity_reference",
						  "customer_name",
						"contact_display", 
						"transaction_date",
						"expected_closing", 
						"custom_refteck_opportunity_reference",
						"name",
						"territory",
						"status", 
						"party_name",
						"custom_revised_due_date"],
						filters=conditions,					
	)
	  
	for op in opportunity_list:

		op_parent = op.name 
		days = date_diff(op.custom_revised_due_date, getdate(nowdate()))
		customer_name = frappe.db.get_value('Customer', op.party_name, 'customer_name')
		# print(days, '---days')
		child_conditions = get_child_conditions(filters,op_parent)
		
		items = frappe.db.get_list(
			"Opportunity Item", 
			parent_doctype='Opportunity',
			fields=["custom_sourcing_person", "parent","custom_refteck_item_comment", "brand", "custom_item_status"], 
			filters=child_conditions,
			group_by="custom_sourcing_person, brand",
			order_by="idx"
		) 

		for item in items:
			if item.custom_item_status != "Closed":
			
			# print(item.custom_refteck_item_comment, item.parent, '---custom_refteck_item_comment')

		# get unique sourcing persons
		# unique_sourcing_persons = []
		# for item in items:
		# 	if item.custom_sourcing_person not in unique_sourcing_persons:
		# 		unique_sourcing_persons.append(item.custom_sourcing_person)	
		
		# loop unique sourcing persons list for brand & comments 
		# for sourcing_person in unique_sourcing_persons:

		# 	customer_name = frappe.db.get_value('Customer', op.party_name, 'customer_name')

		# 	unique_brands = []
		# 	comments = []
		# 	for values in items:
		# 		if sourcing_person == values.custom_sourcing_person and values.brand not in unique_brands:
		# 			unique_brands.append(values.brand)

		# 		if sourcing_person == values.custom_sourcing_person and values.custom_refteck_item_comment:
		# 			comments.append(values.custom_refteck_item_comment)
			
		# 	if(len(unique_brands) > 0):
		# 		brands = ", ".join((ele if ele!=None else '') for ele in unique_brands)
			
		# 	if(len(comments) > 0):
		# 		comments = ", ".join((ele if ele!=None else '') for ele in comments)

				row = {
						"name": item.custom_sourcing_person,
						"rfq_no": op.custom_customer_opportunity_reference ,
						"buyer": op.contact_display,
						"recpt_dt": op.transaction_date,
						"due_date": op.expected_closing,
						"revised_due_date": op.custom_revised_due_date,
						"excess_days":days,
						"refteck_ref_no": op.custom_refteck_opportunity_reference,
						"erp_ref_no": op.name,
						"territory":op.territory,
						"status": item.custom_item_status,
						"client_name": customer_name,
						"oems": item.brand,
						"comments": item.custom_refteck_item_comment
				}
				data.append(row)
		sorted_data = sorted(data, key=itemgetter('name'))
	return sorted_data
