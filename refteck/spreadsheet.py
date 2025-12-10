import json
import frappe
import gspread
from frappe.utils import cstr
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from refteck.api import get_connected_qo, get_sq_details
from frappe.integrations.google_oauth import GoogleOAuth
from gspread_formatting import cellFormat, textFormat, format_cell_range, Border, Borders, Color, set_column_width

class GoogleOAuthSpreadsheets(GoogleOAuth):
    """
    Override GoogleOAuth as it does not include sheets service
    The google project needs to have Drive and Sheets service enabled
    """
    def __init__(self, validate: bool = True):
        self.google_settings = frappe.get_single("Google Settings")
        self.domain = ('sheets', 'v4')
        self.scopes = "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive"

    def get_google_service_object(self, access_token: str, refresh_token: str):
        """Returns google service object"""

        credentials_dict = {
            "token": access_token,
            "refresh_token": refresh_token,
            "token_uri": self.OAUTH_URL,
            "client_id": self.google_settings.client_id,
            "client_secret": self.google_settings.get_password(
                fieldname="client_secret", raise_exception=False
            ),
            "scopes": self.scopes,
        }
        
        return build(
            serviceName=self.domain[0],
            version=self.domain[1],
            credentials=Credentials(**credentials_dict),
            static_discovery=False,
        )

class GSpreadsheet():
    def __init__(self):
        self.account = frappe.get_doc("Google Drive")

        self.oauth_obj = GoogleOAuthSpreadsheets()

        # spreadsheets service
        self.spreadsheet_service = self.oauth_obj.get_google_service_object(
            self.account.get_access_token(),
            self.account.get_password(
                fieldname="indexing_refresh_token", raise_exception=False),
        )

        # drive service
        self.drive_oauth_obj = GoogleOAuth("drive")
        self.drive_service = self.drive_oauth_obj.get_google_service_object(
            self.account.get_access_token(),
            self.account.get_password(
                fieldname="indexing_refresh_token", raise_exception=False),
        )

    def create_sheet(self, title, data=[], folder_id=None, share_with=""):
        """
            Create a new Google Spreadsheet, optionally insert data, move it into a specific folder,
            and share it with a user.
            Args:
                title (str): The title of the new Google Sheet.
                data (list, optional): A 2D list representing rows and columns to insert into the sheet.
                                    Example: [['Name', 'Email'], [
                                        'Alice', 'alice@example.com']]
                folder_id (str, optional): The ID of the Google Drive folder to place the new sheet in.
                                        If not provided, the sheet will be created in the root directory.
                share_with (str, optional): semi-colon seperated Email address to share the sheet with. If provided, the sheet
                                            will be shared with edit access.
            Returns:
                dict: A dictionary containing 'spreadsheetId' and 'spreadsheetUrl' of the created sheet.
            Raises:
                Google API errors via HttpError if creation, data insertion, or sharing fails.
            Example:
                gsheet = GSpreadsheet()
                gsheet.create_sheet(
                    title="Team Contacts",
                    data=[["Name", "Phone"], ["John", "12345"]],
                    folder_id="abc123folderid",
                    share_with="teammate@example.com"
                )
            """
        spreadsheet_body = {
            'properties': {
                'title': title
            }
        }

        spreadsheet = self.spreadsheet_service.spreadsheets().create(body=spreadsheet_body,fields='spreadsheetId,spreadsheetUrl').execute()
        range_name = "Sheet1!A1"
        body = {"values": data}
        self.spreadsheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet["spreadsheetId"],
            range=range_name,
            valueInputOption="RAW",
            body=body,
        ).execute()

        if folder_id:
            self.drive_service.files().update(
                fileId=spreadsheet["spreadsheetId"],
                addParents=folder_id,
                removeParents='root',
                fields='id, parents'
            ).execute()

        if share_with:
            if isinstance(share_with, str):
                share_with = share_with.split(";")
            credentials = frappe.db.get_single_value("Google Spreadsheet Account", "credentials")
            credentials = json.loads(credentials)
            share_with.append(credentials['client_email'])  
           
            def callback(request_id, response, exception):
                if exception:
                    frappe.log_error(
                        title="Export to Sheets:Drive share error.", message=cstr(exception)
                    )

            batch = self.drive_service.new_batch_http_request(
                callback=callback)

            for email in share_with:
                user_permission = {"type": "user",
                                   "role": "writer", "emailAddress": email}
                batch.add(
                    self.drive_service.permissions().create(
                        fileId=spreadsheet["spreadsheetId"],
                        body=user_permission,
                        fields="id",
                    )
                )
            public_permission = {
                "type": "anyone",
                "role": "writer"
            }
            batch.add(
                self.drive_service.permissions().create(
                    fileId=spreadsheet["spreadsheetId"],
                    body=public_permission,
                    fields="id",
                )
            )
            batch.execute()

        return spreadsheet

