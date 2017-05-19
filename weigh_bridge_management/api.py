import frappe
from frappe import _
from frappe.desk.moduleview import get

@frappe.whitelist()
def wbmget(module):
	out = get(module)

	data = out["data"]
	custom_reports = dict(data[len(data) - 1]) #Since list of Custom Reports is appended at the end.

	if (module == "Selling") or (module == "Buying"):
		if (custom_reports['label'] == "Custom Reports"):
			custom_reports['items'].append(
				{'is_query_report': 1, 'type': 'report', 'doctype': 'Weighbridge Ticket', 'name': 'Sales Order and Purchase Order', 'label': 'Sales Order and Purchase Order'} 
			)
		else:
			data.append(
				{'items': [
						{'is_query_report': 1, 'type': 'report', 'doctype': 'Weighbridge Ticket', 'name': 'Sales Order and Purchase Order', 'label': 'Sales Order and Purchase Order'} 
			 		], 'label': 'Custom Reports', 'icon': 'icon-list'
		 		}
			)

	return out
