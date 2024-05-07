frappe.ui.form.on("Supplier Quotation", {
    setup:function(frm){
        frm.set_query("set_warehouse_cf", function(){
            return {
                filters: {
                    company: frm.doc.company
                },
            };
        })
    }
})