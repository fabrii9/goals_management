# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Configuración global del sistema de gestión de objetivos."""

    _inherit = 'res.config.settings'

    goals_gamification_enabled = fields.Boolean(
        string='Activar gamificación',
        config_parameter='goals_management.gamification_enabled',
        default=False,
    )
    goals_xp_task = fields.Integer(
        string='XP por completar tarea',
        config_parameter='goals_management.xp_task',
        default=10,
    )
    goals_xp_micro = fields.Integer(
        string='XP por completar microobjetivo',
        config_parameter='goals_management.xp_micro',
        default=50,
    )
    goals_xp_week = fields.Integer(
        string='XP por completar objetivo semanal',
        config_parameter='goals_management.xp_week',
        default=300,
    )
    goals_xp_month = fields.Integer(
        string='XP por completar objetivo mensual',
        config_parameter='goals_management.xp_month',
        default=1000,
    )
