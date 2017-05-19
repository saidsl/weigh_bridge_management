# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document



class Driver(Document):
	def validate(self):
		self.validate_licence_number()

	def validate_licence_number(self):
		if self.wb_driver_licence: 
			if len(self.wb_driver_licence) < 12:
				frappe.throw(_("License Number must have 12 digits."))

	def before_save(self):
		#Set full name
		self.full_name = self.wb_driver_fn + ((' ' + self.wb_driver_ln) if self.wb_driver_ln else '')