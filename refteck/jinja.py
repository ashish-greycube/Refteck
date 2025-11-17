import frappe
from frappe import _

@frappe.whitelist()
def get_employee_promotion_designation_details(employee):
	emp_promotion_list = frappe.get_all(
		"Employee Promotion",
		filters={"employee": employee},
		fields=["name","promotion_date"],
		order_by="promotion_date desc",
		limit=1,
	)

	if len(emp_promotion_list) > 0:
		promotion_date = ""
		current_designation = ""
		new_designation = ""

		promotion_doc = frappe.get_doc("Employee Promotion", emp_promotion_list[0].name)
		promotion_date = promotion_doc.promotion_date
		
		if len(promotion_doc.promotion_details) > 0:
			for detail in promotion_doc.promotion_details:
				if detail.property == "Designation":
					current_designation = detail.current
					new_designation = detail.new
					break

		return {
			"promotion_date": promotion_date,
			"current_designation": current_designation,
			"new_designation": new_designation
		}