@frappe.whitelist()
def save_to_sheets(doc, share_with):
    doc = frappe.parse_json(doc)
    operating_gp_checklist_data = []
    title = f"{doc.name} - Operating GP Checklist Created on {frappe.utils.nowdate()}"
    google_spreadsheet = {}
   
    try:
        doc_fields = frappe.get_meta(doc.doctype).fields
        operating_gp_checklist_index = None
       
        for field in doc_fields:
            if field.fieldtype == "Tab Break" and field.label == "Operating GP checklist":
                operating_gp_checklist_index = field.idx
                break
        for field in doc_fields[operating_gp_checklist_index:]:
            if field.fieldtype == "Tab Break":
                break
            elif field.fieldtype in ["Section Break", "Column Break"]:
                continue
            elif field.fieldtype == "Table":
                if field.fieldname == "custom_generated_spreadsheet_urls":
                    continue
                if len(doc.get(field.fieldname)) > 0:
                    operating_gp_checklist_data.append([])
                    operating_gp_checklist_data.append([field.label])
                    headers = []
                    for ctfield in frappe.get_meta(field.options).fields:
                        headers.append(ctfield.label)
                    operating_gp_checklist_data.append(headers)
                    for row in doc.get(field.fieldname):
                        row_data = []
                        for ctfield in frappe.get_meta(field.options).fields:
                            row_data.append(row.get(ctfield.fieldname))
                        operating_gp_checklist_data.append(row_data)
            else:
                d = [field.label, doc.get(field.fieldname)]
                operating_gp_checklist_data.append(d)
        
        gsheet = GSpreadsheet()
        google_spreadsheet = gsheet.create_sheet(
            title=title,
            data=operating_gp_checklist_data,
            share_with=share_with,  
        )
        google_spreadsheet['title'] = title

        document = frappe.get_doc(doc.doctype, doc.name)
        document.append("custom_generated_spreadsheet_urls", {
            "spreadsheet_url" : google_spreadsheet['spreadsheetUrl'],
            "creation_date" : frappe.utils.today(),
        })
        document.save(ignore_permissions=True)
    except Exception as ex:
        frappe.throw("SpreadSheet can not be saved to sheets. {0}".format(ex))
    try:
        format_spreadsheet(google_spreadsheet)
    except Exception as ex:
        frappe.throw("SpreadSheet formatting failed. {0}".format(ex))
    return google_spreadsheet

@frappe.whitelist()
def save_quotation_details_to_sheets(doc, share_with):
    google_spreadsheet = {}
    admin_checklist_data = []
    doc = frappe.parse_json(doc)
    title = f"{doc.name} - Admin Checklist Created on {frappe.utils.nowdate()}"

    try:
        doc_fields = frappe.get_meta(doc.doctype).fields
        admin_checklist_index = None
        
        """ 
        Find the index of "Admin Checklist" tab break 
        """
        for field in doc_fields:
            if field.fieldtype == "Tab Break" and field.label == "Admin Checklist":
                admin_checklist_index = field.idx
                break
        
        """
        Collect data of "Admin Checklist" tab untill next tab break.
        """
        
        for field in doc_fields[admin_checklist_index:]:
            if field.fieldtype == "Tab Break":
                break
            elif field.fieldtype in ["Section Break", "Column Break"]:
                continue
            elif field.fieldtype == "HTML":
                if field.fieldname == "custom_sq_details":
                    get_connnected_supplier_quotation_details(doc, admin_checklist_data)

                if field.fieldname == "custom_previous_quotation_details":
                    connected_qo_details = get_previous_quotation_details(doc.name)
                    if connected_qo_details:
                        admin_checklist_data.append(["Previous Quotation Details"])
                        for qo in connected_qo_details:
                            admin_checklist_data.append(qo)

            elif field.fieldtype == "Table":
                if field.fieldname == "custom_generated_spreadsheet_urls":
                    continue

                admin_checklist_data.append([field.label])
                headers = []
                for ctfield in frappe.get_meta(field.options).fields:
                    headers.append(ctfield.label)
                admin_checklist_data.append(headers)
                for row in doc.get(field.fieldname):
                    row_data = []
                    for ctfield in frappe.get_meta(field.options).fields:
                        row_data.append(row.get(ctfield.fieldname))
                    admin_checklist_data.append(row_data)
            else:
                d = [field.label, doc.get(field.fieldname)]
                admin_checklist_data.append(d)

        gsheet = GSpreadsheet()
        google_spreadsheet = gsheet.create_sheet(
            title=title,
            data=admin_checklist_data,
            share_with=share_with,  
        )
        google_spreadsheet['title'] = title
     
        document = frappe.get_doc(doc.doctype, doc.name)
        document.append("custom_generated_spreadsheet_urls", {
            "spreadsheet_url" : google_spreadsheet['spreadsheetUrl'],
            "creation_date" : frappe.utils.today(),
        })
        document.save(ignore_permissions=True)
    except Exception as ex:
        frappe.throw("SpreadSheet can not be saved to sheets. {}".format(ex))
    try:
        format_spreadsheet(google_spreadsheet)
    except Exception as ex:
        frappe.throw("SpreadSheet formatting failed. {0}".format(ex))
    return google_spreadsheet

