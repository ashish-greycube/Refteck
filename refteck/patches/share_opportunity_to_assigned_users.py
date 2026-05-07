import frappe
import json
from frappe.share import add as share_doc

def execute():
    opportunity_list = frappe.db.sql("""
                            SELECT opp.name AS name, opp._assign AS assign_users FROM `tabOpportunity` AS opp """, as_dict=True)
    
    if len(opportunity_list) > 0: 
        for op in opportunity_list:
            if op.assign_users:
                # print("op.assign_users==", op.assign_users, type(op.assign_users))
                assign_users = json.loads(op.assign_users)
                # print("assign_users===", assign_users)
                if len(assign_users) > 0:
                    for user in assign_users:
                        # print("user===", user)
                        share_doc("Opportunity", op.name, user=user, read=1, write=1)
                else:
                    continue
            else:
                continue