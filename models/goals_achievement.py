# -*- coding: utf-8 -*-
from odoo import fields, models


class GoalsAchievement(models.Model):
    """Definición de logros desbloqueables del sistema de objetivos."""

    _name = 'goals.achievement'
    _description = 'Logro'
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
    condition_code = fields.Char(
        string='Código de condición',
        required=True,
        help='Identificador técnico de la condición para desbloquear el logro.',
    )
    badge_id = fields.Many2one(
        comodel_name='goals.badge',
        string='Insignia asociada',
    )
    xp_amount = fields.Integer(
        string='XP al desbloquear',
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
