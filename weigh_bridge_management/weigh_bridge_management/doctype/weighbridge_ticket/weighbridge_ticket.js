// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

var weighing_complete = "Weighing Complete";

frappe.ui.form.on('Weighbridge Ticket', {
	party_type: function(frm){
		if (frm.doc.party_type==="Customer"){
			frm.set_value("wbt_load_direction","Outgoing");
			//Set selling price list
		} 
		else if (frm.doc.party_type==="Supplier") {
			frm.set_value("wbt_load_direction","Incoming");
			//Set buying price list
		}
	},

	wbt_second_weighing: function(frm){
		if (frm.doc.wbt_first_weighing && frm.doc.wbt_second_weighing){
			frm.set_value("wbt_net_weight", Math.abs(frm.doc.wbt_first_weighing - frm.doc.wbt_second_weighing));
		} 
	},

	
	refresh: function(frm, cdt, cdn) {
		set_second_weighing_visibility(frm);
		cur_frm.add_fetch("wbt_driver", "full_name", "driver_name");
		cur_frm.add_fetch("wbt_vehicle", "wb_vehicle_tare_weight", "wbt_vehicle_tare_weight");
		if (frm.doc.workflow_state == "Weighing Complete") {
			if (frm.doc.party_type == "Customer") {
				make_btn_sales_docs(frm);
			} else if (frm.doc.party_type == "Supplier") {
				make_btn_purchase_docs(frm);
			}
		}

		//Filter drivers by vehicle.
		frm.set_query("wbt_driver", function() {
			return {
				query: "weigh_bridge_management.utilities.driverlist.driver_query",
				filters: {"vehicleno": frm.doc.wbt_vehicle}
			};
		});
	},
	customer: function(frm){
		var acc = "Debtors - " + frappe.get_abbr(frm.doc.company,frm.doc.company.length);
		frappe.call({
			method: "erpnext.accounts.utils.get_balance_on",
			args: { "party_type": frm.doc.party_type,
					"party": frm.doc.customer,
					"account" : acc, 		
				  },
			
			callback: function(r){
				if (!r.message || r.message  == 0.0) {
					frm.set_value("customer_balance_status","Customer " + frm.doc.customer + " has not made any deposit");
				}
				else if(r.message<0.0){
					frm.set_value("customer_balance_status","Customer " + frm.doc.customer + " has made a deposit and balance is: Rp " + r.message + " (CR balance)");				
				}
				else{
					fetch_msg_with_creditlimit(frm,r.message);
				}
			}
		});		
	}
});

function fetch_msg_with_creditlimit(frm,message){
	frappe.db.get_value("Customer", {"customer_name": frm.doc.customer}, "credit_limit", function(r) {
		frm.set_value("customer_balance_status","Customer " + frm.doc.customer + " has a credit limit of Rp. " + r.credit_limit  + " and balance of Rp " + message + " (DR balance)");		
	});
}

function make_btn_purchase_docs(frm) {
	frm.add_custom_button(__('Purchase Order'), function(){
		frappe.call({
			method: "weigh_bridge_management.weigh_bridge_management.doctype.weighbridge_ticket.weighbridge_ticket.check_create_po",
			args: {"wbtname": frm.doc.name},
			freeze: true,
			freeze_message: __("Creating Purchase Order"),
			callback: function(r){
				if(!r.exc) {
					//frappe.msgprint(__("Purchase Docs created."));
				} else {
					frappe.msgprint(__("Purchase Order could not be created. <br /> " + r.exc));
				}
			}
		});
	}, __("Make"));


	frm.add_custom_button(__('Purchase Receipt'), function(){
		frappe.call({
			method: "weigh_bridge_management.weigh_bridge_management.doctype.weighbridge_ticket.weighbridge_ticket.check_create_pr",
			args: {"wbtname": frm.doc.name},
			freeze: true,
			freeze_message: __("Creating Purchase Receipt"),
			callback: function(r){
				if(!r.exc) {
					//frappe.msgprint(__("Purchase Docs created."));
				} else {
					frappe.msgprint(__("Purchase Receipt could not be created. <br /> " + r.exc));
				}
			}
		});
	}, __("Make"));

	frm.add_custom_button(__('Purchase Invoice'), function(){
		frappe.call({
			method: "weigh_bridge_management.weigh_bridge_management.doctype.weighbridge_ticket.weighbridge_ticket.check_create_pi",
			args: {"wbtname": frm.doc.name},
			freeze: true,
			freeze_message: __("Creating Purchase Invoice"),
			callback: function(r){
				if(!r.exc) {
					//frappe.msgprint(__("Purchase Docs created."));
				} else {
					frappe.msgprint(__("Purchase Invoice could not be created. <br /> " + r.exc));
				}
			}
		});
	}, __("Make"));
}

function make_btn_sales_docs(frm) {
	frm.add_custom_button(__('Sales Order'), function(){
		frappe.call({
			method: "weigh_bridge_management.weigh_bridge_management.doctype.weighbridge_ticket.weighbridge_ticket.check_create_so",
			args: {"wbtname": frm.doc.name},
			freeze: true,
			freeze_message: __("Creating Sales Order"),
			callback: function(r){
				if(!r.exc) {
					//frappe.msgprint(__("Purchase Docs created."));
				} else {
					frappe.msgprint(__("Sales Order could not be created. <br /> " + r.exc));
				}
			}
		});
	}, __("Make"));

	frm.add_custom_button(__('Delivery Note'), function(){
		frappe.call({
			method: "weigh_bridge_management.weigh_bridge_management.doctype.weighbridge_ticket.weighbridge_ticket.check_create_dn",
			args: {"wbtname": frm.doc.name},
			freeze: true,
			freeze_message: __("Creating Delivery Note"),
			callback: function(r){
				if(!r.exc) {
					//frappe.msgprint(__("Purchase Docs created."));
				} else {
					frappe.msgprint(__("Delivery note could not be created. <br /> " + r.exc));
				}
			}
		});
	}, __("Make"));

	frm.add_custom_button(__('Sales Invoice'), function(){
		frappe.call({
			method: "weigh_bridge_management.weigh_bridge_management.doctype.weighbridge_ticket.weighbridge_ticket.check_create_si",
			args: {"wbtname": frm.doc.name},
			freeze: true,
			freeze_message: __("Creating Sales Invoice"),
			callback: function(r){
				if(!r.exc) {
					//frappe.msgprint(__("Purchase Docs created."));
				} else {
					frappe.msgprint(__("Sales Invoice could not be created. <br /> " + r.exc));
				}
			}
		});
	}, __("Make"));
}


//Hide second weighing fields when doc is local or draft. Shown and enabled on submit.
function set_second_weighing_visibility(frm) {

	var condition_hidden = (frm.doc.__islocal || frm.doc.docstatus==0)
	var condition_readonly = (frm.doc.workflow_state != "Second Weighing")

	frm.set_df_property("wbt_second_weighing_heading", "hidden", condition_hidden);
	frm.set_df_property("wbt_second_weighing", "read_only", condition_readonly);
	frm.set_df_property("wbt_second_weighing", "hidden", condition_hidden);
	frm.set_df_property("wbt_second_weigh_uom", "read_only", condition_readonly);
	frm.set_df_property("wbt_second_weigh_uom", "hidden", condition_hidden);
	frm.set_df_property("wbt_time_out", "read_only", condition_readonly);
	frm.set_df_property("wbt_time_out", "hidden", condition_hidden);
	
}
cur_frm.add_fetch("company", "default_currency", "company_currency");
