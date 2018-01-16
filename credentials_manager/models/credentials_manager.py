from openerp import models, fields, api, tools, _

class credentials_vault(models.Model):
	_name = 'credentials.vault'
	
	name = fields.Char(string="Name")
	username = fields.Char(string="Username")
	password = fields.Char(string="Password")
	comment = fields.Text(string="Comment")