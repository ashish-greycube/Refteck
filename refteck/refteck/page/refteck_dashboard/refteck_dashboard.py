"""
Refteck Group — Multi-Company Shipping Dashboard
Frappe ERPNext Backend Controller

File location (desk page):
  <your_app>/page/refteck-dashboard/refteck_dashboard.py
  OR
  <your_app>/refteck_dashboard/api.py  (for whitelisted API methods only)

All methods decorated with @frappe.whitelist() are callable from
the frontend via frappe.call('your_app.page.refteck-dashboard.refteck_dashboard.get_dashboard_metrics').
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, today, date_diff, nowdate

# ─── COMPANY CONSTANTS ────────────────────────────────────────────────────────

COMPANY_MAP = {
    "india":  "Refteck Solution (Pvt.) Limited",
    "europe": "Refteck Solutions Europe GmbH",
    "uk":     "Refteck Solutions Limited",
    "usa":    "Refteck Solutions USA Inc.",
}

# COMPANY_MAP = frappe.db.sql_list("SELECT name FROM `tabCompany` AS tc WHERE tc.is_group = 0")

CURRENCY_MAP = {
    "india":  "INR",
    "europe": "EUR",
    "uk":     "GBP",
    "usa":    "USD",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE CONTEXT  (called automatically when /refteck-dashboard is loaded)
# ═══════════════════════════════════════════════════════════════════════════════

def get_context(context):
    """Inject server-side context into the Jinja template."""
    context.no_cache = 1
    context.title = "Refteck Group — Multi-Company Shipping Dashboard"
    context.companies = COMPANY_MAP
    context.show_sidebar = False
    return context

def _build_filters(alias, company=None, from_date=None, to_date=None, **kwargs):
    """
    Builds reusable filter strings and values for dynamic Frappe SQL queries.
    
    :param alias: The SQL table prefix (e.g., 'so', 'po', 'si')
    :param kwargs: Key-value pairs for specific field mapping (e.g., party="Cust001")
    """
    conditions = [f"{alias}.docstatus < 2"]
    values = {}

    # 1. Company Filter
    if company and company.lower() != "all":
        conditions.append(f"{alias}.company = %(company)s")
        values["company"] = company

    # 2. Date Range Filters
    if from_date:
        conditions.append(f"{alias}.creation >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        conditions.append(f"{alias}.creation <= %(to_date)s")
        values["to_date"] = to_date

    # 3. Dynamic Kwargs Mapping (so, po, party, payment_term, supplier, etc.)
    # Maps internal function arguments to Frappe DocType Database Column Names
    field_mappings = {
        "so": "name",
        "po": "name",
        "party": "customer",          # Maps 'party' arg to 'customer' field in SO/SI
        "payment_term": "payment_terms_template",
        "supplier": "supplier"
    }

    for key, value in kwargs.items():
        if value:
            db_field = field_mappings.get(key, key)
            if key in ["so", "po"]:
                # Wildcard search for Document Names
                conditions.append(f"{alias}.{db_field} LIKE %({key})s")
                values[key] = f"%{value}%"
            else:
                # Exact match for fields like customer, supplier, payment terms
                conditions.append(f"{alias}.{db_field} = %({key})s")
                values[key] = value

    return {
        "where_clause": " AND ".join(conditions),
        "values": values
    }

# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD TAB - NUMBER CARDS
# ═══════════════════════════════════════════════════════════════════════════════
@frappe.whitelist()
def get_dashboard_metrics(company=None, from_date=None, to_date=None,
                        so=None, party=None, payment_term=None, po=None, supplier=None):
    """
    Returns KPI cards shown at the top of the Dashboard tab.

    """

    so_f = _build_filters("so", company, from_date, to_date, so=so, party=party, payment_term=payment_term)
    si_f = _build_filters("si", company, from_date, to_date, party=party) # SI shares company/date/customer filters
    po_f = _build_filters("po", company, from_date, to_date, po=po, supplier=supplier)

    currency = "USD"
    if company:
        currency = frappe.db.get_value("Company", company, "default_currency")

    # ── 1. Total Orders Received & Gross Margin & Rounded Total ──────────────────────────────────────────────
    orders_data = frappe.db.sql("""
                    SELECT 
                        COUNT(so.name) AS total_so,
                        SUM(so.rounded_total) AS total_orders ,
                        SUM(so.custom_po_margin) AS total_gross_margin
                    FROM `tabSales Order` AS so
                    WHERE {where_clause}
                       """.format(where_clause=so_f["where_clause"]), so_f["values"], as_dict=True)[0]

    # ── 2. Sea Shipment ──────────────────────────────────────────────
    sea_shipments_data = frappe.db.sql("""
                    SELECT COUNT(si.name) AS total_si, SUM(si.rounded_total) AS total_sea_shipment FROM `tabSales Invoice` AS si WHERE {where_clause} AND si.mode_of_transport = "Ship" 
                           """.format(where_clause=si_f["where_clause"]), si_f["values"], as_dict=True)[0]

    # ── 3. Air Shipment ──────────────────────────────────────────────
    air_shipments_data = frappe.db.sql("""
                    SELECT COUNT(si.name) AS total_si, SUM(si.rounded_total) AS total_air_shipment FROM `tabSales Invoice` AS si WHERE {where_clause} AND si.mode_of_transport = "Air"
                            """.format(where_clause=si_f["where_clause"]), si_f["values"], as_dict=True)[0]

    # ── 4. Active Orders (Shipping WIP Report) ──────────────────────────────────────────────
    from refteck.refteck.report.shipping_wip.shipping_wip import get_data as shipping_wip_data
    wip_filters = {
        "from_date" : from_date,
        "to_date": to_date,
        "client": party or '',
        "company": company
    }
    wip_data = shipping_wip_data(wip_filters)
    wip_total = 0
    if len(wip_data) > 0:
        last_row = wip_data[-1]
        default_currency = frappe.db.get_value("Company", company, "default_currency")

        currency_map = {"INR": "inr", "GBP": "gbp", "USD": "usd", "EUR": "euro"}
        wip_total = last_row.get(currency_map.get(default_currency, "order_total_in_usd")) or 0

    # ── 5. Open Shipment ──────────────────────────────────────────────
    open_shipment_data = frappe.db.sql("""
                    SELECT SUM(si.grand_total) AS total_open_shipment FROM `tabSales Invoice` AS si WHERE {where_clause} AND si.custom_ro != ""
                                       """.format(where_clause=si_f["where_clause"]), si_f["values"], as_dict=True)[0]

    
    # ── 6. Shipment Ration ──────────────────────────────────────────────
    shipment_ratio = 0
    if orders_data.total_so > 0:
        shipment_ratio = ((sea_shipments_data.total_si or 0) + (air_shipments_data.total_si or 0))/(orders_data.total_so)

    # ── 7. Overdue SO ──────────────────────────────────────────────
    overdue_so = frappe.db.sql("""
                    SELECT COUNT(so.name) AS total_overdue FROM `tabSales Order` AS so WHERE {where_clause} AND so.delivery_date < CURDATE() AND so.status NOT IN ('Completed','Cancelled')
                            """.format(where_clause=so_f["where_clause"]), so_f["values"], as_dict=True)[0]
    
    # ── 8. AP Advance Paid ──────────────────────────────────────────────
    ap_advance_paid = frappe.db.sql(""" 
                    SELECT SUM(po.advance_paid) AS total_advance_paid FROM `tabPurchase Order` AS po WHERE {where_clause} AND po.advance_paid > 0 
                            """.format(where_clause=po_f["where_clause"]), po_f["values"], as_dict=True)[0]

    # ── 9. Intercompany Transcation ──────────────────────────────────────────────
    ic_data = frappe.db.sql("""
                    SELECT COUNT(so.name) AS ic_exposure FROM `tabSales Order` AS so WHERE {where_clause} AND so.custom_is_intercompany_transaction = 1
                        """.format(where_clause=so_f["where_clause"]), so_f["values"], as_dict=True)[0]

    return {
        "total_orders":  flt((orders_data.total_orders), 2) or 0,
        "sea_shipments":  flt((sea_shipments_data.total_sea_shipment), 2) or 0,
        "air_shipments": flt((air_shipments_data.total_air_shipment), 2) or 0,
        "active_orders" : wip_total or 0,
        "open_shipment" : flt((open_shipment_data.total_open_shipment), 2) or 0, 
        "total_gross_margin": flt((orders_data.total_gross_margin), 2) or 0,
        "shipment_ratio": flt((shipment_ratio), 2) or 0,
        "overdue_so": overdue_so.total_overdue or 0,
        "ap_advance_paid": flt((ap_advance_paid.total_advance_paid), 2) or 0,
        "ic_exposure": ic_data.ic_exposure or 0,
        "currency": currency or "USD"
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD TAB - ORDERS RECEIVED TABLE
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_orders_received(company=None, from_date=None, to_date=None,
                        so=None, party=None, payment_term=None, po=None):
    """
    DocType: Sales Order
    """
    # print(from_date, "--from" , to_date, "--to=====================", so)
    conditions = ["so.docstatus < 2"]
    values = {}

    if company and company != "all":
        conditions.append("so.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(so.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if so:
        conditions.append("so.name LIKE %(so_name)s")
        values["so_name"] = so

    if party:
        conditions.append("so.customer LIKE %(party)s")
        values["party"] = party

    if payment_term:
        conditions.append("so.payment_terms_template = %(payment_term)s")
        values["payment_term"] = payment_term

    if po:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabPurchase Order Item` AS poi 
                WHERE poi.sales_order = so.name AND poi.parent = %(po)s
                ) """)
        values["po"] = po

    where = " AND ".join(conditions)

    so_data =  frappe.db.sql("""
        SELECT
            so.name                          AS order_no,
            so.customer                      AS party_name,
            so.rounded_total                 AS amount,
            so.currency                      AS currency,
            so.transaction_date              AS order_date,
            so.payment_terms_template        AS payment_terms,
            so.delivery_date                 AS due_date,
            so.status,
            CASE
                WHEN so.delivery_date < CURDATE()
                     AND so.status NOT IN ('Completed','Cancelled')
                THEN DATEDIFF(CURDATE(), so.delivery_date)
                ELSE 0
            END AS overdue_days
        FROM `tabSales Order` so
        WHERE {where}
        ORDER BY so.transaction_date DESC
    """.format(where=where), values, as_dict=True)

    return so_data


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD TAB - READY FOR DISPATCH
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_ready_for_dispatch(company=None, from_date=None, to_date=None,
                        po=None, supplier=None, so=None):

    """
    DocType: Sales Order  (is_order_ready = 1)
    """
    conditions = [
        "po.docstatus < 2",
        "po.custom_po_tracking_status = 'Ready for Dispatch'"
    ]
    values = {}

    if company and company != "all":
        conditions.append("po.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(po.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if po:
        conditions.append("po.name LIKE %(po_name)s")
        values["po_name"] = po

    if supplier:
        conditions.append("po.supplier LIKE %(supplier)s")
        values["supplier"] = supplier

    if so:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabPurchase Order Item` AS poi 
                WHERE poi.parent = po.name 
                AND poi.sales_order = %(so)s
                ) """)
        values["so"] = so

    where = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT 
            po.name AS order_no,
            po.supplier AS supplier,
            po.rounded_total AS value,
            po.schedule_date AS ready_date,
            po.currency
        FROM `tabPurchase Order` AS po
        WHERE {where} 
            """.format(where=where), values, as_dict=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD TAB - POST-SHIPMENT
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_post_shipment(company=None, from_date=None, to_date=None,
                        so=None, party=None, po=None):
    conditions = [
        "so.docstatus < 2",
        "si.status IN ('Paid', 'Unpaid', 'Partly Paid')"
    ]
    values = {}

    if company and company != "all":
        conditions.append("so.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(so.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if so:
        conditions.append("so.name LIKE %(so_name)s")
        values["so_name"] = so

    if party:
        conditions.append("so.customer LIKE %(party)s")
        values["party"] = party

    if po:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabPurchase Order Item` AS poi 
                WHERE poi.sales_order = so.name AND poi.parent = %(po)s
                ) """)
        values["po"] = po

    where = " AND ".join(conditions)

    return frappe.db.sql("""
                SELECT
                    so.name AS order_no,
                    so.customer AS party_name,
                    so.rounded_total AS amount,
                    so.delivery_date,
                    sii.parent AS invoice_no,
                    si.status AS payment_terms,
                    SUM(per.allocated_amount) AS payment_amount,                                 
                    MAX(pe.posting_date) AS payment_date,
                    so.currency
                FROM
                    `tabSales Order` AS so
                INNER JOIN `tabSales Invoice Item` AS sii ON
                    sii.sales_order = so.name
                INNER JOIN `tabSales Invoice` AS si ON 
                    si.name = sii.parent 
                LEFT JOIN `tabPayment Entry Reference` AS per ON 
                    per.reference_name = si.name AND per.reference_doctype = 'Sales Invoice'
                LEFT JOIN `tabPayment Entry` AS pe ON 
                    pe.name = per.parent AND pe.docstatus < 2
                WHERE {where}
                GROUP BY so.name
                    """.format(where=where), values, as_dict=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PURCHASE ORDERS TAB - PO NUMBER CARDS
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_purchase_order_kpis(company=None, from_date=None, to_date=None):
    """ bar for Purchase Orders tab."""
    conditions = ["po.docstatus < 2"]
    values = {}

    if company and company != "all":
        conditions.append("po.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)
    
    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(po.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    where = " AND ".join(conditions)
    
    po_details = frappe.db.sql("""
                    SELECT 
                        COUNT(CASE WHEN po.status != 'Completed' THEN po.name END) AS total_po,
                        COUNT(CASE WHEN po.advance_paid > 0 THEN po.name END) AS total_po_with_advance,
                        SUM(po.rounded_total) AS total_amt,
                        po.currency
                    FROM 
                        `tabPurchase Order` AS po
                    WHERE {where}
                        """.format(where=where), values, as_dict=True)[0]
    
    credit_count = (po_details.total_po or 0) - (po_details.total_po_with_advance or 0)

    return {
        "total_pos": po_details.total_po or 0,
        "advance_count": po_details.total_po_with_advance or 0,
        "credit_count": credit_count,
        "total_value": po_details.total_amt or 0,
        "currency": po_details.currency or "USD"
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  PURCHASE ORDERS TAB - PO TABLE
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_purchase_orders(company=None, from_date=None, to_date=None,  po=None, supplier=None, so=None):
    """
    Purchase Orders tracking table.
    """
    conditions = [
        "po.docstatus < 2",
        "po.status != 'Completed'"
    ]

    values = {}

    if company and company != "all":
        conditions.append("po.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(po.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if po:
        conditions.append("po.name LIKE %(po_name)s")
        values["po_name"] = po

    if supplier:
        conditions.append("po.supplier LIKE %(supplier)s")
        values["supplier"] = supplier

    if so:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabPurchase Order Item` AS poi 
                WHERE poi.parent = po.name 
                AND poi.sales_order = %(so)s
                ) """)
        values["so"] = so

    where = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT
            po.name AS po_name,
            po.custom_customer_po_no AS customer_po,
            po.company ,
            po.supplier ,
            po.rounded_total AS po_value,
            po.currency,
            po.custom_updated_payment_terms AS payment_terms
        FROM
            `tabPurchase Order` AS po 
        WHERE {where}
        """.format(where=where), values, as_dict=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SALES ORDERS TAB - NUMBER CARD
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_sales_order_kpis(company=None, from_date=None, to_date=None):
    """KPI bar for Sales Orders tab."""
    conditions = ["so.docstatus < 2"]
    values = {}

    if company and company != "all":
        conditions.append("so.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)
    
    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(so.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    where = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT 
            COUNT(CASE WHEN so.status != 'Completed' THEN so.name END) AS total_so,
            COUNT(CASE WHEN so.custom_is_intercompany_transaction = 1 THEN so.name END) AS ic_count,
            SUM(so.rounded_total) AS total_value,
            COUNT(CASE WHEN so.advance_paid > 0 THEN so.name END) AS total_so_advance,
            SUM(CASE WHEN so.advance_paid > 0 THEN so.advance_paid END) AS total_so_advance_value,
            so.currency
        FROM `tabSales Order` AS so 
        WHERE {where} """.format(where=where), values, as_dict=True)[0]

