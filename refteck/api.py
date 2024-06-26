from __future__ import unicode_literals
import frappe, erpnext
import frappe.defaults
from frappe import msgprint, _
from frappe.utils import flt
from frappe.share import add

def set_warehouse_in_child_table(self,method):
    if self.set_warehouse_cf and len(self.get('items'))>0:
        for row in self.get('items'):
            row.warehouse = self.set_warehouse_cf
        frappe.msgprint(_("Item Warehouse {0} is set in all rows of item table").format(self.set_warehouse_cf), alert=True)

def fetch_rate_from_supplier_quotation(self,method):
    if self.custom_supplier_quotation:
        sq_name = self.custom_supplier_quotation
        sq = frappe.get_doc("Supplier Quotation",sq_name)
        sq_items = sq.get("items")
        po_item = self.get("items")
        sq_item_code = []
        found_rate=True
        for r in po_item:
            for row in sq_items:
                sq_item_code.append(row.item_code)
                if r.item_code == row.item_code:
                    r.rate = row.rate
            if r.item_code not in sq_item_code:
                found_rate=False
                frappe.msgprint(_("Row {0}: Value is not changed for {1}").format(r.idx,r.item_code))
        if found_rate==True:
            frappe.msgprint(_("All item's rate are changed successfully "))   
                
def validation_for_supplier(self,method):
    po_supplier = self.supplier
    supplier = frappe.get_doc("Supplier",po_supplier)
    if supplier.is_approved_for_purchase_cf == 1:
        pass
    else :
        frappe.throw(_('<a href="/app/supplier/{0}" >{0}</a>'+" Supplier is not valid for {1} ").format(po_supplier,self.doctype))
    
def set_common_brands(self,method):
    items = self.get("items")
    item_brands = []
    for i in items:
        if i.brand:
            if i.brand not in item_brands:
                item_brands.append(i.brand)
    if len(item_brands) > 0:
        common_brand = ", ".join(str(elem) for elem in item_brands)
        self.common_brands_in_item_cf = common_brand
        frappe.msgprint(_("Common brands field is updated based on item brands"),alert=True)
    else:
        self.common_brands_in_item_cf = ''

def share_appraisal_to_employee_from_appraisal(self,method):
    report_to_employee_id = frappe.db.get_value("Employee",self.employee,"reports_to")
    if report_to_employee_id == None or report_to_employee_id == "":
        frappe.msgprint(_("Appraisal is not shared with any user as no employee found for report to {0}").format(self.employee),alert=1)
    else :
        user_id = frappe.db.get_value("Employee",report_to_employee_id,"user_id")
        if user_id == "" or user_id == None:
            frappe.msgprint(_("Appriasal is not shared with any user as there is no user id found in {0}").format(report_to_employee_id),alert=1)
        else :
            shared_with_user=add(self.doctype, self.name, user=user_id, read=1, write=1, submit=1)
            if shared_with_user:
                    frappe.msgprint(
                        _("Appraisal {0} is shared with {1} user").format(self.name,user_id),
                        alert=1,
                    )
        