frappe.ui.form.on("Opportunity", {
    before_save: async function (frm) {
        if (frm.is_new() && frm.doc.items.length > 0) {
            await select_brand_wise_sourcing_person(frm)
        }
    },
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.docstatus == 0 && frm.doc.items.length > 0) {
            frm.add_custom_button(__('Allocate SP'), () => select_brand_wise_sourcing_person(frm));
            frm.add_custom_button(__('Allocate Brand'), () => allocate_brand(frm));
        };
        if (!frm.is_new()){
            frm.add_custom_button(__('Share with Assignees'), () => share_with_assignees(frm));
        }
    },
    // onload_post_render: function (frm) {
    //     share_opportunity_doc_to_assignees(frm)
    // }
})

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

let select_brand_wise_sourcing_person = async function (frm) {
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
            fieldtype: "Link",
            fieldname: "sourcing_person",
            options: "User",
            label: __("Sourcing Person"),
            read_only: 0,
            reqd: 1,
            in_list_view: 1,
        },
    ]

    let dialog_fields = [
        {
            label: "Brand Wise Sourcing Person",
            fieldname: "brand_wise_sourcing_person",
            fieldtype: "Table",
            cannot_add_rows: true,
            cannot_delete_rows: true,
            in_place_edit: false,
            reqd: 1,
            data: get_unique_brands(frm),
            fields: table_fields,
        }
    ]

    let promise = new Promise((resolve, reject) => {
        frappe.dom.unfreeze()
        if (!frm.is_new()) {
            resolve()
        }
        dialog = new frappe.ui.Dialog({
            title: __("Set Brand Wise Sourcing Person"),
            fields: dialog_fields,
            primary_action_label: 'Set Sourcing Person',
            primary_action: function (values) {
                // console.log("------values", values)
                let brand_data = values.brand_wise_sourcing_person
                if (brand_data.length > 0) {
                    frm.doc.items.forEach(item => {
                        for (const b of brand_data) {
                            if (item.brand === b.brand && b.sourcing_person) {
                                frappe.model.set_value(item.doctype, item.name, "custom_sourcing_person", b.sourcing_person)
                            }
                        }

                    });
                    frm.refresh_field("items");
                    frm.save()
                }
                dialog.hide()
                resolve()
            }
        })
    })

    dialog.show()

    await promise.then(() => '');
}

let get_unique_brands = function(frm){
    let unique_brands = []
    frm.doc.items.forEach(item => {
        const findBrand =
            unique_brands.find((obj) => obj.brand === item.brand);
        if (!findBrand) {
            unique_brands.push({ "brand": item.brand })
        }
    });
    return unique_brands
}

let allocate_brand = function(frm){
    let selected_items = frm.get_field("items").grid.get_selected_children();
    if (selected_items.length > 0) {
        let dialog = new frappe.ui.Dialog({
            title: __("Allocate Brand"),
            fields: [{
                fieldtype: "Link",
                fieldname: "brand",
                options: "Brand",
                label: __("Brand"),
                read_only: 0,
                reqd: 1,
            }],
            primary_action_label: "Allocate",
            primary_action: function (values) {
                // console.log(values, "===========values===")
                if (values.brand){
                    selected_items.forEach(item => {
                        frappe.model.set_value(item.doctype, item.name, "brand", values.brand)
                    });
                    frm.refresh_field("items");
                    frm.save()
                }
                dialog.hide()

            }
        })
        dialog.show()


    }
    else {
        frappe.show_alert("Please Select Items", 3);
    }
    // console.log(selected_items, "===========")  
}

let share_with_assignees = function (frm) {
    frappe.call({
        method: "refteck.api.share_opportunity_doc_to_assignees",
        args: {
            doctype: frm.doc.doctype,
            docname: frm.doc.name
        },
        callback: function (res) {
            frm.reload_doc();
        }
    })
}

let share_opportunity_doc_to_assignees = function(frm){
    $(".add-assignment-btn").on("click", function () {
        setTimeout(() => {
            let dialog = frappe.ui.open_dialogs[0];
            if (dialog) {
                dialog.set_primary_action(__('Add'), function () {
                    const values = dialog.get_values();
                    if (!values) return;

                    // the original assignment logic (server call)
                    frappe.call({
                        method: 'frappe.desk.form.assign_to.add',
                        args: {
                            doctype: frm.doctype,
                            name: frm.docname,
                            assign_to: values.assign_to,
                            description: values.description,
                            date: values.date,
                            priority: values.priority
                        },
                        callback: function (r) {
                            dialog.hide();
                            //CUSTOM LOGIC: After assignment, share the document with the new assignee
                            frappe.call({
                                method: "refteck.api.share_opportunity_doc_to_assignees",
                                args: {
                                    doctype: frm.doc.doctype,
                                    docname: frm.doc.name
                                },
                                callback: function (res) {
                                    frm.reload_doc();
                                }
                            })
                        }
                    });
                })
            }
        }, 500);


        // console.log("Assignment Button Clicked")
        //  $("div.modal-dialog div.modal-content div.modal-footer div.standard-actions button.btn-primary").on("click", function(){
        // setTimeout(() => {
        //     console.log("Button Clicked")
        // }, 500);
        // })
    })

}