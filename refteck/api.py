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

		# supplier quotation
		supplier_quotation_list = frappe.db.get_all("Supplier Quotation", filters={"opportunity": self.opportunity, "docstatus":1, "status":"Submitted"}, fields=["name"])
		if len(supplier_quotation_list) > 0:

			# supplier quotation item
			for sq in supplier_quotation_list:
				sq_items = frappe.db.get_all("Supplier Quotation Item",parent_doctype="Supplier Quotation",filters={"parent": sq.name},fields=["item_code", "uom", "qty", "rate", "parent", "name"])
				if len(sq_items) > 0:
					for qo_item in self.items:
						qo_item_found=False

						for sq_item in sq_items:
							if qo_item.item_code == sq_item.item_code and qo_item.qty == sq_item.qty:
								qo_item_found=True
								match_found_in_margin_calculation = False

								for row in self.custom_margin_calculation:
									if row.qo_item_ref == qo_item.name:
										if not row.supplier_quotation:
											row.supplier_quotation = sq_item.parent
										match_found_in_margin_calculation = True
										break
								
								if match_found_in_margin_calculation == False:
									row=self.append("custom_margin_calculation",{})
									row.sap_code=sq_item.item_code
									row.uom=sq_item.uom
									row.qty=sq_item.qty
									row.sq_price=sq_item.rate
									row.supplier_quotation=sq_item.parent
									row.sq_item_ref=sq_item.name
									row.qo_item_ref=qo_item.name
							
							if qo_item_found == True:
								break

def remove_items_from_margin_calculation(self, method):
	to_remove = []
	item_list=[]
	for item in self.items:
		item_list.append(item.name)

	for row in self.custom_margin_calculation:
		if row.qo_item_ref not in item_list:
			to_remove.append(row)
		elif row.supplier_quotation==None or row.supplier_quotation=='':
			to_remove.append(row)
		elif frappe.db.exists('Supplier Quotation', row.supplier_quotation)==None:
			to_remove.append(row)
		elif frappe.db.exists('Supplier Quotation', row.supplier_quotation):
			sq_opp = frappe.db.get_value('Supplier Quotation', row.supplier_quotation, 'opportunity')
			if self.opportunity != sq_opp:
				to_remove.append(row)
	
	[self.custom_margin_calculation.remove(d) for d in to_remove]

	for index,margin in enumerate(self.custom_margin_calculation):
		margin.idx=index+1

def get_connected_sq_details(self,method):
	connected_sq_list = []
	supplier_name_list=[]
	payment_terms_list = []
	currency_list = []
	actual_lead_time_list = []
	notes_list = []
	reviewed_by_list = []
	procurement_representative_list = []
	total_weight_list = []
	sq_ref_list=[]

	if self.opportunity:
		if len(self.custom_margin_calculation) > 0:	
			for sq_ref in self.custom_margin_calculation:
				if sq_ref.supplier_quotation:
					if sq_ref.supplier_quotation not in sq_ref_list:
						sq_ref_list.append(sq_ref.supplier_quotation)
			if len(sq_ref_list) > 0:
				for sq	in sq_ref_list:
					sq_doc_exist = frappe.db.exists('Supplier Quotation', sq)
					if sq_doc_exist:
						sq_doc = frappe.get_doc('Supplier Quotation', sq)
						if sq_doc.opportunity == self.opportunity:
							supplier_name_list.append(sq_doc.supplier)
							connected_sq_list.append(sq_doc.name)
							payment_terms_list.append(sq_doc.custom_payment_terms)
							currency_list.append(sq_doc.currency)
							actual_lead_time_list.append(sq_doc.custom_actual_lead_time)
							notes_list.append(sq_doc.custom_notes)
							reviewed_by_list.append(sq_doc.custom_supplier_quotation_reviewed_by)
							procurement_representative_list.append(sq_doc.owner)
							total_weight_list.append(sq_doc.custom_total_weight)

			if len(connected_sq_list) > 0:	
				template_path = "templates/connected_sq_details.html"
				html = frappe.render_template(template_path,  dict(connected_sq=connected_sq_list, 
														supplier_name=supplier_name_list, payment_terms=payment_terms_list, 
														currency=currency_list, actual_lead_time=actual_lead_time_list,
														notes=notes_list, reviewed_by=reviewed_by_list,
														procurement_representative=procurement_representative_list,
														total_weight_list=total_weight_list))  
				self.set_onload("custom_sq_html_data", html) 

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
		if len(connected_qo)>0:
			template_path = "templates/previous_quotation_table.html"
			html = frappe.render_template(template_path,  dict(pervious_qo=connected_qo))  
			# print(html, '---html')  
			self.set_onload("custom_html_data", html) 

def set_taxes_from_other_charges_comparison(self,method):
	if len(self.custom_other_charges_comparison) > 0:
		self.taxes = []
		default_income_account = frappe.db.get_value('Company', self.company, 'default_income_account')
		for charges in self.custom_other_charges_comparison:
			if charges.offer_charges > 0:
				tax = self.append("taxes")
				tax.charge_type = "Actual"
				tax.account_head = default_income_account
				tax.tax_amount = charges.offer_charges
				tax.description = charges.charge_type
				# tax.custom_admin_checklist_other_charges_reference=charges.name

