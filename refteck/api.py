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


def set_items_for_margin_calculaion(self, method):
	if self.opportunity:
		supplier_quotation_list = frappe.db.get_all("Supplier Quotation", filters={"opportunity": self.opportunity}, fields=["name"])
		if len(supplier_quotation_list) > 0:
			for sq in supplier_quotation_list:
				sq_items = frappe.db.get_all("Supplier Quotation Item", 
								 parent_doctype="Supplier Quotation",filters={"parent": sq.name}, 
								 fields=["item_code", "uom", "qty", "rate", "parent", "name"])
				if len(sq_items) > 0:
					for qo_item in self.items:
						qo_item_found=False
						for sq_item in sq_items:
							if qo_item.item_code == sq_item.item_code:
								qo_item_found=True
								match_found_in_margin_calculation = False
								for row in self.custom_margin_calculation:
									if row.item_ref == sq_item.name :
										match_found_in_margin_calculation=True
										break
								if match_found_in_margin_calculation==False:
									self.append("custom_margin_calculation",{
										"sap_code" : sq_item.item_code,
										"uom" : sq_item.uom,
										"qty" : sq_item.qty,
										"sq_price" :sq_item.rate,
										"supplier_quotation" : sq_item.parent,
										"offer_price_without_freight" : '',
										"other_charges" : '',
										"item_ref" : sq_item.name
									})
							if qo_item_found == True:
								break

def get_connected_sq_details(self,method):
	connected_sq_list = []
	supplier_name_list=[]
	payment_terms_list = []
	currency_list = []
	actual_lead_time_list = []
	notes_list = []
	reviewed_by_list = []
	procurement_representative_list = []

	if self.opportunity:
		supplier_quotation = frappe.db.get_all("Supplier Quotation", filters={"opportunity": self.opportunity}, 
										 fields=["name", "supplier", "custom_payment_terms", "currency", 
				   								"custom_actual_lead_time", "custom_notes", "custom_supplier_quotation_reviewed_by", "owner"])
		if len(supplier_quotation) > 0:
			
			for sq in supplier_quotation:
				supplier_name_list.append(sq.supplier)
				connected_sq_list.append(sq.name)
				payment_terms_list.append(sq.custom_payment_terms)
				currency_list.append(sq.currency)
				actual_lead_time_list.append(sq.custom_actual_lead_time)
				notes_list.append(sq.custom_notes)
				reviewed_by_list.append(sq.custom_supplier_quotation_reviewed_by)
				procurement_representative_list.append(sq.owner)

			print(connected_sq_list, '-----connected_sq')
			print(supplier_name_list, '---------supplier_name_list')

			# for co_sq in connected_sq:
			# 	sq_row=sq_row+'<td>'+co_sq+'</td>'
			# sq_row=sq_row+'</tr>'

			# for supplier in supplier_name_list:
			# 	supplier_row=supplier_row+'<td>'+supplier+'</td>'
			# supplier_row=supplier_row+'</tr>'


			
			template_path = "templates/connected_sq_details.html"
			html = frappe.render_template(template_path,  dict(connected_sq=connected_sq_list, 
													  supplier_name=supplier_name_list, payment_terms=payment_terms_list, 
													  currency=currency_list, actual_lead_time=actual_lead_time_list,
													  notes=notes_list, reviewed_by=reviewed_by_list,
													  procurement_representative=procurement_representative_list))  
			self.set_onload("custom_sq_html_data", html) 

	
	# return list_a

def get_connected_qo(quotation_name):
	def get_connected(quotation_name):
		# print(quotation_name, '--quotation_name')
		amended_from = frappe.db.get_value('Quotation',quotation_name, 'amended_from')
		# print(amended_from, '------amended_from')
		if amended_from !=None:
			connected_qo_list.append(amended_from)  
			get_connected(amended_from)     
		else:
			return
			
	connected_qo_list=[]
	get_connected(quotation_name)
	# print(connected_qo_list, '----connected_qo_list')
	return connected_qo_list
	

def set_previous_quotation_data(self,method):
		connected_qo = get_connected_qo(self.name)
		template_path = "templates/previous_quotation_table.html"
		html = frappe.render_template(template_path,  dict(pervious_qo=connected_qo))  
		# print(html, '---html')  
		self.set_onload("custom_html_data", html) 


