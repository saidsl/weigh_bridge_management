# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe import utils
from frappe.utils import add_days, nowdate
from weigh_bridge_management.weigh_bridge_management.doctype.weighbridge_management_settings.weighbridge_management_settings import get_wb_settings

class WeighbridgeTicket(Document):
	def validate(self):
		self.validate_basic()
		self.validate_outgoing()
		self.validate_incoming()
		self.validate_items()

	#When Vehicle is Empty and loaded at WeighBridge.  calculate net_weight = Tare Weight - Gross Weight.
	def validate_outgoing(self):
		if self.wbt_load_direction=="Outgoing":
			tolerance = (1.0*float(self.wbt_vehicle_tare_weight)/100)*10
			if not self.wbt_first_weighing <= (tolerance+float(self.wbt_vehicle_tare_weight)):
				frappe.throw(_("Tare Weight mismatch"))

			if not self.wbt_first_weighing >= (float(self.wbt_vehicle_tare_weight)-tolerance):
				frappe.throw(_("Tare Weight mismatch"))

	#Gross Weight and tare weight validation.			
	def validate_weight(self):
		if self.wbt_load_direction=="Outgoing":
			if (self.wbt_first_weighing > self.wbt_second_weighing):
				frappe.throw(_("Second Weigh Weight. i.e Gross Weight can not be less than tare weight."))	

		if self.wbt_load_direction=="Incoming":
			if (self.wbt_first_weighing < self.wbt_second_weighing):
				frappe.throw(_("First Weigh Weight. i.e Gross Weight can not be less than tare weight."))		
	
	#When Vehicle is loaded and unload at WeighBridge. calculate net_weight = Gross Weight — Tare Weight.		
	def validate_incoming(self):
		if self.wbt_load_direction=="Incoming" and self.workflow_state == "Second Weighing" and self.wbt_second_weighing:

			#frappe.msgprint("%s, %s" % (self.wbt_load_direction, self.workflow_state))

			tolerance =  (1.0*float(self.wbt_vehicle_tare_weight)/100)*10
			if not self.wbt_second_weighing <= (tolerance+float(self.wbt_vehicle_tare_weight)):
				frappe.throw(_("Tare Weight mismatch"))
	
			if not self.wbt_second_weighing >= (float(self.wbt_vehicle_tare_weight)-tolerance):
				frappe.throw(_("Tare Weight mismatch"))

	def validate_basic(self):
		if (self.party_type == "Customer") and not self.customer:
			frappe.throw(_("Customer not selected."))
		elif (self.party_type == "Supplier") and not self.supplier:
			frappe.throw(_("Supplier not selected."))

		if (not self.wbt_first_weighing) or (self.wbt_first_weighing == 0.0):
			frappe.throw(_("First weighing cannot be left blank or zero."))

	def validate_items(self):
		item_list = []
		for itm in self.items:
			if itm.item_type == "Item":
				item_list.append(itm.item_type)
				if not itm.item:
					frappe.throw(_("Items Table ROW # {0} Please select Item".format(itm.idx)))
			elif itm.item_type == "Charge":
				if not itm.account:
					frappe.throw(_("Items Table ROW # {0} Please select Account".format(itm.idx)))
				elif not itm.description:
					frappe.throw(_("Items Table ROW # {0} Please fill in Description".format(itm.idx)))
				elif not itm.rate or itm.rate <= 0:
					frappe.throw(_("Items Table ROW # {0} Please enter valid rate".format(itm.idx)))


		#WBT must have at least one items
		if len(item_list) == 0:
		 	frappe.throw(_("Weighbridge Ticket must have at least one item."))	

		#WBT cannot have more than one item.
		if len(item_list)!= len(set(item_list)):
			frappe.throw(_("Weighbridge Ticket cannot have more than one item."))


	# #When Vehicle is loaded and unload at WeighBridge. calculate net_weight = Gross Weight — Tare Weight.		
	# def validate_incoming(self):
	# 	if self.wbt_load_direction=="Incoming":
	# 		tolerance =  (1.0*float(self.wbt_vehicle_tare_weight)/100)*10
	# 		if not self.wbt_second_weighing <= (tolerance+float(self.wbt_vehicle_tare_weight)):
	# 			frappe.throw(_("Tare Weight MisMatch"))
	
	# 		if not self.wbt_second_weighing >= (float(self.wbt_vehicle_tare_weight)-tolerance):
	# 			frappe.throw(_("Tare Weight MisMatch"))


	#Create Customer order and sales order automatically once Weighing is Complete.
	# def before_update_after_submit(self):
	# 	self.net_weight = abs(self.wbt_first_weighing - self.wbt_second_weighing)

	def on_update_after_submit(self):
		if self.workflow_state == "Weighing Complete":
			#Validate doesnt seem to fire after submitting.
			if ((not self.wbt_second_weighing) or (self.wbt_second_weighing <= 0.0)):
				frappe.throw(_("Second weighing cannot be left blank or zero."))



