frappe.ui.form.on("Supplier Quotation", {
    setup: function (frm) {
        frm.set_query("set_warehouse_cf", function () {
            return {
                filters: {
                    company: frm.doc.company
                },
            };
        })
    },

    //------- L2 ----------- 
    custom_quote_value_l2: function(frm){
        calculate_total_quote_value_for_l2(frm)
    },
    custom_freight_l2: function(frm){
        calculate_total_quote_value_for_l2(frm)
    },
    custom_packing_l2: function(frm){
        calculate_total_quote_value_for_l2(frm)
    },
    custom_other_charges_l2: function(frm){
        calculate_total_quote_value_for_l2(frm)
    },
    custom_discount_l2: function(frm){
        calculate_total_quote_value_for_l2(frm)
    },
    custom_total_quote_value_l2: function(frm){
        calculate_value_in_usd_for_l2(frm)
    },

    //------- L3 ----------- 
    custom_quote_value_l3: function(frm){
        calculate_total_quote_value_for_l3(frm)
    },
    custom_freight_l3: function(frm){
        calculate_total_quote_value_for_l3(frm)
    },
    custom__packing_l3: function(frm){
        calculate_total_quote_value_for_l3(frm)
    },
    custom_other_charges_l3: function(frm){
        calculate_total_quote_value_for_l3(frm)
    },
    custom_discount_l3: function(frm){
        calculate_total_quote_value_for_l3(frm)
    },
    custom_total_quote_value_l3: function(frm){
        calculate_value_in_usd_for_l3(frm)
    },


    //------- L4 ----------- 
    custom_quote_value_l4: function(frm){
        calculate_total_quote_value_for_l4(frm)
    },
    custom_freight_l4: function(frm){
        calculate_total_quote_value_for_l4(frm)
    },
    custom__packing_l4: function(frm){
        calculate_total_quote_value_for_l4(frm)
    },
    custom_other_charges_l4: function(frm){
        calculate_total_quote_value_for_l4(frm)
    },
    custom_discount_l4: function(frm){
        calculate_total_quote_value_for_l4(frm)
    },
    custom_total_quote_value_l4: function(frm){
        calculate_value_in_usd_for_l4(frm)
    },

    //------- L5 -----------
    custom_quote_value_l5: function(frm){
        calculate_total_quote_value_for_l5(frm)
    },
    custom_freight_l5: function(frm){
        calculate_total_quote_value_for_l5(frm)
    },
    custom__packing_5: function(frm){
        calculate_total_quote_value_for_l5(frm)
    },
    custom_other_charges_l5: function(frm){
        calculate_total_quote_value_for_l5(frm)
    },
    custom_discount_l5: function(frm){
        calculate_total_quote_value_for_l5(frm)
    },
    custom_total_quote_value_l5: function(frm){
        calculate_value_in_usd_for_l5(frm)
    },

})

////////// L2 /////////////

let calculate_total_quote_value_for_l2 = function (frm) {
    let total_value = ((frm.doc.custom_quote_value_l2 || 0) + (frm.doc.custom_freight_l2 || 0)
        + (frm.doc.custom_packing_l2 || 0) + (frm.doc.custom_other_charges_l2 || 0)
        - (frm.doc.custom_discount_l2 || 0))

    frm.set_value('custom_total_quote_value_l2', total_value)
}

let calculate_value_in_usd_for_l2 = function (frm) {
    if(frm.doc.custom_currency_l2){
        frappe.db.get_list('Custom Currency Exchange', {
            fields: ['exchange_rate'],
            filters: {
                from_currency: frm.doc.custom_currency_l2,
                to_currency: 'USD',
                date: ['<=', frm.doc.transaction_date]
            },
            order_by: 'date DESC', limit: 1
        }).then(value => {
            // console.log(value[0].exchange_rate);
            if (value.length > 0) {
                let exchange_rate = value[0].exchange_rate;

                let value_in_usd = (frm.doc.custom_total_quote_value_l2 || 0) * (exchange_rate || 0);
                frm.set_value('custom_vbc_l2', value_in_usd)
            }
    
        })
    }
}


