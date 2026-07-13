# -*- coding: utf-8 -*-
from odoo import fields, models


class GoalsUserBadge(models.Model):
    """Relación entre usuarios e insignias obtenidas."""

    _name = 'goals.user.badge'
    _description = 'Insignia de Usuario'
    _order = 'date desc, id desc'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        index=True,
        required=True,
    )
    badge_id = fields.Many2one(
        comodel_name='goals.badge',
        string='Insignia',
        index=True,
        required=True,
    )
    date = fields.Datetime(
        string='Fecha de obtención',
        default=fields.Datetime.now,
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        index=True,
        default=lambda self: self.env.company,
    )
