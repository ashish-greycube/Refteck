frappe.ui.form.on("Sales Order", {
    // onload_post_render: function(frm){
    //     console.log("Sales Order Refreshed")
    //     set_operation_gp_checklist_fields_value(frm)
    // },
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.docstatus == 0 && frm.doc.items.length > 0) {
            frm.add_custom_button(__('Allocate Grade'), () => select_brand_wise_grade(frm));
        }
        if (frm.doc.docstatus != 2) {
            frm.add_custom_button(__('Save to Sheets'), () => {
                save_to_sheets(frm);
            }, "Create")
        }
    },
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

let select_brand_wise_grade = function(frm){
    let dialog = undefined
    let table_fields = [
        {
            fieldtype: "Link",
            fieldname: "brand",
            options: "Brand",
            label: __("Brand"),
            read_only: 1,
            in_list_view: 1,
        },
        {
            fieldtype: "Select",
            fieldname: "grade",
            options: ["New", "Existing"],
            label: __("Grade"),
            read_only: 0,
            reqd: 1,
            in_list_view: 1,
        },
    ]

    let dialog_fields = [
        {
            label: "Brand Wise Grade",
            fieldname: "brand_wise_grade",
            fieldtype: "Table",
            cannot_add_rows: true,
            cannot_delete_rows: true,
            in_place_edit: false,
            reqd: 1,
            data: get_unique_brands(frm),
            fields: table_fields,
        }
    ]

    dialog = new frappe.ui.Dialog({
        title: __("Set Brand Wise Grade"),
        fields: dialog_fields,
        primary_action_label: 'Set Grade',
        primary_action: function (values) {
            // console.log("------values", values)
            let brand_data = values.brand_wise_grade
            if (brand_data.length > 0) {
                frm.doc.items.forEach(item => {
                    for (const b of brand_data) {
                        if (item.brand === b.brand && b.grade){
                            frappe.model.set_value(item.doctype, item.name, "custom_grade", b.grade)
                        }
                    }
                    
                });
                frm.refresh_field("items");
                frm.save()
            }
            dialog.hide()
        }
    })
    dialog.show()
}

let get_unique_brands = function(frm){
    let unique_brands = []
    frm.doc.items.forEach(item => {
        const findBrand = unique_brands.find((obj) => obj.brand === item.brand);
        if (!findBrand) {
            unique_brands.push({ "brand": item.brand })
        }
    });
    return unique_brands
}

function save_to_sheets(frm) {
    let dlg = new frappe.ui.Dialog({
        title: __("Share Permissions"),
        fields: [
            {
                label: "Emails to share with",
                fieldname: "share_with",
                fieldtype: "Data",
                reqd: 1,
                default: frappe.session.user_email,
                description: "Use ';' to separate multiple emails.",
            },
        ],
        primary_action: function () {
            frappe.call({
                method: "refteck.spreadsheet.save_to_sheets",
                args: {
                    doc : frm.doc,
                    share_with: dlg.get_value("share_with"),
                },
                freeze: true,
                freeze_message: "Please wait while the sheet is created",
                callback: (r) => {
                    dlg.hide();
                    frappe.msgprint(
                        __("Created <a href='{}' target='_blank'>{}</a>, shared with {}", [
                            r.message.spreadsheetUrl,
                            r.message.title,
                            dlg.get_value("share_with"),
                        ]),
                        __("Created Spreadsheet.")
                    );
                },
            });
        },
    });
    dlg.show();
}