####### code to syanc with sales & taxes table
# def set_taxes_from_other_charges_comparison(self,method):
# 	default_income_account = frappe.db.get_value('Company', self.company, 'default_income_account')
# 	# items_to_be_removed=[]
# 	if len(self.custom_other_charges_comparison)>0:
# 		for charges in self.custom_other_charges_comparison:
# 			charges_found=False
# 			for item_tax in self.taxes:
# 				if item_tax.custom_admin_checklist_other_charges_reference==charges.name:
# 					charges_found=True
# 					item_tax.tax_amount = charges.offer_charges
# 					item_tax.description = charges.charge_type		
# 					print(charges.name, '---charges.name')			
# 					break
# 			if charges_found==False:
# 				tax = self.append("taxes")
# 				tax.charge_type = "Actual"
# 				tax.account_head = default_income_account
# 				tax.tax_amount = charges.offer_charges
# 				tax.description = charges.charge_type
# 				tax.custom_admin_checklist_other_charges_reference=charges.name
# 				print(tax.name, '---name')

		####### delete
		# for item_tax in self.taxes:
		# 	if item_tax.custom_admin_checklist_other_charges_reference!=None or item_tax.custom_admin_checklist_other_charges_reference!='':
		# 		item_charges_match_found=False
		# 		for charges in self.custom_other_charges_comparison:
		# 			if item_tax.custom_admin_checklist_other_charges_reference==charges.name:
		# 				item_charges_match_found=True
		# 				break
		# 		if item_charges_match_found ==False:
		# 			items_to_be_removed.append(item_tax)
		# if len(items_to_be_removed)>0:
		# 	for re in items_to_be_removed:
		# 		self.remove(re)
			# [self.remove(d) for d in items_to_be_removed]


# def set_quotation_material_total(self, method):
# 	total_offer_freight = 0
# 	total_offer_packing = 0
# 	total_offer_cip_cpt = 0
# 	total_offer_bank_charges = 0
# 	if len(self.taxes) > 0 and len(self.custom_margin_calculation) > 0:
# 		for tax in self.taxes:
# 			desc = tax.description
# 			# print(item.description, '--item.description')
# 			freight = desc.find("Freight")
# 			packing = desc.find("Packing")
# 			cip = desc.find("CIP")
# 			cpt = desc.find("CPT")
# 			bank = desc.find("Bank")
# 			# print(freight, '----x')
# 			if freight > -1:
# 				total_offer_freight = total_offer_freight + tax.tax_amount
# 			if packing > -1:
# 				total_offer_packing = total_offer_packing + tax.tax_amount
# 			if cip > -1 or cpt > -1:
# 				total_offer_cip_cpt = total_offer_cip_cpt + tax.tax_amount
# 			if bank > -1:
# 				total_offer_bank_charges = total_offer_bank_charges + tax.tax_amount
					
	
# 	self.custom_offer_freight = total_offer_freight
# 	self.custom_offer_packing = total_offer_packing
# 	self.custom_offer_cipcpt = total_offer_cip_cpt
# 	self.custom_offer_bank_charges = total_offer_bank_charges

def qo_margin_calculations(self, method):
	if self.custom_margin_calculation and len(self.custom_margin_calculation)>0:
		supplier_quotation_material_total = 0
		offer_material_total = 0

		for row in self.custom_margin_calculation:
			row.buying_value = flt(((row.qty or 0) * (row.sq_price or 0)),2)
			
			row.offer_price_with_charges = flt(((row.offer_price_without_freight or 0) + (row.other_charges or 0)),2)

			row.offer_value_with_charges = flt(((row.qty or 0) * (row.offer_price_with_charges or 0)),2)

			if row.sq_price and row.sq_price > 0:
				row.material_margin = flt(((((row.offer_price_without_freight or 0) / row.sq_price) - 1)*100), 2)

			row.margin = flt(((flt(row.offer_price_without_freight or 0) - (row.sq_price or 0)) * row.qty),2)

			supplier_quotation_material_total = supplier_quotation_material_total + (row.buying_value or 0)
			offer_material_total = offer_material_total + (row.offer_value_with_charges or 0)

		self.custom_supplier_quotation_material_total = supplier_quotation_material_total
		self.custom_offer_material_total = offer_material_total

		final_value = 0
		final_offer_values = 0
		if len(self.custom_other_charges_comparison) > 0:
			for charges in self.custom_other_charges_comparison:
				final_value = final_value + (charges.supplier_quotation_charges or 0)
				final_offer_values = final_offer_values + (charges.offer_charges or 0)

		self.custom_total_sq_other_charges = final_value
		self.custom_total_offer_other_charges = final_offer_values
		self.custom_final_values = final_value + (self.custom_supplier_quotation_material_total or 0)
		self.custom_final_offer_values = final_offer_values + (self.custom_offer_material_total or 0)
		
		self.custom_final_margin = (self.custom_final_offer_values or 0) - (self.custom_final_values or 0)
		if  self.custom_final_values and  self.custom_final_values > 0:
			self.custom_overall_margin = (self.custom_final_margin / self.custom_final_values) * 100
		
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

def set_offer_price_without_freight_and_other_charges_in_qo(self, method):
	if self.amended_from and self.is_new():
		if len(self.custom_margin_calculation) > 0:
			for margin in self.custom_margin_calculation:
				sq_doc = frappe.get_doc("Supplier Quotation", margin.supplier_quotation)
				prev_qo = frappe.get_doc("Quotation", self.amended_from)
				for row in prev_qo.custom_margin_calculation:
					if sq_doc.amended_from and row.supplier_quotation == sq_doc.amended_from:
						margin.offer_price_without_freight = row.offer_price_without_freight
						margin.other_charges = row.other_charges
						break
					elif row.supplier_quotation == sq_doc.name:
						margin.offer_price_without_freight = row.offer_price_without_freight
						margin.other_charges = row.other_charges
						break			

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
							qo_item.description = "<b>Scope of Supply:</b> <br>"+ (sq_item.custom_refteck_scope_of_supply or '')
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