// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on("Driver", "wb_driver_fn", function(frm) {
	setfullname(frm);
});

frappe.ui.form.on("Driver", "wb_driver_ln", function(frm) {
	setfullname(frm);
});


function setfullname(frm) {
	frm.set_value("full_name", frm.doc.wb_driver_fn + (frm.doc.wb_driver_ln ? ' ' + frm.doc.wb_driver_ln : ''));
}