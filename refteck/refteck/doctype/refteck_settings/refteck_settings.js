// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Refteck Settings", {
	frequency(frm) {
        let today_date = frappe.datetime.nowdate()
        let day = (frappe.datetime.str_to_obj(today_date)).getDate()
        let month = (frappe.datetime.str_to_obj(today_date)).getMonth() + 1
        let year = moment(new Date()).year();
        console.log(day, month, year)
        if (frm.doc.frequency == "Weekly"){
            if (day <= 15){
                let new_date =__("{0}-{1}-15",[year,month])
                console.log(new_date)
                frm.set_value("next_date",new_date)
            }else{
                let new_date =__("{0}-{1}-15",[year,month])
            }
        }
        else if (frm.doc.frequency == "Fortnightly"){

        }
	},
});
    