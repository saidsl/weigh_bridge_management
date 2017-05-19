frappe.query_reports["Driver List"] = {
	"filters": [
		{
			"fieldname":"wb_vehicle_registration",
			"label": __("Vehicle Registration"),
			"fieldtype": "data",
			"default": frappe.defaults.get_user_default("wb_vehicle_registration")
		},
		{
			"fieldname":"wb_customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"wb_supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname":"wb_driver_fn",
			"label": __("First Name"),
			"fieldtype": "Data",
		},
		
	]
}

