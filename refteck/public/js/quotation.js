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

frappe.ui.form.on("Margin Calculation RT", {
    offer_price_without_freight:function(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        let offer_price_with_charges = (row.offer_price_without_freight || 0) + (row.other_charges || 0)
        frappe.model.set_value(cdt, cdn, "offer_price_with_charges", offer_price_with_charges);
    },
    other_charges:function(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        let offer_price_with_charges = (row.offer_price_without_freight || 0) + (row.other_charges || 0)
        frappe.model.set_value(cdt, cdn, "offer_price_with_charges", offer_price_with_charges);
    },
    offer_price_with_charges:function (frm, cdt, cdn) {
        console.log("offer_price_with_charges")
        let row = locals[cdt][cdn]
        if(row.sap_code){
            frm.doc.items.forEach((item) => {
                if (item.item_code === row.sap_code && item.name === row.qo_item_ref) {
                    let old_rate = item.rate
                    frappe.model.set_value(item.doctype, item.name, "rate", row.offer_price_with_charges);
                    frappe.show_alert({
                        message:__('Row {0}: In Item table, Rate {1} changed to {2}', [item.idx, old_rate, item.rate]),
                        indicator:'green'
                    }, 5);
                }
            });
        }
    }
})

frappe.ui.form.on("Other Charges Comparison", {
    before_custom_other_charges_comparison_remove: function(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        if (row.name) {
            var tbl = frm.doc.taxes || [];
            var i = tbl.length;
            while (i--) {
                if (tbl[i].custom_admin_checklist_other_charges_reference == row.name) {
                    cur_frm.get_field("taxes").grid.grid_rows[i].remove();
                }
            }
            cur_frm.refresh();
        }
    }
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