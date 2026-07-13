# -*- coding: utf-8 -*-
from odoo import fields, models


class GoalsBadge(models.Model):
    """Insignias otorgadas por logros en el sistema de objetivos."""

    _name = 'goals.badge'
    _description = 'Insignia'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )
    description = fields.Text(
        string='Descripción',
        translate=True,
    )
    image = fields.Binary(
        string='Imagen',
        attachment=True,
    )
    icon_class = fields.Char(
        string='Clase de icono',
        default='fa fa-star',
        help='Clase de icono FontAwesome, por ejemplo "fa fa-trophy".',
    )
    xp_amount = fields.Integer(
        string='XP al otorgar',
        default=0,
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        index=True,
        default=lambda self: self.env.company,
    )
