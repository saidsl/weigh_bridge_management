# Copyright (c) 2013, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}
    
	columns = get_columns(filters)
	entries = get_entries(filters)
	data = []
	total_wbt_net_weight = 0.0

	# To find Total of net weight at the end of report.
	for d in entries:
		total_wbt_net_weight += (d.wbt_net_weight)

		data.append([
			d.csname, d.name, d.wbt_vehicle, d.workflow_state, d.wbt_net_weight
		])

	if data:
		total_row = [""]*len(data[0])
		total_row[0] = _("Total")
		total_row[-1] = total_wbt_net_weight
		data.append(total_row)

	return columns, data

#Display Column row from Wieghbridge Ticket Report.
def get_columns(filters):
	if not filters.get("doc_type"):
		msgprint(_("Please select the document type first"), raise_exception=1)

	return [filters["doc_type"] + ":Link/" + filters["doc_type"] + ":140",
		_("Weighbridge Ticket") + ":Link/Weighbridge Ticket:140",
		_("Vehicle") + ":Link/Vehicle:140",
		_("State") + ":Link/DocType:140",
		_("Net Weight") + ":Float:140"]

#Display Data in  Wieghbridge Ticket Report.
def get_entries(filters):
	# doc_field = filters["doc_type"] == 'Customer'
	# conditions, values = get_conditions(filters, doc_field)
	entries = frappe.db.sql("""
		select
			cs.name AS csname, wt.name, wt.wbt_vehicle, wt.workflow_state, wt.wbt_net_weight 
		from 
			`tab%s` cs, `tabWeighbridge Ticket` wt 
		where  
			wt.workflow_state = 'Weighing Complete'
			AND (cs.name = wt.customer OR cs.name = wt.supplier);
		""" %(filters["doc_type"]), as_dict=1)

	return entries

# Start Wrok Here-- after break
# def get_conditions(filters, doc_field):
# 	conditions = [""]
#  	values = []

#  	for field in ["Supplier", "Customer"]:
# 		if filters.get(field):
#  			conditions.append("wt.{0}=%s".format(field))
#  			values.append(filters[field])
#  	return " and ".join(conditions), values
