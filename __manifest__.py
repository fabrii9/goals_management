# -*- coding: utf-8 -*-
{
    'name': 'Goals Management System',
    'version': '19.0.1.0.0',
    'summary': 'Sistema de Gestion de Objetivos integrado con Proyecto y Helpdesk.',
    'description': """
Goals Management System para Odoo 19
=====================================

Convierte tareas diarias en progreso medible hacia objetivos personales
y empresariales.
    """,
    'category': 'Productivity',
    'author': 'Aftermoves',
    'website': 'https://aftermoves.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'project',
        'calendar',
    ],
    'data': [
        'security/goals_security.xml',
        'security/ir.model.access.csv',
        'data/goals_sequence.xml',
        'views/goals_category_views.xml',
        'views/goals_tag_views.xml',
        'views/goals_goal_views.xml',
        'views/goals_micro_objective_views.xml',
        'views/goals_daily_focus_views.xml',
        'views/project_task_views.xml',
        'views/calendar_event_views.xml',
        'views/goals_dashboard_views.xml',
        'views/res_config_settings_views.xml',
        'views/goals_menus.xml',
    ],
    'demo': [
        'data/goals_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'goals_management/static/src/components/**/*',
            'goals_management/static/src/scss/goals_management.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