#SALES DOCS ------


# @frappe.whitelist()
# def create_sales_docs(docname):
# 	so = None

# 	soname = frappe.db.get_value("Sales Order", {"weighbridge_ticket":docname}, "name")

# 	if soname:
# 		frappe.msgprint(_("Sales Order '%s' already created against this Weighbridge Ticket" % (soname)))			
# 	else:
# 		so = create_so(docname)

# 	if so:
# 		dnname = frappe.db.get_value("Delivery Note", {"weighbridge_ticket":docname}, "name")

# 		if dnname:
# 			frappe.msgprint(_("Delivery Note '%s' already created against this Weighbridge Ticket." % (dnname)))
# 		else:
# 			dn = create_dn_for_so(docname, so)

# @frappe.whitelist()
# def create_purchase_docs(docname=None):
# 	po = None

# 	poname = frappe.db.get_value("Purchase Order", {"weighbridge_ticket":docname}, "name")

# 	if poname:
# 		frappe.msgprint(_("Purchase Order '%s' already created against this Weighbridge Ticket" % (poname)))			
# 	else:
# 		po = create_po(docname)

# 	if po:
# 		prname =  frappe.db.get_value("Purchase Receipt", {"weighbridge_ticket":docname}, "name")

# 		if prname:
# 			frappe.msgprint(_("Purchase Receipt '%s' already created against this Weighbridge Ticket." % (prname)))
# 		else:
# 			pr = create_pr_for_po(docname, po)
	
#HELPERS		
def create_so(wbtname=None):
	wbt = loadwbt(wbtname)
	#wbt = None

	# try:
	# 	wbt = frappe.get_doc("Weighbridge Ticket", wbtname)
	# except Exception, e:
	# 	frappe.throw(_("Weighbridge Ticket '%s' could not be loaded." % (wbtname)))

	#Create a sales order if customer is selected.
	so = frappe.new_doc("Sales Order")	
	so.transaction_date = frappe.utils.today()

	so.company = wbt.company
	so.customer = wbt.customer
	so.delivery_date = add_days(so.transaction_date, 10)
	so.currency = wbt.company_currency
	
	so.selling_price_list = "Standard Selling" 
	so.weighbridge_ticket = wbtname

	#frappe.msgprint(so.weighbridge_ticket)
	if so.weighbridge_ticket == "": 
		frappe.throw("WBT was not set for SO")

	#Get Warehouse from WB_Settings
	# wbms = get_wb_settings(wbt.company)
	# if not wbms:
	# 	frappe.throw("Please ensure Weighbridge Management Settings has valid data.")
	# wh = wbms["warehouse"]

	wh = get_warehouse_from_items(wbt)  #get warehouse from item

	item_price = None

	for itm in wbt.items:

		if itm.item_type == "Item":

			item_price = frappe.db.get_value("Item Price",
					{	"price_list": wbt.selling_price_list,
						"item_code": itm.item
					}, 	"price_list_rate")

			if (not item_price) or (item_price == 0.0):
				frappe.throw(_("Please set price for item '%s' in Price List '%s'" % (itm.item, wbt.selling_price_list)))
	 
	
			so.append("items", {
				"item_code": itm.item,
				"warehouse": wh,
				"qty": wbt.wbt_net_weight,
				"rate": item_price,
				"conversion_factor": 1.0
			})	
		
		elif itm.item_type == "Charge":

			so.append("taxes", {
				"charge_type": "Actual",
				"account_head": itm.account,
				"description": itm.description,
				"tax_amount": itm.rate
			})

	try:
		so.save()
	except Exception, e:
		frappe.throw(_("Sales Order was not submitted. <br/> %s" % (e)))
	else:
		frappe.msgprint(_("Sales Order %s created successfully." % (so.name)))

	return so

