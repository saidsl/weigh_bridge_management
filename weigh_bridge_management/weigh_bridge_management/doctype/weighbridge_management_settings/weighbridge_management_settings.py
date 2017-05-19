# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class wbmWeighbridgeManagementSettings(Document):
	def validate(self):
		self.validate_warehouses()
		self.validate_repeating_companies()
	
	def validate_repeating_companies(self):
		"""Error when Same Company is entered multiple times in warehouses"""
		wh_list = []
		for entry in self.warehouses:
			wh_list.append(entry.company)

		if len(wh_list)!= len(set(wh_list)):
			frappe.throw(_("Same Company is entered more than once"))

	def validate_warehouses(self):
		for entry in self.warehouses:
			"""Error when Company of Warehouse doesn't match with Company Selected"""
			if frappe.db.get_value("Warehouse", entry.warehouse, "company") != entry.company:
				frappe.throw(_("Warehouse does not match with Company"))


@frappe.whitelist()
def get_wb_settings(company):
	"""Return for Company - income_account, receivable_account, payable_account, tax_account and cost_center"""
	out = {
		"warehouse" : frappe.db.get_value("Weighbridge Management Settings Warehouse",
		{
			"company": company
		}, "warehouse")
	}

	if not out["warehouse"]:
		frappe.throw(_("Set default Warehouse in Weighbridge Management Settings"))

	return out