def qo_margin_calculations(self, method):
	if self.custom_margin_calculation:
		margin_total = 0
		material_margin_total = 0
		for row in self.custom_margin_calculation:
			row.buying_value = flt((row.qty * row.sq_price),2)
			
			row.offer_price_with_charges = flt((row.offer_price_without_freight + row.other_charges),2)
			# print(row.offer_price_with_charges, '--row.offer_price_with_charges')

			row.offer_value_with_charges = flt(((row.qty or 0) * (row.offer_price_with_charges or 0)),2)
			# print(row.offer_value_with_charges, '--row.offer_value_with_charges')

			# print(type(row.offer_price_without_freight), type(row.sq_price))
			if row.sq_price and row.sq_price > 0:
				row.material_margin = flt((((row.offer_price_without_freight or 0) / row.sq_price) - 1),2)
			# print(row.material_margin, '---row.material_margin')

			# print(type(row.offer_price_without_freight), 'row.offer_price_without_freight', type(row.sq_price), 'row.sq_price')
			row.margin = flt(((flt(row.offer_price_without_freight) - row.sq_price) * row.qty),2)
			# print(row.margin, '---row.margin')

			margin_total = margin_total + (row.buying_value or 0)
			material_margin_total = material_margin_total + (row.material_margin or 0)

		self.custom_margin_total = margin_total
		if self.custom_margin_total:
			self.custom_final_values = flt((self.custom_margin_total 
									+ self.custom_freight + self.custom_packing 
									+ self.custom_cipcpt + self.custom_bank_charges),2)
			self.custom_final_margin = material_margin_total - self.custom_final_values
			if  self.custom_final_values and  self.custom_final_values>0:
				self.custom_overall_margin = flt(((material_margin_total / self.custom_final_values) - 1),2)
			print(self.custom_overall_margin, '----self')
		
def validate_admin_checklist(self, method):

	self.custom_offer_prepared_by = self.owner
	self.custom_buyer = self.contact_person
	self.custom_rfq_no = self.custom_customer_opportunity_reference
	self.custom_offer_payment_terms_ = self.payment_terms_template
	self.custom_qo_incoterm = self.incoterm
	self.custom_qo_offer_lead_time = self.custom_lead_time
	self.custom_qo_validity = self.valid_till
	
	# vendor_code = frappe.db.get_value('Customer', self.party_name, 'custom_vendor_code')

	vendor_code = frappe.db.get_value('Customer Vendor Reference', {'parent': self.party_name, 'company': self.company}, ['vendor_code'])
	self.custom_vendor_code = vendor_code
	# print(vendor_code, '------vendor_code')

def set_item_descripion_in_qn_item(self, method):
	if self.custom_fetch_sq_details_in_qn == 1:
		opportunity_name = self.opportunity
		if opportunity_name:
			supplier_quotation = frappe.db.get_all("Supplier Quotation", filters={"opportunity": self.opportunity}, fields=["name"],limit=1)
			if len(supplier_quotation) > 0:
				print('supplier_quotation[0]',supplier_quotation[0])
				supplier_quotation_doc = frappe.get_doc("Supplier Quotation",supplier_quotation[0].name)
				supplier_quotation_items = supplier_quotation_doc.get("items")
				item_list = []
				for sq_item in supplier_quotation_items:
					for qo_item in self.items:
						if qo_item.item_code == sq_item.item_code:
							qo_item.description = "<b>REFTECK SCOPE OF SUPPLY:</b> <br>"+ (sq_item.custom_refteck_scope_of_supply or '')
							qo_item.custom_legacy_data = sq_item.description
							if qo_item.item_code not in item_list:
								item_list.append(qo_item.item_code)
				item_name = ", ".join((ele if ele!=None else '') for ele in item_list)
				frappe.msgprint(_("Description for item code {0} is changed.").format(item_name),alert=1)

def set_po_tracking_status_in_po_item(self,method):
	if self.custom_apply_to_all_line_item == 1 and self.custom_po_tracking_status:
		for row in self.items:
			row.custom_po_line_item_tracking_status = self.custom_po_tracking_status
		frappe.msgprint(_("PO tracking status is set to {0} in {1} PO items").format(self.custom_po_tracking_status,len(self.items)),alert=1)