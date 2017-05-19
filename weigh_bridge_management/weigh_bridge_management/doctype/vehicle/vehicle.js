// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt
frappe.provide("erpnext.utils");

frappe.ui.form.on('Vehicle', {
	refresh: function(frm) {
		if (!cur_frm.doc.__islocal) {
			$(frm.fields_dict['drivers'].wrapper)
				.html(frappe.render_template("driver_list", cur_frm.doc.__onload));
		}
	}
});

cur_frm.add_fetch("vehicle_driver", "wb_driver_fn", "driver_name");
cur_frm.add_fetch("vehicle_driver", "wb_driver_licence", "driver_licence_no");
