frappe.ui.form.on("Request for Quotation", {
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