def get_connnected_supplier_quotation_details(doc, admin_checklist_data):
    connected_sq_list, supplier_name_list, payment_terms_list, currency_list, actual_lead_time_list, notes_list, reviewed_by_list, procurement_representative_list, total_weight_list, sq_ref_list = get_sq_details(doc, method=None)
    admin_checklist_data.append(["Connected Supplier Quotation"])
    admin_checklist_data.append(["Supplier Quotation", connected_sq_list[0] if len(connected_sq_list) > 0 else ""])
    admin_checklist_data.append(["Supplier", supplier_name_list[0] if len(supplier_name_list) > 0 else ""])
    admin_checklist_data.append(["Payment Terms", payment_terms_list[0] if len(payment_terms_list) > 0 else ""])
    admin_checklist_data.append(["Currency", currency_list[0] if len(currency_list) > 0 else ""])
    admin_checklist_data.append(["Actual Lead Time", actual_lead_time_list[0] if len(actual_lead_time_list) > 0 else ""])
    admin_checklist_data.append(["Total Weight", total_weight_list[0] if len(total_weight_list) > 0 else ""])
    admin_checklist_data.append(["Notes", notes_list[0] if len(notes_list) > 0 else ""])
    admin_checklist_data.append(["Supplier Quotation Reviewed By", reviewed_by_list[0] if len(reviewed_by_list) > 0 else ""])
    admin_checklist_data.append(["Procurement Representative", procurement_representative_list[0] if len(procurement_representative_list) > 0 else ""])

def get_previous_quotation_details(name):
    connected_qo_details = get_connected_qo(name)
    if len(connected_qo_details) > 0:
        previous_qo = connected_qo_details[0]
        doc = frappe.get_doc("Quotation", previous_qo)
        qo_data = [
            ["SAP CODE", "UOM", "QTY", "SQ price", "Buying Value", "Offer Price without freight", "Other Charges", "Offer Price with charges", "Offer Value with Charges", "Material Margin", "Margin"],
        ]
        
        for margin in doc.custom_margin_calculation:
            row = [
                margin.sap_code,
                margin.uom,
                margin.qty,
                margin.sq_price,
                margin.buying_value,
                margin.offer_price_without_freight,
                margin.other_charges,
                margin.offer_price_with_charges,
                margin.offer_value_with_charges,
                margin.material_margin,
                margin.margin,
            ]
            qo_data.append(row)
        
        qo_data.append(["Charge Type", "Supplier Quotation Charges", "Offer Charges"])
        for charges in doc.custom_other_charges_comparison:
            row = [
                charges.charge_type,
                charges.supplier_quotation_charges,
                charges.offer_charges,
            ]
            qo_data.append(row)

        qo_data.append(["Total SQ Other Charges", doc.custom_total_sq_other_charges])
        qo_data.append(["Final Buying Value", doc.custom_final_values])
        qo_data.append(["Final Margin", doc.custom_final_margin])
        qo_data.append(["Total Offer Other Charges", doc.custom_total_offer_other_charges])
        qo_data.append(["Final Offer Value", doc.custom_final_offer_values])
        qo_data.append(["Overall Margin", round(doc.custom_overall_margin, 2)])

        return qo_data
    
def format_spreadsheet(google_spreadsheet):
    credentials = frappe.db.get_single_value("Google Spreadsheet Account", "credentials")
    credentials = json.loads(credentials)

    gc = gspread.service_account_from_dict(credentials)
    sh = gc.open(google_spreadsheet['title'])
    worksheet = sh.sheet1
    all_data = worksheet.get_all_values()

    # Format Column Width As Per MaxCharacters in Column
    for i in range(1, len(all_data[0]) + 1):
        new_column_length = max(len(cell) for cell in worksheet.col_values(i))
        new_column_letter = chr(ord('A') + i - 1)
        if new_column_length > 0:
            set_column_width(worksheet, new_column_letter, round(new_column_length*8.2))


    """ Bold and align left the first label column before the table """
    fmt = cellFormat(
        textFormat=textFormat(bold=True),
        horizontalAlignment='LEFT'
    )

    """ Define table rows count + Bold and align left table """
    border_style = Borders(
        top=Border(style='SOLID', width=1, color=Color(0, 0, 0)),
        bottom=Border(style='SOLID', width=1, color=Color(0, 0, 0)),
        left=Border(style='SOLID', width=1, color=Color(0, 0, 0)),
        right=Border(style='SOLID', width=1, color=Color(0, 0, 0)),
    )

    table_format = cellFormat(
        borders=border_style,
        horizontalAlignment='LEFT',
    )
    
    for i in range(len(all_data)):
        length = len(worksheet.row_values(i+1))
        if length == 1:
            format_cell_range(worksheet, f'A{i+1}', fmt)        
        elif length == 2:
            format_cell_range(worksheet, f'A{i+1}', fmt)
        elif length > 2:
            last_col = chr(ord('A') + length - 1)
            format_cell_range(worksheet, f'A{i+1}:{last_col}{i+1}', table_format)

    