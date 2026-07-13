# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import float_round


class ResUsers(models.Model):
    """Extensión de usuarios para gamificación de objetivos."""

    _inherit = 'res.users'

    goals_xp_total = fields.Integer(
        string='XP total',
        compute='_compute_goals_xp',
        store=True,
    )
    goals_level = fields.Integer(
        string='Nivel',
        compute='_compute_goals_xp',
        store=True,
    )
    goals_xp_for_next_level = fields.Integer(
        string='XP para siguiente nivel',
        compute='_compute_goals_xp',
        store=True,
    )
    goals_xp_in_current_level = fields.Integer(
        string='XP en nivel actual',
        compute='_compute_goals_xp',
        store=True,
    )
    goals_progress_to_next_level = fields.Float(
        string='Progreso al siguiente nivel',
        compute='_compute_goals_xp',
        store=True,
    )
    goals_streak_days = fields.Integer(
        string='Racha (días)',
        default=0,
    )
    goals_last_active_date = fields.Date(
        string='Última fecha activa',
    )
    goals_badges_count = fields.Integer(
        string='Insignias',
        compute='_compute_goals_badges_count',
        store=True,
    )

    @api.depends('goals_xp_log_ids.amount')
    def _compute_goals_xp(self):
        """Calcula nivel y progreso a partir del XP acumulado."""
        for user in self:
            total = sum(user.goals_xp_log_ids.mapped('amount'))
            user.goals_xp_total = total
            # Nivel lineal: 1000 XP por nivel.
            level = 1 + (total // 1000)
            xp_for_current = (level - 1) * 1000
            xp_for_next = level * 1000
            user.goals_level = level
            user.goals_xp_for_next_level = xp_for_next
            user.goals_xp_in_current_level = total - xp_for_current
            progress = (
                (total - xp_for_current) / (xp_for_next - xp_for_current)
                * 100.0 if xp_for_next > xp_for_current else 0.0
            )
            user.goals_progress_to_next_level = float_round(
                progress, precision_digits=2
            )

    @api.depends('goals_user_badge_ids')
    def _compute_goals_badges_count(self):
        for user in self:
            user.goals_badges_count = len(user.goals_user_badge_ids)

    goals_xp_log_ids = fields.One2many(
        comodel_name='goals.xp.log',
        inverse_name='user_id',
        string='Registros de XP',
    )
    goals_user_badge_ids = fields.One2many(
        comodel_name='goals.user.badge',
        inverse_name='user_id',
        string='Insignias obtenidas',
    )

    def goals_grant_xp(self, amount, source, source_model=None,
                       source_res_id=None, description=None):
        """Otorga experiencia al usuario y actualiza racha si corresponde.

        Este método es el punto central de la gamificación. Otros modelos
        lo invocan cuando ocurre un evento que debe generar XP.
        """
        self.ensure_one()
        if amount <= 0:
            return self.env['goals.xp.log']
        self.env['goals.xp.log'].sudo().create({
            'user_id': self.id,
            'amount': amount,
            'source': source,
            'source_model': source_model,
            'source_res_id': source_res_id or 0,
            'description': description,
            'company_id': self.env.company.id,
        })
        self._goals_update_streak()
        return True

    def _goals_update_streak(self):
        """Actualiza la racha de días consecutivos con actividad."""
        self.ensure_one()
        today = fields.Date.context_today(self)
        last = self.goals_last_active_date
        if not last:
            self.goals_streak_days = 1
        elif last == today:
            return
        elif last == fields.Date.add(today, days=-1):
            self.goals_streak_days += 1
        else:
            self.goals_streak_days = 1
        self.goals_last_active_date = today

    def action_grant_badge(self, badge):
        """Otorga una insignia al usuario si aún no la posee."""
        self.ensure_one()
        if not badge:
            return False
        existing = self.env['goals.user.badge'].sudo().search([
            ('user_id', '=', self.id),
            ('badge_id', '=', badge.id),
        ], limit=1)
        if existing:
            return False
        self.env['goals.user.badge'].sudo().create({
            'user_id': self.id,
            'badge_id': badge.id,
            'company_id': self.env.company.id,
        })
        if badge.xp_amount:
            self.goals_grant_xp(
                badge.xp_amount,
                source='badge',
                source_model='goals.badge',
                source_res_id=badge.id,
                description=f"Insignia: {badge.name}",
            )
        return True
