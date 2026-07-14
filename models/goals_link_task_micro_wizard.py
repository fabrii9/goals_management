# -*- coding: utf-8 -*-
from odoo import fields, models


class GoalsLinkTaskMicroWizard(models.TransientModel):
    """Wizard para vincular tareas de proyecto ya existentes a un microobjetivo."""

    _name = 'goals.link.task.micro.wizard'
    _description = 'Vincular tareas a microobjetivo'

    micro_objective_id = fields.Many2one(
        comodel_name='goals.micro.objective',
        string='Microobjetivo',
        required=True,
        default=lambda self: self.env.context.get('default_micro_objective_id'),
    )
    task_ids = fields.Many2many(
        comodel_name='project.task',
        relation='goals_link_task_micro_wizard_task_rel',
        column1='wizard_id',
        column2='task_id',
        string='Tareas',
        help='Tareas que se asociarán al microobjetivo seleccionado.',
    )

    def action_link(self):
        """Asocia las tareas seleccionadas al microobjetivo."""
        for wizard in self:
            if wizard.micro_objective_id and wizard.task_ids:
                wizard.task_ids.write({
                    'micro_objective_id': wizard.micro_objective_id.id,
                    'objective_id': False,
                })
        return {'type': 'ir.actions.act_window_close'}
