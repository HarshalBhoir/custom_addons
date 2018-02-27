# -*- coding: utf-8 -*-

from odoo import models, api

class SignupEnable(models.Model):
    _name = 'signup.enable'

    @api.model
    def _init_settings(self):
        base_settings_obj = self.env['base.config.settings']
	#Activate allow signup with template user
        base_settings_id = base_settings_obj.create({'auth_signup_uninvited':True, 'template_user_id': True})
        base_settings_id.execute() #Execute setting
        return True
