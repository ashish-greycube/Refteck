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
		]
    }

    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)