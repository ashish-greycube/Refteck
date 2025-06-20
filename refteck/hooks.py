app_name = "refteck"
app_title = "Refteck"
app_publisher = "GreyCube Technologies"
app_description = "Customization for Refteck"
app_email = "admin@greycube.in"
app_license = "agpl-3.0"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/refteck/css/refteck.css"
# app_include_js = "/assets/refteck/js/refteck.js"

# include js, css files in header of web template
# web_include_css = "/assets/refteck/css/refteck.css"
# web_include_js = "/assets/refteck/js/refteck.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "refteck/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Purchase Order":"public/js/purchase_order.js",
             "Supplier Quotation":"public/js/supplier_quotation.js",
             "Request for Quotation":"public/js/request_for_quotation.js",
             "Purchase Invoice":"public/js/purchase_invoice.js",
             "Purchase Receipt":"public/js/purchase_receipt.js",
             "Quotation":"public/js/quotation.js",
             "Opportunity":"public/js/opportunity.js",
             "Sales Order":"public/js/sales_order.js",
             }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "refteck/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "refteck.utils.jinja_methods",
# 	"filters": "refteck.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "refteck.install.before_install"
# after_install = "refteck.install.after_install"
after_migrate = "refteck.migrate.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "refteck.uninstall.before_uninstall"
# after_uninstall = "refteck.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "refteck.utils.before_app_install"
# after_app_install = "refteck.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "refteck.utils.before_app_uninstall"
# after_app_uninstall = "refteck.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "refteck.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# permission_query_conditions = {
#     "Salary Slip": "refteck.api.has_permission_for_salary_slip_in_list_view",
#     "Salary Structure Assignment" : "refteck.api.has_permission_for_salary_structure_assignment_in_list_view",
#     "Additional Salary" : "refteck.api.has_permission_for_additional_salary_in_list_view"
# }

# has_permission = {
# 	"Salary Slip": "refteck.api.has_permission_to_open_salary_related_documents",
#     "Salary Structure Assignment" : "refteck.api.has_permission_to_open_salary_related_documents",
#     "Additional Salary" : "refteck.api.has_permission_to_open_salary_related_documents"	
# }

# user_allowed_for_salary_related_documents=["karan@kpkothari.com","nshah@refteck.com"]

# report_restricted_for_salary_slip=["Salary Register"]

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }
# https://github.com/frappe/frappe/pull/11527
# override_doctype_class = {
# 	"Report": "refteck.api.CustomReport"
# }
# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Request for Quotation": {
		"before_validate":"refteck.api.set_warehouse_in_child_table"
	},
    "Supplier Quotation":{
        "before_validate":"refteck.api.set_warehouse_in_child_table",
        "validate":"refteck.api.calculate_procurement_values_in_sq",
        "on_submit": "refteck.api.get_admin_checklist_qo_in_sq"
    },
    "Purchase Order":{
        "before_validate":["refteck.api.fetch_rate_from_supplier_quotation",
                       "refteck.api.validation_for_supplier"],
        "validate":"refteck.api.set_po_tracking_status_in_po_item"
    },
    "Quotation":{
        "before_validate":["refteck.api.set_common_brands",
                           "refteck.api.set_taxes_from_other_charges_comparison"],
        "validate":[
                    "refteck.api.set_items_for_margin_calculaion",
                    "refteck.api.set_offer_price_without_freight_and_other_charges_in_qo",
                    "refteck.api.validate_admin_checklist",
                    "refteck.api.set_item_descripion_in_qn_item",
                    # "refteck.api.set_quotation_material_total",
                    "refteck.api.remove_items_from_margin_calculation",
                    ],
        "before_save":"refteck.api.qo_margin_calculations",
        "onload":["refteck.api.set_previous_quotation_data",
                  "refteck.api.get_connected_sq_details"],
    },
    # "Opportunity":{
    #     "onload": "refteck.api.set_status_for_same_brand_in_op_items"
    # },
    "Purchase Invoice":{
        "before_validate": "refteck.api.validation_for_supplier"
    },
    "Purchase Receipt":{
        "before_validate": "refteck.api.validation_for_supplier"
    },
    "Appraisal":{
        "after_insert": "refteck.api.share_appraisal_to_employee_from_appraisal"
    },
    "Sales Order":{
        "validate": ["refteck.api.set_operation_gp_checklist_fields_value",
                     "refteck.api.set_item_for_operation_checklist_in_so",
                     "refteck.api.set_other_charges_in_so_from_qo",
                     "refteck.api.calculate_operating_gp_value_and_charges"],
        "before_update_after_submit": ["refteck.api.set_operation_gp_checklist_fields_value",
                                   "refteck.api.calculate_operating_gp_value_and_charges"]
    }
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"refteck.tasks.all"
# 	],
# 	"daily": [
# 		"refteck.tasks.daily"
# 	],
# 	"hourly": [
# 		"refteck.tasks.hourly"
# 	],
# 	"weekly": [
# 		"refteck.tasks.weekly"
# 	],
# 	"monthly": [
# 		"refteck.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "refteck.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "refteck.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "refteck.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["refteck.utils.before_request"]
# after_request = ["refteck.utils.after_request"]

# Job Events
# ----------
# before_job = ["refteck.utils.before_job"]
# after_job = ["refteck.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"refteck.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

