frappe.ui.form.on("Opportunity Item", {
    custom_item_status: function(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        frm.doc.items.forEach((item) => {
            if(row.custom_sourcing_person === item.custom_sourcing_person && row.brand === item.brand && row.name !== item.name){
                frappe.model.set_value(item.doctype, item.name, "custom_item_status", row.custom_item_status)
            }
        })
    }
})