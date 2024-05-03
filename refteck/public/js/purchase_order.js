frappe.ui.form.on("Purchase Order", {
    onload_post_render: function (frm) {
        frm.set_query("supplier", function () {
            return {
                filters: {
                    is_approved_for_purchase_cf: 1,
                },
            };
        });
    },
    refresh: function (frm) {
        frm.set_query("supplier", function () {
            return {
                filters: {
                    is_approved_for_purchase_cf: 1,
                },
            };
        });
    },
})