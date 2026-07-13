# -*- coding: utf-8 -*-
from odoo import fields, models


class GoalsLinkTaskWizard(models.TransientModel):
    """Wizard para vincular tareas de proyecto ya existentes a un objetivo semanal."""

    _name = 'goals.link.task.wizard'
    _description = 'Vincular tareas a objetivo'

    goal_id = fields.Many2one(
        comodel_name='goals.goal',
        string='Objetivo semanal',
        required=True,
        domain="[('period_type', '=', 'week')]",
        default=lambda self: self.env.context.get('default_goal_id'),
    )
    task_ids = fields.Many2many(
        comodel_name='project.task',
        relation='goals_link_task_wizard_task_rel',
        column1='wizard_id',
        column2='task_id',
        string='Tareas',
        help='Tareas que se asociarán al objetivo semanal seleccionado.',
    )

    def action_link(self):
        """Asocia las tareas seleccionadas al objetivo semanal."""
        for wizard in self:
            if wizard.goal_id and wizard.task_ids:
                wizard.task_ids.write({'objective_id': wizard.goal_id.id})
        return {'type': 'ir.actions.act_window_close'}