def create_dn_for_so(wbtname, so):
	from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
	dn = make_delivery_note(so.name)
	dn.weighbridge_ticket = wbtname

	dn.save()
	frappe.db.commit()
	frappe.msgprint(_("Delivery Note %s created successfully." % (dn.name)))

	return dn

def create_si_for_so(wbtname, so):
	from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
	si = make_sales_invoice(so.name)
	si.weighbridge_ticket = wbtname

	si.save()
	frappe.db.commit()
	frappe.msgprint(_("Sales Invoice %s created successfully." % (si.name)))

	return si
			
def create_po(wbtname):
	wbt = loadwbt(wbtname)
	# wbt = None

	# try:
	# 	wbt = frappe.get_doc("Weighbridge Ticket", wbtname)
	# except Exception, e:
	# 	frappe.throw(_("Weighbridge Ticket '%s' could not be loaded." % (wbtname)))
	
	po = frappe.new_doc("Purchase Order")
	po.transaction_date = frappe.utils.today()

	po.company = wbt.company
	po.supplier = wbt.supplier
	po.is_subcontracted = "No"
	po.conversion_factor = 1
	po.weighbridge_ticket = wbtname

	#Get Warehouse from WB_Settings
	# wbms = get_wb_settings(wbt.company)
	# if not wbms:
	# 	frappe.throw("Please ensure Weighbridge Management Settings has valid data.")
	# wh = wbms["warehouse"]


	wh = get_warehouse_from_items(wbt) # Get warehouse from item

	item_price = None

	for itm in wbt.items:

		if itm.item_type == "Item":

			#Fetch item price to append in PO items
			item_price = frappe.db.get_value("Item Price",
					{
						"price_list": wbt.buying_price_list,
						"item_code": itm.item
					}, "price_list_rate")

			if (not item_price) or (item_price == 0.0):
				frappe.throw(_("Please set price for item '%s' in Price List '%s'" % (itm.item, wbt.buying_price_list)))
		
			po.append("items", {
				"item_code": itm.item,
				"warehouse": wh,
				"qty": wbt.wbt_net_weight,
				"rate": item_price,
				"schedule_date": add_days(nowdate(), 1)
			})

		elif itm.item_type == "Charge":
			po.append("taxes", {
				"charge_type": "Actual",
				"account_head": itm.account,
				"description": itm.description,
				"tax_amount": itm.rate
			})

	try:
		po.save()
	except Exception, e:
		frappe.throw(_("Purchase Order was not submitted. <br/> %s" % (e)))
	else:
		frappe.msgprint(_("Purchase Order %s created successfully." % (po.name)))

	return po
	
def create_pr_for_po(wbtname, po):
	from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
	pr = make_purchase_receipt(po.name)
	pr.weighbridge_ticket = wbtname

	pr.save()
	frappe.db.commit()
	frappe.msgprint(_("Purchase Receipt %s created successfully." % (pr.name)))

	return pr

def create_pi_for_po(wbtname, po):
	from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice
	pi = make_purchase_invoice(po.name)
	pi.weighbridge_ticket = wbtname

	pi.save()
	frappe.db.commit()
	frappe.msgprint(_("Purchase Invoice %s created successfully." % (pi.name)))

	return pi

#~HELPERS

#Sales Docs
#Returns SO against WBT if found. If not found, SO is created and returned.
@frappe.whitelist()
def check_create_so(wbtname):
	so = None

	soname = frappe.db.get_value("Sales Order", {"weighbridge_ticket":wbtname}, "name")

	if soname:
		so = frappe.get_doc("Sales Order", soname)
		frappe.msgprint(_("Sales Order '%s' already created against this Weighbridge Ticket" % (soname)))			
	else:
		so = create_so(wbtname)

	return so

@frappe.whitelist()
def check_create_dn(wbtname=None):
	dnname = frappe.db.get_value("Delivery Note", {"weighbridge_ticket":wbtname}, "name")

	if dnname:
		frappe.msgprint(_("Delivery Note '%s' already created against this Weighbridge Ticket." % (dnname)))
	else:
		dn = create_dn_without_so(wbtname)

