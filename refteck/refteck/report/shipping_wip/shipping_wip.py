# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from datetime import datetime
from frappe.utils import fmt_money,add_days, flt, cstr
from frappe.desk.form.assign_to import get


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)
	msg="Shipping WIP report returns data only if there are SO linked with PO and such SO are without SI"
	if not data:
		msgprint(_("No records found"))
		return columns, data, msg, None
		
	return columns, data, msg, None

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
			"fieldname": "po_date",
			"fieldtype": "Date",
			"label": _("PO date"),
			"width": 110
		},
		{
			"fieldname": "client",
			"fieldtype": "Data",
			"label": _("Client"),
			# "options": "Customer",
			"width": 200
		},
		{
			"fieldname": "assigned_to",
			"fieldtype": "Link",
			"label": _("Assigned to"),
			"options": "User",
			"width": 200
		},
		{
			"fieldname": "incoterm",
			"fieldtype": "Link",
			"label": _("Incoterm"),
			"options": "Incoterm",
			"width": 90
		},
		{
			"fieldname": "code",
			"fieldtype": "Data",
			"label": _("Code"),
			"width": 110
		},
		{
			"fieldname": "po_no",
			"fieldtype": "Data",
			"label": _("PO No."),
			"width": 140
		},
		{
			"fieldname": "buyer",
			"fieldtype": "Data", 
			"label": _("Buyer"),
			"options": "Contact",
			"width": 220
		},
		{
			"fieldname": "supplier",
			"fieldtype": "Link", 
			"label": _("Supplier"),
			"options": "Supplier",
			"width": 200
		},
		{
			"fieldname": "delivery_date",
			"fieldtype": "Date",
			"label": _("Delivery Date"),
			"width": 110
		},
		{
			"fieldname": "company",
			"fieldtype": "Link", 
			"label": _("UK/US"),
			"options": "Company",
			"width": 240
		},
		{
			"fieldname": "payment_terms_template",
			"fieldtype": "Link",
			"label": _("Payment Terms Template"),
			"options": "Payment Terms Template",
			"width": 180
		},
		{
			"fieldname": "updated_payment_terms",
			"fieldtype": "Data",
			"label": _("Updated Payment Terms"),
			"width": 180
		},
		{
			"fieldname": "current_lead_time_ship_date",
			"fieldtype": "Data",
			"label": _("Lead time"),
			"width": 110
		},
		{
			"fieldname": "gbp",
			"fieldtype": "Data",
			"label": _("GBP"), 
			"width": 150
		},
		{
			"fieldname": "euro",
			"fieldtype": "Data",
			"label": _("EURO"), 
			"width": 150
		},
		{
			"fieldname": "usd",
			"fieldtype": "Data",
			"label": _("USD"), 
			"width": 150
		},
		{
			"fieldname": "inr",
			"fieldtype": "Data",
			"label": _("INR"), 
			"width": 150
		},
		{
			"fieldname": "others",
			"fieldtype": "Data",
			"label": _("OTHERS"), 
			"width": 150
		},
 		{
            "fieldname": "order_total",
            "fieldtype": "Data",
            "label": _("Order Total"),
            "width": 150
        },	
		{
			"fieldname": "order_total_in_usd",
			"fieldtype": "Data",
			"label": _("Order Total In USD"), 
			"width": 150
		},	
		{
			"fieldname": "payment_status",
			"fieldtype": "Data",
			"label": _("Payment Status"),
			"width": 130
		},
		{
			"fieldname": "comments",
			"fieldtype": "Data",
			"label": _("Comments"),
			"width": 200
		},
		]
	return columns

def get_conditions(filters):
	conditions =""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += " and DATE(tso.creation) between {0} and {1}".format(
        		frappe.db.escape(filters.get("from_date")),
        		frappe.db.escape(filters.get("to_date")))		
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	
	if filters.client:
		conditions += " and tso.customer = '{0}'".format(filters.client)

	if filters.assigned_to:
		conditions += " and todo.allocated_to = '{0}'".format(filters.assigned_to)

	if filters.company:
		conditions += " and tso.company = '{0}'".format(filters.company)

	if filters.get("delivery_from_date") and filters.get("delivery_to_date"):
		if filters.get("delivery_to_date") >= filters.get("delivery_from_date"):
			conditions += " and DATE(tso.delivery_date) between {0} and {1}".format(
        		frappe.db.escape(filters.get("delivery_from_date")),
        		frappe.db.escape(filters.get("delivery_to_date")))		
		else:
			frappe.throw(_("Delivery : To Date should be greater then From Date"))
	
	if filters.order_code:
		conditions += " and tpo.custom_order_code = '{0}'".format(filters.order_code)

	# conditions.append({"per_delivered": ['<', 100], "status": ['!=', "Closed"]})

	return conditions

