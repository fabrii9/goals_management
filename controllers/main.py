# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
from odoo.tools import date_utils


class GoalsDashboardController(http.Controller):
    """Controlador para el dashboard de Goals Management System."""

    @http.route('/goals/dashboard/data', type='jsonrpc', auth='user')
    def dashboard_data(self):
        """Retorna los datos necesarios para renderizar el dashboard."""
        user = request.env.user
        today = fields.Date.context_today(user)
        company_id = user.company_id.id

        # Objetivo anual actual
        year_goal = request.env['goals.goal'].sudo().search([
            ('period_type', '=', 'year'),
            ('state', 'in', ['draft', 'active', 'done']),
            ('date_start', '<=', today),
            ('date_end', '>=', today),
            ('company_id', '=', company_id),
        ], order='priority desc, id desc', limit=1)

        # Objetivo semanal actual
        week_goal = request.env['goals.goal'].sudo().search([
            ('period_type', '=', 'week'),
            ('state', 'in', ['draft', 'active', 'done']),
            ('date_start', '<=', today),
            ('date_end', '>=', today),
            ('company_id', '=', company_id),
        ], order='priority desc, id desc', limit=1)

        # Focos del día
        daily_focus = request.env['goals.daily.focus'].sudo().search([
            ('user_id', '=', user.id),
            ('date', '=', today),
        ], order='sequence')

        # Tareas recientes completadas
        recent_tasks = request.env['project.task'].sudo().search([
            ('micro_objective_id', '!=', False),
            ('is_closed', '=', True),
            ('company_id', '=', company_id),
        ], order='date_last_stage_update desc', limit=10)

        # Datos para gráfico de productividad (últimas 7 semanas)
        productivity_data = self._get_productivity_data(user, today)

        return {
            'user': {
                'name': user.name,
                'id': user.id,
                'goals_xp_total': user.goals_xp_total,
                'goals_level': user.goals_level,
                'goals_xp_for_next_level': user.goals_xp_for_next_level,
                'goals_xp_in_current_level': user.goals_xp_in_current_level,
                'goals_progress_to_next_level': user.goals_progress_to_next_level,
                'goals_streak_days': user.goals_streak_days,
                'goals_badges_count': user.goals_badges_count,
            },
            'year_goal': self._goal_to_dict(year_goal),
            'week_goal': self._goal_to_dict(week_goal),
            'daily_focus': [
                {
                    'id': focus.id,
                    'sequence': focus.sequence,
                    'name': focus.name,
                    'state': focus.state,
                    'micro_objective_id': focus.micro_objective_id.id,
                }
                for focus in daily_focus
            ],
            'recent_tasks': [
                {
                    'id': task.id,
                    'name': task.name,
                    'project': task.project_id.name,
                    'user': task.user_id.name,
                    'date': task.date_last_stage_update.isoformat()
                    if task.date_last_stage_update else None,
                }
                for task in recent_tasks
            ],
            'productivity_data': productivity_data,
            'gamification_enabled': request.env['ir.config_parameter']
            .sudo()
            .get_param('goals_management.gamification_enabled'),
        }

    def _goal_to_dict(self, goal):
        if not goal:
            return False
        return {
            'id': goal.id,
            'name': goal.name,
            'progress': goal.progress,
            'period_type': goal.period_type,
            'state': goal.state,
            'date_start': goal.date_start.isoformat() if goal.date_start else None,
            'date_end': goal.date_end.isoformat() if goal.date_end else None,
        }

    def _get_productivity_data(self, user, today):
        """Calcula tareas completadas por día durante la última semana."""
        start_date = date_utils.subtract(today, days=6)
        tasks = request.env['project.task'].sudo().search([
            ('micro_objective_id', '!=', False),
            ('is_closed', '=', True),
            ('date_last_stage_update', '>=', start_date),
            ('date_last_stage_update', '<=', today),
            ('company_id', '=', user.company_id.id),
        ])
        data = {}
        for i in range(7):
            day = date_utils.add(start_date, days=i)
            data[day.isoformat()] = 0
        for task in tasks:
            day = task.date_last_stage_update
            if day:
                data[day.isoformat()] = data.get(day.isoformat(), 0) + 1
        return [
            {'date': day, 'completed': count}
            for day, count in sorted(data.items())
        ]