@frappe.whitelist()
def check_create_si(wbtname=None):

	siname = frappe.db.get_value("Sales Invoice", {"weighbridge_ticket":wbtname}, "name")

	if siname:
		frappe.msgprint(_("Sales Invoice '%s' already created against this Weighbridge Ticket." % (siname)))
	else:
		si = create_si_without_so(wbtname)
			
#DEPRECATED : 160703

# @frappe.whitelist()
# def check_create_dn(wbtname=None):
# 	so = check_create_so(wbtname)

# 	if so:
# 		dnname = frappe.db.get_value("Delivery Note", {"weighbridge_ticket":wbtname}, "name")

# 		if dnname:
# 			frappe.msgprint(_("Delivery Note '%s' already created against this Weighbridge Ticket." % (dnname)))
# 		else:
# 			dn = create_dn_for_so(wbtname, so)
# 			#dn = create_dn_without_so(wbtname)

# @frappe.whitelist()
# def check_create_si(wbtname=None):
# 	so = check_create_so(wbtname)

# 	if so:
# 		siname = frappe.db.get_value("Sales Invoice", {"weighbridge_ticket":wbtname}, "name")

# 		if siname:
# 			frappe.msgprint(_("Sales Invoice '%s' already created against this Weighbridge Ticket." % (siname)))
# 		else:
# 			si = create_si_for_so(wbtname, so)	
# 			#si = create_si_without_so(wbt)


def create_dn_without_so(wbtname=None):
	wbt = loadwbt(wbtname)

	dn = frappe.new_doc("Delivery Note")
	
	dn.posting_date = frappe.utils.today()
	
	dn.company = wbt.company
	dn.currency = wbt.company_currency
	dn.customer = wbt.customer

	dn.weighbridge_ticket = wbtname
	#Get Warehouse from WB_Settings

	# wbms = get_wb_settings(wbt.company)
	# if not wbms:
	# 	frappe.throw("Please ensure Weighbridge Management Settings has valid data.")
	# wh = wbms["warehouse"]

	wh = get_warehouse_from_items(wbt) #Get warehouse form item

	item_price = None

	for itm in wbt.items:
		if itm.item_type == "Item":

			item_price = frappe.db.get_value("Item Price",
					{	"price_list": wbt.selling_price_list,
						"item_code": itm.item
					}, 	"price_list_rate")

			if (not item_price) or (item_price == 0.0):
				frappe.throw(_("Please set price for item '%s' in Price List '%s'" % (itm.item, wbt.selling_price_list)))
	 
	
			dn.append("items", {
				"item_code": itm.item,
				"warehouse": wh,
				"qty": wbt.wbt_net_weight,
				"rate": item_price,
				"conversion_factor": 1.0
			})	
			#not included: Expense Account, Cost Center, Target Warehouse, Conversion Factor
		
		elif itm.item_type == "Charge":

			dn.append("taxes", {
				"charge_type": "Actual",
				"account_head": itm.account,
				"description": itm.description,
				"tax_amount": itm.rate
			})

	try:
		dn.save()
	except Exception, e:
		frappe.throw(_("Delivery Note was not submitted. <br/> %s" % (e)))
	else:
		frappe.msgprint(_("Delivery Note '%s' created successfully." % (dn.name)))

	return dn

def create_si_without_so(wbtname=None):
	#frappe.msgprint("Create SI Without SO")
	wbt = loadwbt(wbtname)

	si = frappe.new_doc("Sales Invoice")
	
	si.posting_date = frappe.utils.today()
	
	si.company = wbt.company
	si.currency = wbt.company_currency
	si.customer = wbt.customer

	si.weighbridge_ticket  = wbtname

	#Get Warehouse from WB_Settings
	# wbms = get_wb_settings(wbt.company)
	# if not wbms:
	# 	frappe.throw("Please ensure Weighbridge Management Settings has valid data.")
	# wh = wbms["warehouse"]

	wh = get_warehouse_from_items(wbt) #Get warehouse form item

	item_price = None

	for itm in wbt.items:
		if itm.item_type == "Item":

			item_price = frappe.db.get_value("Item Price",
					{	"price_list": wbt.selling_price_list,
						"item_code": itm.item
					}, 	"price_list_rate")

			if (not item_price) or (item_price == 0.0):
				frappe.throw(_("Please set price for item '%s' in Price List '%s'" % (itm.item, wbt.selling_price_list)))
	 
	
			si.append("items", {
				"item_code": itm.item,
				"warehouse": wh,
				"qty": wbt.wbt_net_weight,
				"rate": item_price,
				"conversion_factor": 1.0
			})	
			#not included: Expense Account, Cost Center, Target Warehouse, Conversion Factor
		
		elif itm.item_type == "Charge":

			si.append("taxes", {
				"charge_type": "Actual",
				"account_head": itm.account,
				"description": itm.description,
				"tax_amount": itm.rate
			})
	try:
		si.save()
	except Exception, e:
		frappe.throw(_("Sales Invoice was not submitted. <br/> %s" % (e)))
	else:
		frappe.msgprint(_("Sales Invoice '%s' created successfully." % (si.name)))

	return si