# ═══════════════════════════════════════════════════════════════════════════════
#  SALES ORDERS TAB - TABLE
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_sales_orders(company=None, so=None, from_date=None, to_date=None, party=None, po=None):
    """
    Sales Orders tracking table.
    """

    conditions = ["so.docstatus < 2", "so.status != 'Completed'"]
    values = {}

    if company and company != "all":
        conditions.append("so.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(so.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if so:
        conditions.append("so.name LIKE %(so_name)s")
        values["so_name"] = so

    if party:
        conditions.append("so.customer LIKE %(party)s")
        values["party"] = party
    
    if po:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabPurchase Order Item` AS poi 
                WHERE poi.sales_order = so.name AND poi.parent = %(po)s
                ) """)
        values["po"] = po

    where = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT 
            so.name AS so_name,
            COALESCE(so.po_no, so.name ) AS so_number,
            so.company ,
            so.customer,
            so.rounded_total AS so_value,
            so.currency 
        FROM `tabSales Order` AS so 
        WHERE {where}
    """.format(where=where), values, as_dict=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PRODUCTION TAB
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_production_orders(company=None, from_date=None, to_date=None,
                        po=None, supplier=None, so=None):
    """
    Work Orders currently in production.
    """
    conditions = [
        "po.docstatus < 2"
    ]
    values = {}

    if company and company != "all":
        conditions.append("po.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(po.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if po:
        conditions.append("po.name LIKE %(po_name)s")
        values["po_name"] = po

    if supplier:
        conditions.append("po.supplier LIKE %(supplier)s")
        values["supplier"] = supplier

    if so:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabPurchase Order Item` AS poi 
                WHERE poi.parent = po.name 
                AND poi.sales_order = %(so)s
                ) """)
        values["so"] = so

    where = " AND ".join(conditions)

    return frappe.db.sql("""
       SELECT
            po.name AS po_name,
            po.custom_customer_po_no AS customer_po,
            po.supplier AS supplier,
            po.rounded_total AS value,
            po.transaction_date AS start_date,
            po.schedule_date AS est_completion,
            po.currency
        FROM
            `tabPurchase Order` AS po
        INNER JOIN `tabPurchase Order Item` AS poi ON
            poi.parent = po.name
            AND poi.custom_po_line_item_tracking_status = "Under Production"
        WHERE
            {where}
        GROUP BY
            poi.parent
    """.format(where=where), values, as_dict=True)



# ═══════════════════════════════════════════════════════════════════════════════
#  SHIPMENTS TAB - PENDING AWAITING FF
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_awaiting_ff(company=None, from_date=None, to_date=None,
                    so=None, party=None):
 
    conditions = [
        " docstatus < 2",
        "si.custom_ro LIKE 'FF AWAITED'"
    ]
    values = {}

    if company and company != "all":
        conditions.append("si.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(si.posting_date) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if so:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabSales Invoice Item` AS sii 
                WHERE sii.parent = si.name 
                AND sii.sales_order = %(so)s
                ) """)
        values["so"] = so

    if party:
        conditions.append("si.customer LIKE %(party)s")
        values["party"] = party

    where = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT
            si.name AS invoice_no,
            si.po_no AS customer_po_no,
            si.customer AS party_name,
            si.rounded_total AS amount,
            si.custom_material_readiness_date AS packed_date,
            si.currency
        FROM
            `tabSales Invoice` AS si
        WHERE
            {where}
    """.format(where=where), values, as_dict=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SHIPMENTS TAB - SEA SHIPMENTS TABLE
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_sea_shipments(company=None, from_date=None, to_date=None,
                        so=None, party=None):
    
    conditions = [
        "si.docstatus < 2",
        "si.mode_of_transport = 'Ship'"
    ]
    values = {}

    if company and company != "all":
        conditions.append("si.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(si.posting_date) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if so:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabSales Invoice Item` AS sii 
                WHERE sii.parent = si.name 
                AND sii.sales_order = %(so)s
                ) """)
        values["so"] = so

    if party:
        conditions.append("si.customer LIKE %(party)s")
        values["party"] = party

    where = " AND ".join(conditions)

    # SQL QUERY ─────────────────────────────────────────────────────────────────
    return frappe.db.sql("""
        SELECT
            si.name AS invoice_no,
            si.customer AS party_name,
            si.custom_airway_bill AS airway_bill,
            si.rounded_total AS amount,
            si.custom_delivery_date AS delivery_date,
            si.currency
        FROM
            `tabSales Invoice` AS si
        WHERE {where}
    """.format(where=where), values, as_dict=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SHIPMENTS TAB - AIR SHIPMENTS TABLE
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_air_shipments(company=None, from_date=None, to_date=None,
                        so=None, party=None):

    conditions = [
        "si.docstatus < 2",
        "si.mode_of_transport = 'Air'"
    ]
    values = {}

    if company and company != "all":
        conditions.append("si.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(si.posting_date) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if so:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabSales Invoice Item` AS sii 
                WHERE sii.parent = si.name 
                AND sii.sales_order = %(so)s
                ) """)
        values["so"] = so

    if party:
        conditions.append("si.customer LIKE %(party)s")
        values["party"] = party

    where = " AND ".join(conditions)
    # SQL QUERY ─────────────────────────────────────────────────────────────────
    return frappe.db.sql("""
        SELECT
            si.name AS invoice_no,
            si.customer AS party_name,
            si.custom_airway_bill AS airway_bill,
            si.rounded_total AS amount,
            si.custom_delivery_date AS delivery_date,
            si.currency
        FROM
            `tabSales Invoice` AS si
        WHERE {where}   
    """.format(where=where), values, as_dict=True)







# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 11 — AR COLLECTIONS TAB
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_ar_collection_kpis(company=None, from_date=None, to_date=None):
    from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute
    
    """
    Summary KPI cards for AR Collections tab.
    """

    conditions = ["si.docstatus = 1"]
    values = {}

    if company and company != "all":
        # conditions.append("si.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)
  
    # if from_date:
    #     conditions.append("si.posting_date >= %(from_date)s")
    #     values["from_date"] = from_date

    if to_date:
        # conditions.append("si.posting_date <= %(to_date)s")
        values["report_date"] = to_date

    where = " AND ".join(conditions)

    report_data = execute(values)[1]
    # print(values ,"-------valuess")
    # print(report_data, "===report_data=====")

    total_pending_collection = 0
    total_invoiced = 0
    total_paid_collection = 0
    total_acc_receivable = 0

    payment_collection_data = []
    pending_collection_data = []
    if len(report_data) > 0:
        for row in report_data:
            total_pending_collection = total_pending_collection + (row.outstanding or 0)
            total_invoiced = total_invoiced + (row.invoiced or 0)
            
            if row.voucher_type == "Sales Invoice":
                # print(row.paid, "====row.paid=====")
                total_paid_collection = total_paid_collection + (row.paid or 0)
                total_acc_receivable = total_acc_receivable + (row.outstanding or 0)
                # print(row.paid , "===row.paid====", row.outstanding, "====row.outstanding====")
                if row.paid and row.paid > 0:
                    # print(row.paid, "====row.paid===")
                    payment_collection_data.append({
                        "order_no": row.voucher_no,
                        "party_name": row.party,
                        "currency": row.account_currency,
                        "value": row.paid,
                    })

                if row.outstanding and row.outstanding > 0:
                    # print(row.outstanding, "=====row.outstanding====")
                    pending_collection_data.append({
                        "order_no": row.voucher_no,
                        "party_name": row.party,
                        "currency": row.account_currency,
                        "value": row.outstanding,
                    })

    currency = "USD"
    if company:
        currency = frappe.db.get_value("Company", company, "default_currency")

    # print(total_paid_collection, "=======total_paid_collection=====")
    ar_data = {
        "total_pending_collection" : flt((total_pending_collection), 2) or 0,
        "total_invoiced" : flt((total_invoiced), 2),
        "total_paid_collection" : flt((total_paid_collection), 2),
        "total_acc_receivable" : flt((total_acc_receivable), 2),
        "payment_collection_data": payment_collection_data,
        "pending_collection_data": pending_collection_data,
        "currency": currency
    }

    return ar_data


@frappe.whitelist()
def get_ar_collection_details(company=None, from_date=None, to_date=None):
    ar_data = get_ar_collection_kpis(company, from_date, to_date)
    # print(ar_data, "=====", type(ar_data))
    # print(ar_data.get("payment_collection_data"), "------get_ar_collection_details---------")
    return ar_data["payment_collection_data"] or []


@frappe.whitelist()
def get_pending_collections(company=None, from_date=None, to_date=None):
    ar_data = get_ar_collection_kpis(company, from_date, to_date)
    # print(ar_data.get("pending_collection_data"), "-------------pending_collection_data-------")
    return ar_data["pending_collection_data"] or []



# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 15 — INTERCOMPANY TRANSACTIONS TAB
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_intercompany_transactions(company=None, so=None, from_date=None, to_date=None, party=None, po=None):
    """
    DocType: Sales Order - Is Intercompany Transaction? = Yes

    """
    conditions = ["so.docstatus < 2", "so.custom_is_intercompany_transaction = 1"]
    values = {}

    if company and company != "all":
        conditions.append("so.company = %(company)s")
        values["company"] = COMPANY_MAP.get(company, company)

    if from_date and to_date:
        if to_date >= from_date:
            conditions.append("DATE(so.creation) between %(from_date)s AND %(to_date)s")
            values["from_date"] = from_date
            values["to_date"] = to_date
        else:
            frappe.throw(_("To Date should be greater then From Date"))

    if so:
        conditions.append("so.name LIKE %(so_name)s")
        values["so_name"] = so

    if party:
        conditions.append("so.customer LIKE %(party)s")
        values["party"] = party

    if po:
        conditions.append("""
            EXISTS (
                SELECT 1 
                FROM `tabPurchase Order Item` AS poi 
                WHERE poi.sales_order = so.name AND poi.parent = %(po)s
                ) """)
        values["po"] = po

    where = " AND ".join(conditions)

    # SQL QUERY ─────────────────────────────────────────────────────────────────
    return frappe.db.sql("""
        SELECT 
            so.name AS so_name,
            COALESCE(so.po_no, so.name ) AS so_number,
            so.company ,
            so.customer,
            so.rounded_total AS so_value,
            so.currency 
        FROM `tabSales Order` AS so 
        WHERE {where}
    """.format(where=where), values, as_dict=True, debug=1)


