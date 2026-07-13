# -*- coding: utf-8 -*-
from odoo import fields, models


class CalendarEvent(models.Model):
    """Extensión de eventos de calendario para vincularlos a objetivos."""

    _inherit = 'calendar.event'

    goal_id = fields.Many2one(
        comodel_name='goals.goal',
        string='Objetivo estratégico',
        index=True,
        help='Objetivo estratégico relacionado con este evento.',
    )
    micro_objective_id = fields.Many2one(
        comodel_name='goals.micro.objective',
        string='Microobjetivo',
        index=True,
        help='Microobjetivo relacionado con este evento.',
    )
