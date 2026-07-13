# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestGoalsGamification(TransactionCase):

    def setUp(self):
        super(TestGoalsGamification, self).setUp()
        self.user = self.env.ref('base.user_admin')
        self.env['ir.config_parameter'].sudo().set_param(
            'goals_management.gamification_enabled', 'True'
        )

    def test_grant_xp(self):
        """Otorgar XP debe crear un registro y actualizar el nivel."""
        self.user.goals_grant_xp(
            1500,
            source='test',
            description='XP de prueba',
        )
        self.assertEqual(self.user.goals_xp_total, 1500)
        self.assertEqual(self.user.goals_level, 2)
        logs = self.env['goals.xp.log'].sudo().search([
            ('user_id', '=', self.user.id),
        ])
        self.assertEqual(len(logs), 1)

    def test_streak_update(self):
        """La racha debe incrementarse en días consecutivos."""
        from odoo import fields
        today = fields.Date.context_today(self.user)
        yesterday = fields.Date.subtract(today, days=1)
        self.user.goals_last_active_date = yesterday
        self.user.goals_streak_days = 5
        self.user._goals_update_streak()
        self.assertEqual(self.user.goals_streak_days, 6)
        self.assertEqual(self.user.goals_last_active_date, today)
