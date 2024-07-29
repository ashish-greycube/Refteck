frappe.ui.form.on("Quotation", {
    onload(frm) {
        if (
            frm.fields_dict["custom_previous_quotation_details_"] &&
            frm.is_new() == undefined &&
            frm.doc.__onload && "custom_html_data" in frm.doc.__onload
        ) {
            frm.set_df_property('custom_previous_quotation_details_', 'options', frm.doc.__onload.custom_html_data)
        }
    }
})