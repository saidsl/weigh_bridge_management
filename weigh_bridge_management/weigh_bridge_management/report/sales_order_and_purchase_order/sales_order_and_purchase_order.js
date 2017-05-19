

frappe.query_reports["Sales Order and Purchase Order"] = {
	"filters": [
		{
			fieldname: "doc_type",
			label: __("Document Type"),
			fieldtype: "Select",
			options: "Sales Order\nPurchase Order",
			default: "Sales Order"
		}
	]
}