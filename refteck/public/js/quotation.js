frappe.ui.form.on("Quotation", {
    onload(frm) {
        draw_html(frm)

    },
    refresh(frm) {
        draw_html(frm)

    },
    setup(frm) {
        draw_html(frm)

    },    
})


function draw_html(frm) {
    if (
        frm.fields_dict["custom_previous_quotation_details"] &&
        frm.is_new() == undefined &&
        frm.doc.__onload && "custom_html_data" in frm.doc.__onload
    ) {
        frm.set_df_property('custom_previous_quotation_details', 'options', frm.doc.__onload.custom_html_data)
        frm.refresh_field('custom_previous_quotation_details')
    }else{
        frm.set_df_property('custom_previous_quotation_details', 'options', "<div><div>")
        frm.refresh_field('custom_previous_quotation_details')         
    }
    if (
        frm.fields_dict["custom_sq_details"] &&
        frm.doc.custom_margin_calculation.length>0 &&
        frm.doc.__onload && "custom_sq_html_data" in frm.doc.__onload
    ) {
        frm.set_df_property('custom_sq_details', 'options', frm.doc.__onload.custom_sq_html_data)
        frm.refresh_field('custom_sq_details')
       
    }else{
        frm.set_df_property('custom_sq_details', 'options', '<div><div>')
        frm.refresh_field('custom_sq_details')
    }   
}