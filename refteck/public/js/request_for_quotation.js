frappe.ui.form.on("Request for Quotation", {
    set_warehouse_cf: function (frm) {
        for(let i = 0; i<frm.doc.items.length; i++){
            frm.doc.items[i].warehouse = frm.doc.set_warehouse_cf 
        }
        refresh_field("items"); 
        frappe.show_alert('Item Warehouse is set in all row of item table', 5);
    }
})