#~SALES DOCS

#PURCHASE

@frappe.whitelist()
def check_create_po(wbtname):
	po = None

	poname = frappe.db.get_value("Purchase Order", {"weighbridge_ticket":wbtname}, "name")

	if poname:
		po = frappe.get_doc("Purchase Order", poname)
		frappe.msgprint(_("Purchase Order '%s' already created against this Weighbridge Ticket" % (poname)))			
	else:
		po = create_po(wbtname)

	return po

@frappe.whitelist()
def check_create_pr(wbtname=None):
	prname = frappe.db.get_value("Purchase Receipt", {"weighbridge_ticket":wbtname}, "name")

	if prname:
		frappe.msgprint(_("Purchase Receipt '%s' already created against this Weighbridge Ticket." % (prname)))
	else:
		#frappe.msgprint(prname)
		pr = create_pr_without_po(wbtname)

@frappe.whitelist()
def check_create_pi(wbtname=None):
	piname = frappe.db.get_value("Purchase Invoice", {"weighbridge_ticket":wbtname}, "name")

	if piname:
		frappe.msgprint(_("Purchase Invoice '%s' already created against this Weighbridge Ticket." % (piname)))
	else:
		pi = create_pi_without_po(wbtname)

#DEPRECATED: 160703
# @frappe.whitelist()
# def check_create_pr(wbtname=None):
# 	po = check_create_po(wbtname)

# 	if po:
# 		prname = frappe.db.get_value("Purchase Receipt", {"weighbridge_ticket":wbtname}, "name")

# 		if prname:
# 			frappe.msgprint(_("Purchase Receipt '%s' already created against this Weighbridge Ticket." % (prname)))
# 		else:
# 			pr = create_pr_for_po(wbtname, po) Replace with Create PR without PO: 160703
# 			#pr = create_pr_without_po(wbtname)

# @frappe.whitelist()
# def check_create_pi(wbtname=None):
# 	po = check_create_po(wbtname)

# 	if po:
# 		piname = frappe.db.get_value("Purchase Invoice", {"weighbridge_ticket":wbtname}, "name")

# 		if piname:
# 			frappe.msgprint(_("Purchase Invoice '%s' already created against this Weighbridge Ticket." % (piname)))
# 		else:
# 			pi = create_pi_for_po(wbtname, po)
# 			#pi = create_pi_without_po(wbtn)


def create_pr_without_po(wbtname=None):
	wbt = loadwbt(wbtname)
	# wbt = None

	# try:
	# 	wbt = frappe.get_doc("Weighbridge Ticket", wbtname)
	# except Exception, e:
	# 	frappe.throw(_("Weighbridge Ticket '%s' could not be loaded." % (wbtname)))


	pr = frappe.new_doc("Purchase Receipt")
	pr.posting_date = frappe.utils.today()
	pr.posting_time = frappe.utils.today()
	pr.company = wbt.company

	# wbms = get_wb_settings(wbt.company)
	# if not wbms:
	# 	frappe.throw("Please ensure Weighbridge Management Settings has valid data.")
	# wh = wbms["warehouse"]

	wh = get_warehouse_from_items(wbt)   # Get warehouse from item
	pr.supplier_warehouse = wh
	pr.currency = wbt.company_currency
	pr.supplier = wbt.supplier

	pr.weighbridge_ticket = wbtname

	item_price = None

	for itm in wbt.items:

		if itm.item_type == "Item":

			#Fetch item price to append in PO items
			item_price = frappe.db.get_value("Item Price",
					{
						"price_list": wbt.buying_price_list,
						"item_code": itm.item
					}, "price_list_rate")

			if (not item_price) or (item_price == 0.0):
				frappe.throw(_("Please set price for item '%s' in Price List '%s'" % (itm.item, wbt.buying_price_list)))
		
			pr.append("items", {
				"item_code": itm.item,
				"warehouse": wh,
				"qty": wbt.wbt_net_weight,
				"received_qty": wbt.wbt_net_weight,
				"rate": item_price
			})

		elif itm.item_type == "Charge":
			pr.append("taxes", {
				"charge_type": "Actual",
				"account_head": itm.account,
				"description": itm.description,
				"tax_amount": itm.rate
			})

	try:
		pr.save()
	except Exception, e:
		frappe.throw(_("Purchase Receipt was not created. <br/> %s" % (e)))
	else:
		frappe.msgprint(_("Purchase Receipt '%s' created successfully." % (pr.name)))
	
	return pr

