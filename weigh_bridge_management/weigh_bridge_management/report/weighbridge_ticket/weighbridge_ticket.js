// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.query_reports["Weighbridge Ticket"] = {
	"filters": [
		{
			fieldname: "doc_type",
			label: __("Document Type"),
			fieldtype: "Select",
			options: "Customer\nSupplier",
			default: "Customer"
		}
	]
}