////////// L3 /////////////

let calculate_total_quote_value_for_l3 = function (frm) {
    let total_value = ((frm.doc.custom_quote_value_l3 || 0) + (frm.doc.custom_freight_l3 || 0)
        + (frm.doc.custom__packing_l3 || 0) + (frm.doc.custom_other_charges_l3 || 0)
        - (frm.doc.custom_discount_l3 || 0))

    frm.set_value('custom_total_quote_value_l3', total_value)
}

let calculate_value_in_usd_for_l3 = function (frm) {
    if(frm.doc.custom_currency_l3){
        frappe.db.get_list('Custom Currency Exchange', {
            fields: ['exchange_rate'],
            filters: {
                from_currency: frm.doc.custom_currency_l3,
                to_currency: 'USD',
                date: ['<=', frm.doc.transaction_date]
            },
            order_by: 'date DESC', limit: 1
        }).then(value => {
            // console.log(value[0].exchange_rate);
            if (value.length > 0) {
                let exchange_rate = value[0].exchange_rate;

                let value_in_usd = (frm.doc.custom_total_quote_value_l3 || 0) * (exchange_rate || 0);
                frm.set_value('custom_vbc_l3', value_in_usd)
            }
    
        })
    }
}


////////// L4 /////////////

let calculate_total_quote_value_for_l4 = function (frm) {
    let total_value = ((frm.doc.custom_quote_value_l4 || 0) + (frm.doc.custom_freight_l4 || 0)
        + (frm.doc.custom__packing_l4 || 0) + (frm.doc.custom_other_charges_l4 || 0)
        - (frm.doc.custom_discount_l4 || 0))

    frm.set_value('custom_total_quote_value_l4', total_value)
}

let calculate_value_in_usd_for_l4 = function (frm) {
    if(frm.doc.custom_currency_l4){
        frappe.db.get_list('Custom Currency Exchange', {
            fields: ['exchange_rate'],
            filters: {
                from_currency: frm.doc.custom_currency_l4,
                to_currency: 'USD',
                date: ['<=', frm.doc.transaction_date]
            },
            order_by: 'date DESC', limit: 1
        }).then(value => {
            // console.log(value[0].exchange_rate);

            if (value.length > 0) {
                let exchange_rate = value[0].exchange_rate;
    
                let value_in_usd = (frm.doc.custom_total_quote_value_l4 || 0) * (exchange_rate || 0);
                frm.set_value('custom_vbc_l4', value_in_usd)
            }
    
        })
    }
}

////////// L5 /////////////

let calculate_total_quote_value_for_l5 = function (frm) {
    let total_value = ((frm.doc.custom_quote_value_l5 || 0) + (frm.doc.custom_freight_l5 || 0)
        + (frm.doc.custom__packing_5 || 0) + (frm.doc.custom_other_charges_l5 || 0)
        - (frm.doc.custom_discount_l5 || 0))

    frm.set_value('custom_total_quote_value_l5', total_value)
}

let calculate_value_in_usd_for_l5 = function (frm) {
    if(frm.doc.custom_currency_l5){
        frappe.db.get_list('Custom Currency Exchange', {
            fields: ['exchange_rate'],
            filters: {
                from_currency: frm.doc.custom_currency_l5,
                to_currency: 'USD',
                date: ['<=', frm.doc.transaction_date]
            },
            order_by: 'date DESC', limit: 1
        }).then(value => {
            // console.log(value[0].exchange_rate);
            if (value.length > 0) {
                let exchange_rate = value[0].exchange_rate;
    
                let value_in_usd = (frm.doc.custom_total_quote_value_l5 || 0) * (exchange_rate || 0);
                frm.set_value('custom_vbc_l5', value_in_usd)
            }
        })
    }
}