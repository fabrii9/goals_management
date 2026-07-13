# -*- coding: utf-8 -*-
from odoo import fields, models


class GoalsCategory(models.Model):
    """Categorías para clasificar objetivos estratégicos y microobjetivos."""

    _name = 'goals.category'
    _description = 'Categoría de Objetivo'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )
    color = fields.Integer(
        string='Color',
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

    _name_uniq = models.Constraint(
        "UNIQUE (name, company_id)",
        "El nombre de la categoría debe ser único por compañía.",
    )
