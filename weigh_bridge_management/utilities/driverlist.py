import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond


def load_drivers(vehicleno):
    """Loads Drivers list in `__onload`"""
    #Get Vehicle Drivers
    vddict = frappe.db.sql("SELECT vehicle_driver FROM `tabVehicle Driver` WHERE parent = '{vno}';".format(vno=vehicleno), as_dict=1)

    vdlist = map(lambda x: x['vehicle_driver'], vddict) #Returns values of dict as a list.

    #Load drivers from license nos.
    dl = frappe.get_all("Driver", fields=["*"], filters={"name" : ["in", vdlist]}, order_by="wb_driver_fn")
    return dl

	
def driver_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""SELECT A.name, A.wb_driver_fn, A.wb_driver_ln, A.full_name, A.wb_driver_licence from `tabDriver` as A
            INNER JOIN `tabVehicle Driver` AS B on A.name = B.vehicle_driver
            where B.parent = '{vehicleno}' 
                and ({key} like %(txt)s
                or wb_driver_fn like %(txt)s
                or wb_driver_licence like %(txt)s)
            {mcond}
        order by
            if(locate(%(_txt)s, A.name), locate(%(_txt)s, A.name), 99999),
            if(locate(%(_txt)s, wb_driver_fn), locate(%(_txt)s, wb_driver_fn), 99999),
            if(locate(%(_txt)s, wb_driver_licence), locate(%(_txt)s, wb_driver_licence), 99999)
        limit %(start)s, %(page_len)s""".format(
            key="A.name" if searchfield == 'name' else searchfield,
            vehicleno=filters.get('vehicleno'),
            mcond=get_match_cond(doctype)
        ), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len
        })