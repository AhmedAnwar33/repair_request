# -*- coding: utf-8 -*-
{
    'name': "Repair Request Management",
    'summary': """ Manage and track customer repair requests. """,
    'description': """
        Repair Request Management
        This module allows businesses to efficiently manage repair requests from customers.
        Key Features:
        - Track repair requests with states: Draft, In Progress, Done.
        - Automatically compute time spent on repairs.
        - Assign priorities and due dates (dateline) to requests.
        - Link repair requests to customers and devices.
        - Add multiple repair line items with products, quantities, and pricing.
        - Automatically calculate estimated repair costs.
        - Generate invoices directly from completed repair requests.

        Ideal for service centers, IT support teams, or any business handling equipment repairs.

    """,
    'author': "Ahmed Anwar",
    'website': "https://www.linkedin.com/in/ahmed-anwar-a055ab254/",
    "license": "LGPL-3",
    'category': 'Sales/Sales',
    'version': '18.0.1.0.0',
    'depends': ['base','product','account'],

    'data': [
        'data/sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/repair_request_views.xml',
        'report/repair_request_template.xml',
        'report/reports.xml',
        
        'views/menu.xml',
    ],
}
