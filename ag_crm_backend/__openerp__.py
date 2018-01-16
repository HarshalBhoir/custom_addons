{
    'name': 'AG CRM Material Theme',
    'version': '1.0',
    'author': 'Vinay Gharat (AQUAGiraffe - An MSP1 Company)',
    'sequence': 1,
    'category': 'UI',
    'description': """
Material Theme for AG CRM
""",
    'depends': ['web'],
    'data': [
        'views/ag_crm_backend.xml',
    ],
    'qweb': [
        # 'static/src/xml/ag_crm_backend.xml',
    ],
    'bootstrap': True,
    'installable' : True,
    'application' : False,
}