def create_pi_without_po(wbtname=None):
	wbt = loadwbt(wbtname)
	# wbt = None

	# try:
	# 	wbt = frappe.get_doc("Weighbridge Ticket", wbtname)
	# except Exception, e:
	# 	frappe.throw(_("Weighbridge Ticket '%s' could not be loaded." % (wbtname)))

	pi = frappe.new_doc("Purchase Invoice")
	
	pi.posting_date = frappe.utils.today()
	pi.posting_time = frappe.utils.today()
	pi.company = wbt.company

	# wbms = get_wb_settings(wbt.company)
	# if not wbms:
	# 	frappe.throw("Please ensure Weighbridge Management Settings has valid data.")
	# wh = wbms["warehouse"]

	wh = get_warehouse_from_items(wbt)    # Get warehouse from item

	pi.supplier_warehouse = wh
	pi.currency = wbt.company_currency 
	pi.supplier = wbt.supplier
	pi.conversion_rate = 1
	
	pi.weighbridge_ticket = wbtname

	item_price = None

	for itm in wbt.items:

		if itm.item_type == "Item":
			#Fetch PR against WBT to link in item, in case Buying Settings > Purchase Receipt Required = Yes
			prname = frappe.db.get_value("Purchase Receipt", {"weighbridge_ticket":wbtname}, "name")
			if not prname:
				frappe.throw(_("Please create Purchase Receipt before making Purchase Invoice"))

			#Fetch item price to append in PO items
			item_price = frappe.db.get_value("Item Price",
					{
						"price_list": wbt.buying_price_list,
						"item_code": itm.item
					}, "price_list_rate")

			if (not item_price) or (item_price == 0.0):
				frappe.throw(_("Please set price for item '%s' in Price List '%s'" % (itm.item, wbt.buying_price_list)))
		
			pi.append("items", {
				"item_code": itm.item,
				"warehouse": wh,
				"qty": wbt.wbt_net_weight,
				"rate": item_price,
				"purchase_receipt": prname
			})
			#missing: serial_no, cost_center, project.
		elif itm.item_type == "Charge":
			pi.append("taxes", {
				"charge_type": "Actual",
				"account_head": itm.account,
				"description": itm.description,
				"tax_amount": itm.rate
			})
	try:
		pi.save()
	except Exception, e:
		frappe.throw(_("Purchase Invoice was not created. <br/> %s" % (e)))
	else:
		frappe.msgprint(_("Purchase Invoice '%s' created successfully." % (pi.name)))

	return pi

#~PURCHASE


def loadwbt(wbtname=None):
	wbt = None

	try:
		wbt = frappe.get_doc("Weighbridge Ticket", wbtname)
	except Exception, e:
		frappe.throw(_("Weighbridge Ticket '%s' could not be loaded." % (wbtname)))

	return wbt

def get_warehouse_from_items(wbt):
	getticketitem = frappe.get_all("Weighbridge Ticket Item",fields = ["*"],filters = {"parent":wbt.name,"item_type":"Item"})
	itm = frappe.get_doc("Item",getticketitem[0].item)
	if not itm.default_warehouse:
		frappe.throw(_("Default warehouse must be set for item {itm}".format(itm.name)))		
		return
	else:
		return itm.default_warehouse
