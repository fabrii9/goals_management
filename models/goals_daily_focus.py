# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GoalsDailyFocus(models.Model):
    """Focos diarios: máximo 3 objetivos importantes por usuario y día."""

    _name = 'goals.daily.focus'
    _description = 'Foco Diario'
    _order = 'date desc, sequence, id'

    STATES = [
        ('pending', 'Pendiente'),
        ('done', 'Hecho'),
    ]

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        default=lambda self: self.env.user,
        index=True,
        required=True,
    )
    date = fields.Date(
        string='Fecha',
        default=fields.Date.context_today,
        index=True,
        required=True,
    )
    sequence = fields.Integer(
        string='Orden',
        default=1,
        required=True,
        help='Posición del foco diario (1, 2 o 3).',
    )
    name = fields.Char(
        string='Título',
        required=True,
    )
    micro_objective_id = fields.Many2one(
        comodel_name='goals.micro.objective',
        string='Microobjetivo vinculado',
        index=True,
    )
    goal_id = fields.Many2one(
        comodel_name='goals.goal',
        string='Objetivo vinculado',
        index=True,
        help='Permite vincular un objetivo estratégico directamente.',
    )
    state = fields.Selection(
        selection=STATES,
        string='Estado',
        default='pending',
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        index=True,
        default=lambda self: self.env.company,
        required=True,
    )

    _user_date_sequence_uniq = models.Constraint(
        "UNIQUE (user_id, date, sequence)",
        "Solo se permiten 3 focos diarios por usuario.",
    )

    @api.constrains('sequence')
    def _check_sequence_range(self):
        for focus in self:
            if focus.sequence < 1 or focus.sequence > 3:
                raise ValidationError(_(
                    "El orden del foco diario debe estar entre 1 y 3."
                ))

    @api.constrains('micro_objective_id', 'goal_id')
    def _check_single_link(self):
        for focus in self:
            if focus.micro_objective_id and focus.goal_id:
                raise ValidationError(_(
                    "Un foco diario no puede vincular un microobjetivo y un "
                    "objetivo estratégico al mismo tiempo."
                ))

    def action_done(self):
        self.write({'state': 'done'})

    def action_pending(self):
        self.write({'state': 'pending'})
