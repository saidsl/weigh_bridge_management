# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from weigh_bridge_management.utilities.driverlist import load_drivers

class Vehicle(Document):

	def onload(self):

		dlist = load_drivers(self.wb_vehicle_registration)

		
		self.get("__onload").driver_list = dlist

	# def fetch_driver_info(self, driverdocname):

	# 	frappe.msgprint(driverdocname)

	# 	dr = frappe.get_doc("Driver", driverdocname)

	# 	return dr