# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT , DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _
import logging
from odoo.osv import  osv
from odoo import SUPERUSER_ID
import geocoder
from time import gmtime, strftime
import dateutil.parser
from openerp.exceptions import UserError , ValidationError
import requests
import googlemaps
import urllib
import simplejson
from geopy.geocoders import GoogleV3

# googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

# gmaps = googlemaps.Client(key='AIzaSyBWGBUR56Byqip7RUel5-EeWzFQygna2Hg')
# google_api_key = 'AIzaSyCt4jsSrJ9C9tIhlAg0hMerzY3lOE1yoq8'
geocoder = GoogleV3()


datetimeFormat = '%Y-%m-%d %H:%M:%S'

class sales_meet(models.Model):
    _inherit = "calendar.event"


    @api.model
    def create(self, vals):
        # print "HHHHHHHHHHHHH" , vals , vals["start_datetime"]
        result = super(sales_meet, self).create(vals)
        

        # a = vals["start_datetime"]
        # c = strftime("%Y-%m-%d")
        # d = dateutil.parser.parse(a).date()
        # if str(d) !=c:
        #     raise UserError("Please Select Todays Date")




        return result

#    @api.multi
 #   def write(self ,vals):
  #      res = super(sales_meet, self).write(vals)
#
 #       a = self.start_datetime
  #      c = strftime("%Y-%m-%d")
   #     d = dateutil.parser.parse(a).date()
    #    if str(d) < c:
     #       raise UserError("Please Select Todays Date")
