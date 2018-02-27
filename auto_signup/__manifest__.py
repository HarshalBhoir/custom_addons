# -*- coding: utf-8 -*-
{
    'name': "Auto Signup",

    'summary': """
        Automatic signup enable""",

    'description': """
        No need to enable 'Allow external users to sign up' from General Settings
	This module installation automatically enable external signup without any configuration with Template user
    """,

    'author': "Aktiv software ",
    'website': "http://www.aktivsoftware.com/",

    'category': 'signup',
    'version': '0.1',

    'depends': ['base_setup', 'website', 'portal'],

    'data': [
	'views/signup_views.xml'
    ],

    'images':  ['static/description/banner.jpg'],
    'application': True,
}
