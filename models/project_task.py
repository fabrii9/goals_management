# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    """Extensión de tareas de proyecto para vincularlas a objetivos.

    Una tarea puede vincularse a:
    - Un microobjetivo (goals.micro.objective), que a su vez pertenece a un
      objetivo semanal.
    - Directamente a un objetivo semanal (goals.goal de tipo 'week').

    Esto ofrece flexibilidad tanto para gestión detallada (microobjetivos)
    como para seguimiento rápido (objetivo semanal directo).
    """

    _inherit = 'project.task'

    objective_id = fields.Many2one(
        comodel_name='goals.goal',
        string='Objetivo Semanal',
        domain="[('period_type', '=', 'week')]",
        index=True,
        help='Objetivo semanal al que contribuye esta tarea directamente.',
        tracking=True,
    )
    is_micro_objective = fields.Boolean(
        string='Es Micro Objetivo',
        default=False,
        help='Marcar si esta tarea representa un micro objetivo diario o una '
             'tarea rápida de enfoque.',
    )
    micro_objective_id = fields.Many2one(
        comodel_name='goals.micro.objective',
        string='Microobjetivo',
        index=True,
        help='Microobjetivo al que contribuye esta tarea.',
        tracking=True,
    )
    goal_id = fields.Many2one(
        comodel_name='goals.goal',
        string='Objetivo estratégico',
        compute='_compute_goal_id',
        store=True,
        index=True,
        help='Objetivo semanal relacionado con esta tarea.',
    )

    @api.depends('objective_id', 'micro_objective_id.goal_id')
    def _compute_goal_id(self):
        for task in self:
            task.goal_id = (
                task.objective_id
                or task.micro_objective_id.goal_id
                or False
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('micro_objective_id') and vals.get('objective_id'):
                vals['objective_id'] = False
        tasks = super(ProjectTask, self).create(vals_list)
        for task in tasks:
            if task.is_closed and (task.micro_objective_id or task.objective_id):
                task._goals_notify_task_completed()
        return tasks

    def write(self, vals):
        # Evitar vinculación simultánea a objetivo directo y microobjetivo.
        if 'micro_objective_id' in vals and vals.get('micro_objective_id'):
            vals['objective_id'] = False
        if 'objective_id' in vals and vals.get('objective_id'):
            vals['micro_objective_id'] = False
        was_closed = {task.id: task.is_closed for task in self}
        result = super(ProjectTask, self).write(vals)
        for task in self:
            if task.is_closed and not was_closed.get(task.id):
                task._goals_notify_task_completed()
        return result

    def _goals_notify_task_completed(self):
        """Hook invocado cuando una tarea pasa a estado cerrado."""
        self.ensure_one()
        if self.env['ir.config_parameter'].sudo().get_param(
            'goals_management.gamification_enabled'
        ):
            xp = int(self.env['ir.config_parameter'].sudo().get_param(
                'goals_management.xp_task', default=10
            ))
            for assignee in self.user_ids:
                assignee.goals_grant_xp(
                    xp,
                    source='task_completed',
                    source_model='project.task',
                    source_res_id=self.id,
                    description=f"Tarea completada: {self.name}",
                )
        self._goals_try_complete_micro_objective()
        self._goals_try_complete_weekly_objective()

    def _goals_try_complete_micro_objective(self):
        """Marca el microobjetivo como done si todas sus tareas están cerradas."""
        self.ensure_one()
        micro = self.micro_objective_id
        if not micro or micro.state in {'done', 'cancelled'}:
            return
        tasks = micro.task_ids.filtered(lambda t: t.active)
        if tasks and all(task.is_closed for task in tasks):
            micro.action_done()

    def _goals_try_complete_weekly_objective(self):
        """Marca el objetivo semanal como done si todo está cerrado.

        El módulo puente de helpdesk puede extender este método para incluir
        tickets en la verificación.
        """
        self.ensure_one()
        goal = self.objective_id
        if not goal or goal.state in {'done', 'cancelled'}:
            return
        if not goal._goals_weekly_can_be_completed():
            return
        goal.action_done()
