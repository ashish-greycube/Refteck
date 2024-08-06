# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from frappe.utils import date_diff, today, getdate, flt
from frappe.core.doctype.communication.email import make
from frappe.desk.query_report import build_xlsx_data
from frappe.utils.xlsxutils import make_xlsx
import json

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data, report_summary = get_data(filters)

	if not data:
		msgprint(_("No records found"))
		return columns, data
		
	# print(data, '---data')
	return columns, data, None, None, report_summary


def get_columns(filters):
	columns = [
		{
			"fieldname": "purchase_order_number",
			"fieldtype": "Data",
			"label": _("Purchase Order Number"),
			"width": 140
		},
		{
			"fieldname": "client_name",
			"fieldtype": "Data",
			"label": _("Client Name"),
			# "options": "Contact",
			"width": 120
		},
		{
			"fieldname": "customer",
			"fieldtype": "Link",
			"label": _("Customer"),
			"options": "Customer",
			"width": 170,
			"hidden": 1
		},
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": _("Company"),
			"options": "Company",
			"width": 170,
			"hidden": 1
		},
		{
			"fieldname": "invoice_number",
			"fieldtype": "Link",
			"label": _("Invoice Number"),
			"options": "Sales Invoice",
			"width": 150
		},
		{
			"fieldname": "invoice_date",
			"fieldtype": "Date",
			"label": _("Invoice Date"),
			"width": 110
		},
		{
			"fieldname": "awb_date",
			"fieldtype": "Date",
			"label": _("AWB Date"),
			"width": 110
		},
		{
			"fieldname": "due_date",
			"fieldtype": "Date",
			"label": _("Due Date"),
			"width": 110
		},
		{
			"fieldname": "usd",
			"fieldtype": "Float",
			"label": _("USD"), 
			"precision": 2,
			"width": 100
		},
		{
			"fieldname": "gbp",
			"fieldtype": "Float",
			"label": _("GBP"),
			"precision": 2, 
			"width": 100
		},
		{
			"fieldname": "euro",
			"fieldtype": "Float",
			"label": _("EURO"), 
			"precision": 2,
			"width": 100
		},
		{
			"fieldname": "invoice_amount",
			"fieldtype": "Float", 
			"label": _("Invoice Amount"),
			"precision": 2,
			"width": 120
		},
		{
			"fieldname": "amount_paid",
			"fieldtype": "Float", 
			"label": _("Amount Paid"),
			"precision": 2,
			"width": 120,
		},
		{
			"fieldname": "invoice_outstanding",
			"fieldtype": "Float", 
			"label": _("Invoice Outstanding"),
			"precision": 2,
			"width": 120,
		},
		{
			"fieldname": "days_late",
			"fieldtype": "Data",
			"label": _("Days Late"), 
			"width": 90
		}		
		]
	return columns

def get_conditions(filters):
	conditions = ""

	# if filters.get("to_date") >= filters.get("from_date"):
	# 		conditions += " and posting_date between '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))
	# else:
	# 	frappe.throw(_("To Date should be greater then From Date"))

	if filters.get("to_date"):
		conditions += " and posting_date <= %(to_date)s"

	if filters.customer:
		conditions += " and customer = %(customer)s"
	
	if filters.company:
		conditions += " and company = %(company)s"
	
	return conditions


def get_data(filters):

	conditions = get_conditions(filters)

	data = frappe.db.sql(""" SELECT name as invoice_number, po_no as purchase_order_number, contact_display as client_name,
					  customer as customer,
					  custom_airway_bill_date as awb_date, posting_date as invoice_date, due_date as due_date, 
					  if(currency='USD', grand_total, '-') as usd,
					  if(currency='GBP', grand_total, '-') as gbp,
					  if(currency='EUR', grand_total, '-') as euro,
					  grand_total as invoice_amount,
					  outstanding_amount as invoice_outstanding
					  FROM `tabSales Invoice` 
					  WHERE  outstanding_amount > 0 and docstatus = 1
					  {0}
					 """.format(conditions), filters, as_dict=1)
	
	to_date = getdate(today())
	total_invoice_amount = 0
	balance_due = 0
	amount_paid = 0
	for row in data:
		row['days_late'] =  date_diff(to_date, row['due_date'])
		row['amount_paid'] = flt((row['invoice_amount'] - row['invoice_outstanding']),2)
		total_invoice_amount = flt((total_invoice_amount + row['invoice_amount']),2)
		balance_due = flt((balance_due + row['invoice_outstanding']),2)
		amount_paid = flt((amount_paid + row['amount_paid']),2)

	report_summary=[
		{'label':'Total Invoice Amount','value':total_invoice_amount},
		{'label':'Amount Paid','value':amount_paid},
		{'label':'Balance Due','value':balance_due}		
		]

	return data, report_summary

def get_excel_of_report(columns, data):
	report_data = frappe._dict()
	report_data["columns"] = columns
	report_data["result"] = data
	xlsx_data, column_widths = build_xlsx_data(report_data, [], 1,include_filters=False ,ignore_visible_idx=True)
	xlsx_file = make_xlsx(xlsx_data, "Statement Of Accounts", column_widths=column_widths)
	return xlsx_file.getvalue()
	

@frappe.whitelist()
def send_email_to_customer(to_date, customer, company, data, columns, report_summary):

	si_data = data = json.loads(data)
	report_summary = json.loads(report_summary)
	columns = json.loads(columns)

	excel_of_report = get_excel_of_report(columns, data)
	attachments = excel_of_report
	file_name="SOA_{0}_from_{1}_{2}.xls".format(customer,to_date,frappe.generate_hash()[:2])
	attachments = [{"fname": file_name, "fcontent": excel_of_report}]


	STANDARD_USERS = ("Guest", "Administrator")

	contact_details = frappe.db.get_all('Dynamic Link', 
									 filters={'link_doctype': 'Customer', 'link_name': ['=', customer], 'parenttype': 'Contact'}, 
									 fields=['parent'])
	
	contact_emails = []
	for email in contact_details:
		# print(email.parent, '---------parent')
		email_id = frappe.db.get_value('Contact', email.parent, 'email_id')
		if email_id:
			contact_emails.append(email_id)

	# print(contact_emails, '----contact_emails')

	if len(contact_emails) > 0:
		recipients_emails = ", ".join((ele if ele!=None else '') for ele in contact_emails)
	else:
		frappe.throw(_('No primary contact found'))

	sender = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
	recipients = recipients_emails
	subject = "Statement Of Account" + " - " + customer + " till " + to_date

	

	template_path = "templates/statement_of_account_email.html"
	email_template = frappe.render_template(template_path,  dict(si_data=si_data, customer=customer, to_date=to_date, report_summary=report_summary)) 
	message = email_template	


	send_email(recipients, sender, subject, message, attachments)

def send_email(recipients, sender, subject, message, attachments):
	make(
		recipients=recipients,
		sender=sender,
		subject=subject,
		content=message,
		attachments=attachments,	
		# attachments=None,
		send_email=True,
	)["name"]

	frappe.msgprint(_("Email Sent to Users {0}").format(recipients))	

