// These fields are saved in IST, so show and save them without timezone conversion
frappe.provide("refteck");

if (!refteck.checkin_time_in_ist) {
	refteck.checkin_time_in_ist = true;

	const TIME_ZONE = "Asia/Kolkata";
	const IST_FIELDS = {
		"Employee Checkin": [
			"time",
			"shift_start",
			"shift_end",
			"shift_actual_start",
			"shift_actual_end",
		],
		Attendance: ["in_time", "out_time"],
	};

	const is_ist_field = (df) => Boolean(IST_FIELDS[df?.parent]?.includes(df.fieldname));

	const format_as_saved = (value) => {
		if (!value) return "";
		const date_format = frappe.datetime.get_user_date_fmt().toUpperCase();
		const time_format = frappe.datetime.get_user_time_fmt();
		return moment(value, frappe.defaultDatetimeFormat).format(`${date_format} ${time_format}`);
	};

	// List, report view and read-only fields
	const default_formatter = frappe.form.formatters.Datetime;
	frappe.form.formatters.Datetime = function (value, df, ...args) {
		if (is_ist_field(df)) return format_as_saved(value);
		return default_formatter.call(this, value, df, ...args);
	};

	// Editable fields
	frappe.ui.form.ControlDatetime = class extends frappe.ui.form.ControlDatetime {
		format_for_input(value) {
			return is_ist_field(this.df) ? format_as_saved(value) : super.format_for_input(value);
		}

		parse(value) {
			if (!value || !is_ist_field(this.df)) return super.parse(value);
			value = this.eval_expression(value, "datetime");
			return value === "Invalid date" ? "" : value;
		}

		get_now_date() {
			if (!is_ist_field(this.df)) return super.get_now_date();
			return frappe.datetime.moment_to_date_obj(moment.tz(TIME_ZONE));
		}

		get_start_date() {
			if (!is_ist_field(this.df)) return super.get_start_date();
			return this.value ? frappe.datetime.str_to_obj(this.value) : this.get_now_date();
		}

		get_user_time_zone() {
			return is_ist_field(this.df) ? TIME_ZONE : super.get_user_time_zone();
		}
	};

	// Frappe's default "Now" is system time (GMT)
	frappe.ui.form.on("Employee Checkin", {
		onload(frm) {
			if (!frm.is_new()) return;
			frm.set_value("time", moment.tz(TIME_ZONE).format(frappe.defaultDatetimeFormat));
		},
	});
}
