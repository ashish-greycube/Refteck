frappe.ui.form.on("Sales Order", {
    // onload_post_render: function(frm){
    //     console.log("Sales Order Refreshed")
    //     set_operation_gp_checklist_fields_value(frm)
    // },
    po_no: function(frm){
        frm.set_value('custom_sales_order_no', frm.doc.po_no)
    },
    transaction_date: function(frm){
        frm.set_value('custom_so_received_date', frm.doc.transaction_date)
    },
    contact_display: function(frm){
        frm.set_value('custom_buyer', frm.doc.contact_display)
    },
    total: function(frm){
        // console.log("inside total")
        frm.set_value('custom_so_basic_value', frm.doc.total)
    },
    custom_ld_applicable: function(frm){
        frm.set_value('custom_ld', frm.doc.custom_ld_applicable)
    }
})

let set_operation_gp_checklist_fields_value = function(frm){
    console.log("inside function")
    if(frm.doc.po_no){
        frm.set_value('custom_sales_order_no', frm.doc.po_no)
    }
    if(frm.doc.po_date){
        frm.set_value('custom_so_received_date', frm.doc.transaction_date)
    }
    if(frm.doc.contact_display){
        frm.set_value('custom_sales_order_no', frm.doc.po_no)
    }
    if(frm.doc.total){
        frm.set_value('custom_so_basic_value', frm.doc.total)
    }
    if(frm.doc.custom_ld_applicable){
        frm.set_value('custom_ld', frm.doc.custom_ld_applicable)
    }
}