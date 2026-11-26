from frappe.utils.data import get_datetime_in_timezone

CHECKIN_TIME_ZONE = "Asia/Kolkata"
TIME_PERMLEVEL = 1


def set_checkin_time_in_ist(doc, method=None):
	if not doc.is_new() or doc.flags.ignore_permissions:
		return

	# HR and the biometric API user can write Time, so keep the time they sent
	if TIME_PERMLEVEL in doc.get_permlevel_access():
		return

	# Frappe resets Time to system time (GMT) for other users
	doc.time = get_datetime_in_timezone(CHECKIN_TIME_ZONE).replace(tzinfo=None, microsecond=0)
