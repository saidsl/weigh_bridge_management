# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "weigh_bridge_management"
app_title = "Weigh Bridge Management"
app_publisher = "MN Technique"
app_description = "ERPNext Weigh Bridge Management App"
app_icon = "icon-truck"
app_color = "#16161D"
app_email = "support@castlecraft.in"
app_license = "GPL v3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/weigh_bridge_management/css/weigh_bridge_management.css"
# app_include_js = "/assets/weigh_bridge_management/js/weigh_bridge_management.js"
app_include_js = "/assets/js/wbm.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/weigh_bridge_management/css/weigh_bridge_management.css"
# web_include_js = "/assets/weigh_bridge_management/js/weigh_bridge_management.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "weigh_bridge_management.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "weigh_bridge_management.install.before_install"
# after_install = "weigh_bridge_management.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "weigh_bridge_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"weigh_bridge_management.tasks.all"
# 	],
# 	"daily": [
# 		"weigh_bridge_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"weigh_bridge_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"weigh_bridge_management.tasks.weekly"
# 	]
# 	"monthly": [, 
# 		"weigh_bridge_management.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "weigh_bridge_management.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
#frappe.desk.doctype.event.event.get_events": "weigh_bridge_management.event.get_events"
	"frappe.desk.moduleview.get":"weigh_bridge_management.api.wbmget"
}

fixtures = ["Custom Script", 
			"Custom Field", 
			"Property Setter",  
			{"dt": "UOM", "filters": [["name", "=", "Tons"]]},
			{"dt": "Workflow", "filters": [["document_type", "=", "Weighbridge Ticket"]]},
			{"dt": "Workflow State", "filters": [["name", "in", ["First Weighing", "Second Weighing", "Weighing Complete"]]]},
			{"dt": "Workflow Action", "filters": [["name", "=", "Second Weighing"]]}, 
			{"dt": "Print Format", "filters": [["name", "=", "Print Without Amount"]]}]