def get_data(filters):
	data = []
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(
		"""SELECT
			tso.name as so,
			tso.po_date,
			tso.customer_name as client,
			todo.allocated_to as assigned_to,
			tso.incoterm,
			tpo.name as purchase_order,
			tpo.advance_paid,
			tpo.rounded_total,
			tpo.custom_order_code as code,
			tso.po_no,
			tso.contact_display as buyer,
			tpo.supplier,
			tso.delivery_date,
			tso.company,
			tpo.payment_terms_template,
			tpo.custom_updated_payment_terms as updated_payment_terms,
			tpo.custom_current_lead_time_ship_date as current_lead_time_ship_date,
			IF(tso.currency = 'GBP',
			CONCAT('£ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as gbp,
			IF(tso.currency = 'EUR',
			CONCAT('€ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as euro,
			IF(tso.currency = 'USD',
			CONCAT('$ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as usd,
			IF(tso.currency = 'INR',
			CONCAT('₹ ',ROUND(sum(tsoi.net_amount),2)),
			'-') as inr,
			IF(tso.currency NOT IN ('GBP', 'EUR', 'USD', 'INR'), ROUND(sum(tsoi.net_amount),2), '-') as OTHERS,
			tso.grand_total as order_total,
			CONCAT('$ ',ROUND((tso.grand_total * coalesce(fn.exchange_rate, 1)),2)) as order_total_in_usd,
			tpo.custom_shipping_remarks as comments,
			tso.currency,
			tso.creation
		FROM
			`tabSales Order` tso
		inner join `tabSales Order Item` tsoi 
		on
			tsoi.parent = tso.name
			and tso.docstatus=1
			and tso.custom_to_ignore_in_shipping_wip=0
		inner join `tabPurchase Order Item` tpoi 
		on
			tpoi.sales_order = tso.name
		inner join `tabPurchase Order` tpo
		on
			tpo.name = tpoi.parent
			and tpoi.sales_order_item = tsoi.name
		left join `tabToDo` as todo
			on todo.reference_type='Sales Order'
			and todo.reference_name=tso.name	
			and todo.status!='Cancelled'
		left outer join `tabCustom Currency Exchange` fn on fn.from_currency = tso.currency
    	and fn.to_currency = 'USD'
    	and fn.`date` = (
							select `date` 
							from `tabCustom Currency Exchange` x
							where x.from_currency = tso.currency and x.to_currency = 'USD' 
								and x.`date` <= tso.transaction_date 
								ORDER BY x.date DESC 
								LIMIT 1)	
		where
			tso.per_billed <100
			and NOT EXISTS ( select 1 from `tabSales Invoice Item` tsii where tsii.so_detail=tsoi.name and tsii.sales_order=tso.name and tsii.docstatus!=2)		
			{0}
		group by
			tpo.name
		order by
			tso.name
		""".format(conditions),filters,as_dict=1,debug=1
	)

	gbp_total = 0
	euro_total = 0
	usd_total = 0
	inr_total = 0
	other_total = 0
	in_usd_total = 0
	for d in data:
		d['order_total']=fmt_money(d['order_total'], currency=d['currency'])

		gbp_total =  flt((gbp_total + (flt((d.gbp[1:]), 2) or 0)), 2)
		usd_total =  flt((usd_total + (flt((d.usd[1:]), 2) or 0)), 2)
		euro_total =  flt((euro_total + (flt((d.euro[1:]), 2) or 0)),2)
		inr_total =  flt((inr_total + (flt((d.inr[1:]), 2) or 0)), 2)
		other_total =  flt((other_total + (flt((d.others), 2) or 0)), 2)
		in_usd_total = flt((in_usd_total + (flt((d.order_total_in_usd[2:]), 2) or 0)), 2)

		# purchase invoice
		pi_items = frappe.db.get_list(
			"Purchase Invoice Item", 
			parent_doctype='Purchase Invoice',fields=["parent"],filters={"purchase_order": d.purchase_order})
		
		payment_status = ""

		if (len(pi_items) > 0):			
			pi_list = frappe.db.get_list("Purchase Invoice", 
								fields=["name","bill_no","bill_date", "currency","docstatus", "total_advance", "rounded_total", "due_date"],
								filters={"name":pi_items[0].parent})
			
		if(len(pi_items) > 0 and pi_list[0].p == 1):
			if pi_list[0].total_advance == 0:
				payment_status = "Unpaid"
			
			if pi_list[0].rounded_total != pi_list[0].total_advance and pi_list[0].total_advance != 0:
				payment_status = "Partly Paid"
			
			if pi_list[0].rounded_total == pi_list[0].total_advance and pi_list[0].total_advance != 0:
				payment_status = "Paid"
		
		else:
			if d.advance_paid == 0:
				payment_status = "Unpaid"
			
			if d.rounded_total != d.advance_paid and d.advance_paid != 0:
				payment_status = "Partly Paid"
			
			if d.rounded_total == d.advance_paid and d.advance_paid != 0:
				payment_status = "Paid"

		d['payment_status'] = payment_status


	data.append({"so":"<b>Total</b>", 
			  "gbp": "<b>" + "£ " + cstr(gbp_total) + "</b>",
			  "euro": "<b>" + "€ " + cstr(euro_total) + "</b>",
			  "usd": "<b>" + "$ " + cstr(usd_total) + "</b>",
			  "inr": "<b>" + "₹ " + cstr(inr_total) + "</b>",
			  "others": "<b>" + cstr(other_total) + "</b>",
			  "order_total_in_usd": "<b>" + "$ " + cstr(in_usd_total) + "</b>"})

	return data

@frappe.whitelist()
def create_dialog_data(sales_order):
	# print(sales_order, '----------------sales_order')
	template_path = "templates/report_dialog_data.html"
	# frappe.render_template(template_path,  dict(sales_order=sales_order))  
	return frappe.render_template(template_path,  dict(sales_order=sales_order)) 