from odoo import models, fields, api, _

class crm_lead_extension(models.Model):
	_inherit = "crm.lead"

	website = fields.Char(string='Website')