from __future__ import unicode_literals

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def after_migrate():
    custom_fields = {
        "Supplier": [
            {
				"fieldname":"is_approved_for_purchase_cf",
				"label":"Is Approved For Purchase?",
				"fieldtype":"Check",
				"insert_after": "country",
				"is_custom_field":1,
				"is_system_generated":0
            }			
        ],
        "Request for Quotation": [	
			{
				"fieldname":"set_warehouse_cf",
				"label":"Item Warehouse",
				"fieldtype":"Link",
                "options":"Warehouse",
				"insert_after": "items_section",
				"is_custom_field":1,
				"is_system_generated":0
			}			
		],
        "Supplier Quotation": [	
			{
				"fieldname":"set_warehouse_cf",
				"label":"Item Warehouse",
				"fieldtype":"Link",
                "options":"Warehouse",
				"insert_after": "items_section",
				"is_custom_field":1,
				"is_system_generated":0
			}			
		],
        "Quotation": [	
			{
				"fieldname":"common_brands_in_item_cf",
				"label":"Common Brands",
				"fieldtype":"Small Text",
				"insert_after": "customer_name",
				"is_custom_field":1,
				"is_system_generated":0
			},
            {
                "fieldname": "custom_gsheet_links_section_break",
                "fieldtype": "Section Break",
                "insert_after" : "custom_previous_quotation_details",
                "is_custom_field":1,
				"is_system_generated":0
			},
             {
                "fieldname": "custom_generated_spreadsheet_urls",
                "fieldtype": "Table",
                "insert_after" : "custom_gsheet_links_section_break",
                "label":"Generated Spreadsheet URLs",
                "is_custom_field":1,
				"is_system_generated":0,
                "options" : "Generated Spreadsheet URL RT",
                "allow_on_submit" : 1
			}			
		],
        "Sales Order": [
            {
                "fieldname": "custom_gsheet_links_section_break",
                "fieldtype": "Section Break",
                "insert_after" : "custom_material_margin_",
                "is_custom_field":1,
				"is_system_generated":0
			},
             {
                "fieldname": "custom_generated_spreadsheet_urls",
                "fieldtype": "Table",
                "insert_after" : "custom_gsheet_links_section_break",
                "label":"Generated Spreadsheet URLs",
                "is_custom_field":1,
				"is_system_generated":0,
                "options" : "Generated Spreadsheet URL RT",
                "allow_on_submit" : 1
			}
		]
    }

    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)