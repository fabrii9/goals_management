# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    """Extensión de tareas de proyecto para vincularlas a microobjetivos."""

    _inherit = 'project.task'

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
        related='micro_objective_id.goal_id',
        store=True,
        index=True,
        help='Objetivo semanal relacionado con esta tarea.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super(ProjectTask, self).create(vals_list)
        for task in tasks:
            if task.micro_objective_id and task.is_closed:
                task._goals_notify_task_completed()
        return tasks

    def write(self, vals):
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
            if self.user_id:
                self.user_id.goals_grant_xp(
                    xp,
                    source='task_completed',
                    source_model='project.task',
                    source_res_id=self.id,
                    description=f"Tarea completada: {self.name}",
                )
        self._goals_try_complete_micro_objective()

    def _goals_try_complete_micro_objective(self):
        """Marca el microobjetivo como done si todas sus tareas están cerradas."""
        self.ensure_one()
        micro = self.micro_objective_id
        if not micro or micro.state in {'done', 'cancelled'}:
            return
        tasks = micro.task_ids.filtered(lambda t: t.active)
        if tasks and all(task.is_closed for task in tasks):
            micro.action_done()
