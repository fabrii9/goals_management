# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.exceptions import AccessError


class TestGoalsSecurity(TransactionCase):

    def setUp(self):
        super(TestGoalsSecurity, self).setUp()
        self.user_a = self.env['res.users'].create({
            'name': 'Usuario A',
            'login': 'user_a',
            'group_ids': [(6, 0, [self.env.ref('goals_management.group_goals_user').id])],
        })
        self.user_b = self.env['res.users'].create({
            'name': 'Usuario B',
            'login': 'user_b',
            'group_ids': [(6, 0, [self.env.ref('goals_management.group_goals_user').id])],
        })

    def test_user_only_sees_own_goals(self):
        """Un usuario no debe ver objetivos ajenos."""
        goal_a = self.env['goals.goal'].sudo().create({
            'name': 'Objetivo A',
            'period_type': 'week',
            'date_start': fields.Date.from_string('2026-01-01'),
            'date_end': fields.Date.from_string('2026-01-07'),
            'user_id': self.user_a.id,
        })
        goal_b = self.env['goals.goal'].sudo().create({
            'name': 'Objetivo B',
            'period_type': 'week',
            'date_start': fields.Date.from_string('2026-01-01'),
            'date_end': fields.Date.from_string('2026-01-07'),
            'user_id': self.user_b.id,
        })

        env_a = self.env(user=self.user_a)
        goals_a = env_a['goals.goal'].search([])
        self.assertIn(goal_a.id, goals_a.ids)
        self.assertNotIn(goal_b.id, goals_a.ids)
