# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters : filters = {}
    columns, data = [], []
 
    columns = get_columns()
    data = get_data(filters)
 
    if not data :
        frappe.msgprint('No Records Found')
        return columns, data

    return columns,data

def get_columns():
    columns = [
        {
            "fieldname" :"sales_invoice",
            "fieldtype" :"Link",
            "label" :"ID",
            "options" : "Sales Invoice",
            "width" :150
        },
        {
            "fieldname" :"docstatus",
            "fieldtype" :"docstatus",
            "label" :"docstatus",
            "width" :120
        },
        {
            "fieldname" :"po_no",
            "fieldtype" :"Data",
            "label" :"Customer's Purchase Order",
            "width" :150
        },
        {
            "fieldname" :"customer",
            "fieldtype" :"Link",
            "label" :"Customer",
            "options":"Customer",
            "width" :150
        },
        {
            "fieldname" :"contact_display",
            "fieldtype" :"Data",
            "label" :"Contact",
            "width" :120
        },
        {
            "fieldname" :"posting_date",
            "fieldtype" :"Date",
            "label" :"Date",
            "width" :120
        },
        {
            "fieldname" :"asn",
            "fieldtype" :"Data",
            "label" :"ASN",
            "width" :120
        },
        {
            "fieldname" :"currency",
            "fieldtype" :"Link",
            "label" :"Currency",
            "options":"Currency",
            "width" :120
        },
        {
            "fieldname" :"status",
            "fieldtype" :"data",
            "label" :"Status",
            "width" :120
        },
        {
            "fieldname" :"company",
            "fieldtype" :"Link",
            "label" :"Company",
            "options":"Company",
            "width" :200
        },
        {
            "fieldname" :"base_grand_total",
            "fieldtype" :"data",
            "label" :"Grand Total (Company Currency)",
            "width" :120
        },
        {
            "fieldname" :"ro",
            "fieldtype" :"data",
            "label" :"RO",
            "width" :120
        },
        {
            "fieldname" :"owner",
            "fieldtype" :"Link",
            "label" :"owner",
            "options": "User",
            "width" :170
        },
        {
            "fieldname" :"incoterm",
            "fieldtype" :"Link",
            "label" :"Incoterm",
            "options":"Incoterm",
            "width" :120
        },
        {
            "fieldname" :"ageing_days",
            "fieldtype" :"Int",
            "label" :"Ageing Days",
            "width" :120
        },
    ]
    return columns

def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql("""
            SELECT 
                si.name as sales_invoice,
                si.docstatus as docstatus,
                si.po_no as po_no,
                si.customer as customer,
                si.contact_display as contact_display,
                si.posting_date as posting_date,
                si.custom_asn as asn,
                si.currency as currency,
                si.status as status,
                si.company as company,
                si.base_grand_total as base_grand_total,
                si.custom_ro as ro,
                si.owner as owner,
                si.incoterm as incoterm,
                DATEDIFF(CURDATE(), si.posting_date) as ageing_days
            FROM `tabSales Invoice` AS si
            WHERE docstatus >= 0 {0}
            ORDER BY posting_date DESC
        """.format(conditions),as_dict = 1,debug=1)
    
    return data

        
def get_conditions(filters):
    conditions = ""

    if filters.get("company"):
        conditions += " AND company = '{0}'".format(filters["company"])

    if filters.get("customer"):
        conditions += " AND customer ='{0}'".format(filters["customer"])
        
    if filters.get("date"):
        conditions += " AND posting_date ='{0}'".format(filters["date"])
    
    if filters.get("status"):
        conditions += " AND status ='{0}'".format(filters["status"])
    
    if filters.get("is_ro_set"):
        if filters.get("is_ro_set") == "Set":
            conditions += " AND (custom_ro OR custom_ro != '')"
        elif filters.get("is_ro_set") == "Not Set":
            conditions += " AND (custom_ro IS NULL OR custom_ro = '')"
        
    return conditions
