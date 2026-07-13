# -*- coding: utf-8 -*-
from odoo import fields, models


class GoalsXpLog(models.Model):
    """Trazabilidad de experiencia otorgada a usuarios."""

    _name = 'goals.xp.log'
    _description = 'Registro de XP'
    _order = 'date desc, id desc'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        index=True,
        required=True,
    )
    amount = fields.Integer(
        string='Cantidad',
        required=True,
    )
    source = fields.Char(
        string='Origen',
        required=True,
        help='Identificador del evento que generó la experiencia.',
    )
    source_model = fields.Char(
        string='Modelo origen',
        help='Modelo técnico relacionado con el evento.',
    )
    source_res_id = fields.Integer(
        string='ID origen',
        help='ID del registro que generó la experiencia.',
    )
    description = fields.Char(
        string='Descripción',
    )
    date = fields.Datetime(
        string='Fecha',
        default=fields.Datetime.now,
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        index=True,
        default=lambda self: self.env.company,
    )
