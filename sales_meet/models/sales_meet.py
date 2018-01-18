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
from openerp.exceptions import UserError , ValidationError
import requests
import googlemaps
import urllib
import simplejson

googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

gmaps = googlemaps.Client(key='AIzaSyBWGBUR56Byqip7RUel5-EeWzFQygna2Hg')


datetimeFormat = '%Y-%m-%d %H:%M:%S'

class sales_meet(models.Model):
    _inherit = "calendar.event"

    # @api.model
    # def create(self, vals):
    #     result = super(sales_meet, self).create(vals)

    #     print "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK"

    #     return result

    @api.model
    def default_get(self, fields_list):
        res = super(sales_meet, self).default_get(fields_list)

        # res['start_datetime'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        meetings = self.env['calendar.event'].search([])
        for record in meetings:
            if record.status != 'close' and record.user_id.id == self.env.uid :
                raise ValidationError('Kindly Checkout from previous Meeting - %s' % (record.name))
        return res


    def _default_stage_id(self):
        stage = self.env['crm.stage'].search([('name','=','New')])
        return stage.id

    checkin_lattitude = fields.Char('Checkin Latitude')
    checkin_longitude = fields.Char('Checkin Longitude')
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
    stage_id = fields.Many2one('crm.stage', string='Stage', track_visibility='onchange', index=True ,
     default=lambda self: self._default_stage_id())
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
    # street = fields.Char('Street')
    # street2 = fields.Char('Street2')
    # zip = fields.Char('Zip', change_default=True)
    # city = fields.Char('City')
    # state_id = fields.Many2one("res.country.state", string='State')
    # country_id = fields.Many2one('res.country', string='Country')

    # start = fields.Datetime('Start', help="Start date of an event, without time for full days events")
    # stop = fields.Datetime('Stop', help="Stop date of an event, without time for full days events")
    # start_datetime = fields.Datetime('Start DateTime', compute=False, inverse=False, store=True, states={'done': [('readonly', True)]}, track_visibility='onchange')


    # @api.onchange('name')
    # def _onchange_name(self):
    #     """ Make entry on email and availability on change of partner_id field. """
    #     print "LLLLLLLLLLLLLLLOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
    #     self.start_datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())


    # @api.multi
    # @api.depends('allday', 'start_date')
    # def _compute_display_start(self):
    #     for meeting in self:
    #         meeting.display_start = meeting.start_date if meeting.allday else meeting.start_datetime


    # @api.constrains('stop_datetime', 'start_date', 'stop_date')
    # def _check_closing_date(self):
    #     for meeting in self:
    #         if meeting.start_datetime and meeting.stop_datetime and meeting.stop_datetime < meeting.start_datetime:
    #             raise ValidationError(_('Ending datetime cannot be set before starting datetime.'))
    #         if meeting.start_date and meeting.stop_date and meeting.stop_date < meeting.start_date:
    #             raise ValidationError(_('Ending date cannot be set before starting date.'))

    # @api.onchange('duration')
    # def _onchange_duration(self):
    #     if self.start_datetime:
    #         start = fields.Datetime.from_string(self.start_datetime)
    #         self.start = self.start_datetime
    #         self.stop = fields.Datetime.to_string(start + timedelta(hours=self.duration))

    @api.one
    def checkin(self):
        latlong = []
        h = geocoder.ip('ip')
        g = geocoder.ip('me')
        latlong.append(g.latlng)
        self.checkin_lattitude = g.latlng[0]
        self.checkin_longitude = g.latlng[1]
        self.timein = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.status = 'open'
        # self.start_datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    @api.one
    def get_coordinates(self, from_sensor=False):
        query = self.source
        query = query.encode('utf-8')
        params = {
            'address': query,
            'sensor': "true" if from_sensor else "false"
        }
        url = googleGeocodeUrl + urllib.urlencode(params)
        json_response = urllib.urlopen(url)
        response = simplejson.loads(json_response.read())
        if response['results']:
            location = response['results'][0]['geometry']['location']
            latitude, longitude = location['lat'], location['lng']
        else:
            latitude, longitude = None, None
            print query, "<no results>"

        query2 = self.destination
        query2 = query2.encode('utf-8')
        params2 = {
            'address': query2,
            'sensor': "true" if from_sensor else "false"
        }
        url2 = googleGeocodeUrl + urllib.urlencode(params2)
        json_response2 = urllib.urlopen(url2)
        response2 = simplejson.loads(json_response2.read())
        if response2['results']:
            location2 = response2['results'][0]['geometry']['location']
            latitude2, longitude2 = location2['lat'], location2['lng']
        else:
            latitude2, longitude2 = None, None
            print query2, "<no results>"


        self.checkin_lattitude = latitude
        self.checkin_longitude = longitude

        self.checkout_lattitude = latitude2
        self.checkout_longitude = longitude2

        # self.description = str(latitude) + " ," + str(longitude)
        # return latitude, longitude

        source_latlong= '"' + str(latitude) + ',' + str(longitude) + '"'
        destination_latlong= '"' + str(latitude2) + ',' + str(longitude2) + '"'

        now = datetime.now()
        directions_result = gmaps.directions(source_latlong,
                                             destination_latlong,
                                             mode="driving",
                                             avoid="ferries",
                                             departure_time=now
                                            )


        self.distance =  directions_result[0]['legs'][0]['distance']['text']

        print directions_result[0]['legs'][0]['distance']['text']
        print  directions_result[0]['legs'][0]['duration']['text']  , type(directions_result[0]['legs'][0]['duration']['text'])



    @api.one
    def checkout(self):
        latlong = []
        duration = 0.0
        g = geocoder.ip('me')
        print(g.latlng)
        latlong.append(g.latlng)
        self.checkout_lattitude = g.latlng[0]
        self.checkout_longitude = g.latlng[1]
        self.timeout = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.status = 'close'

        duration = datetime.strptime(self.timeout, datetimeFormat) - datetime.strptime(self.timein,datetimeFormat)
        self.meeting_duration = duration
