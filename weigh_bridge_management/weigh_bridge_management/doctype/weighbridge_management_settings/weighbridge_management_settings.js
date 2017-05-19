// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

cur_frm.set_query("warehouse", "warehouses", function(doc, cdt, cdn) {
	return{
		filters: [
			['Warehouse', 'company', '=', doc.company]
		]
	}
});