#
 #              
  #      return res

    # @api.model
    # def create(self, vals):
    #     if ('name' not in vals and vals['type_order'] == 'claim')\
    #     or ('name' in vals and vals.get('name') == 'New' and vals['type_order'] == 'claim'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('claim.order')
    #     result = super(claim_order, self).create(vals)
    #     return result

    @api.model
    def default_get(self, fields_list):
        res = super(sales_meet, self).default_get(fields_list)

        res['start_datetime'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        res['start'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        res['stop'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        # res['stop_datetime'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        # res['name'] = "KKKKKKKKKKKKKKKKKK"

        # meetings = self.env['calendar.event'].search([])
        # for record in meetings:
        #     if record.status != 'close' and record.user_id.id == self.env.uid :
        #         raise ValidationError('Kindly Checkout from previous Meeting - %s' % (record.name))
        return res

    

    # def _default_stage_id(self):
    #     stage = self.env['crm.stage'].search([('name','=','New')])
    #     return stage.id

    name = fields.Char('Meeting Subject', states={'done': [('readonly', True)]}, required=False) #, states={'done': [('readonly', True)]}, required=False
    checkin_lattitude = fields.Float('Checkin Latitude' , digits=(16, 5) , store=True, track_visibility='onchange') 
    checkin_longitude = fields.Float('Checkin Longitude', digits=(16, 5), store=True, track_visibility='onchange')  
    checkout_lattitude = fields.Char('Checkout Latitude')
    checkout_longitude = fields.Char('Checkout Longitude')
    distance = fields.Char('Distance')
    timein = fields.Datetime(string="Time IN")
    timeout = fields.Datetime(string="Time OUT")
    # start_datetime = fields.Datetime(string="Date" ,default=lambda self: datetime.now())
    islead = fields.Boolean("Lead")
    isopportunity = fields.Boolean("Opportunity")
    iscustomer = fields.Boolean("Customer")
    ischeck = fields.Selection([('lead', 'Lead'), ('opportunity', 'Opportunity'), ('customer', 'Customer')], string='Is Lead/Customer', 
         track_visibility='onchange')
    lead_id = fields.Many2one('crm.lead', string='Lead', track_visibility='always')
    # partner_id = fields.Many2one('res.partner', string='Customer', track_visibility='always')
    status = fields.Selection([('draft', 'Draft'), ('open', 'In Meeting'), ('close', 'Close')], string='Status', 
        readonly=True, track_visibility='onchange', default='draft')
    stage_id = fields.Many2one('crm.stage', string='Stage', track_visibility='onchange', index=True ) # default=lambda self: self._default_stage_id()
    meeting_duration = fields.Char('Meeting Duration')
    source = fields.Char('Source Address')
    source_address = fields.Char('Source Address')
    destination = fields.Char('Destination Address')
    destination_address = fields.Char('Destination Address')
    # phone = fields.Char('Phone')
    # website = fields.Char('Website')
    partner_latitude = fields.Float(string='Source Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Source Geo Longitude', digits=(16, 5))
    partner_dest_latitude = fields.Float(string='Dest Geo Latitude', digits=(16, 5))
    partner_dest_longitude = fields.Float(string='Dest Geo Longitude', digits=(16, 5))
    date_localization = fields.Date(string='Geolocation Date')

    # CRM Actions
    next_activity_id = fields.Many2one("crm.activity", string="Next Activity", index=True)
    date_action = fields.Date('Next Activity Date', index=True)
    title_action = fields.Char('Next Activity Summary')
    categ_id = fields.Many2one('crm.activity', string="Activity", track_visibility='always')
    partner_id = fields.Many2one('res.partner', track_visibility='always')

    start = fields.Datetime('Start')
    stop = fields.Datetime('Stop')
    start_date = fields.Date('Start Date', compute=False, inverse=False)
    start_datetime = fields.Datetime('Start DateTime', compute=False, inverse=False)
    stop_date = fields.Date('End Date', compute=False, inverse=False)
    stop_datetime = fields.Datetime('End Datetime', compute=False, inverse=False)  # old date_deadline
    display_time = fields.Char('Event Time', compute=False)
    display_start = fields.Char('Date', compute=False)
    reverse_location = fields.Char('Current Location')

    @api.multi
    def checkedin(self):
            pass


    @api.multi
    def checkin(self):
        # if not self.name:
            self.status = 'open'
        #     print "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK"

        # else:
        #     self.name = ''
        #     raise UserError("Click on 'Check IN' Button first, Then enter Meeting name")


    # @api.onchange('start_datetime')
    # def _onchange_datetime(self):
    #     print "GGGGGGGGGGGGGGGGGGGGGGGG" , self.start_datetime , strftime("%Y-%m-%d")


    # @api.onchange('name','checkin_lattitude','checkin_longitude')
    # def _onchange_address(self):
    #     if self.checkin_lattitude and self.checkin_longitude:
    #         try:

    #             location_list = geocoder.reverse((self.checkin_lattitude,self.checkin_longitude))
    #             print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL" , location_list
    #             location = location_list[0]
    #             address = location.address

    #             self.reverse_location = address

    #         except UserError:
    #             pass


    @api.onchange('start_datetime')
    def _onchange_start_datetime(self):
        a = self.start_datetime
        c = strftime("%Y-%m-%d")
        d = dateutil.parser.parse(a).date()
        if str(d) < c:
            raise UserError("Please Select Todays Date")





    @api.multi
    def create_event(self):
        calendar_event_vals = {
                'name': self.title_action,
                'start_datetime': self.date_action,
                'stop_datetime': self.date_action,
                'start': self.date_action,
                'stop': self.date_action,
                'allday': False,
                'show_as': 'free',
                'partner_ids': [(6, 0, [])],
                'categ_id': self.next_activity_id.id,
                'user_id': self.user_id.id,
                'ischeck': self.ischeck,
                'lead_id': self.lead_id.id if self.ischeck=='lead' else '',
                # 'lead_id': self.lead_id.id if self.ischeck=='opportunity' else '',
                # 'lead_id': self.lead_id.id if self.ischeck=='lead' else '',
            }

        # # if self.name == self.search([('id','in',inv_res)])
        # prod_package = self.env['product.packaging'].search([('name','=',self.title_action)])

        # print "Create Meeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeting" , self.ischeck, self.lead_id.id, self.title_action, self.date_action,[(6, 0, [])], self.next_activity_id.id ,self.user_id.id, self.next_activity_id
        self.status = 'close'
        self.env['calendar.event'].create(calendar_event_vals)
        
