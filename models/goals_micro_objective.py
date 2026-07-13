# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GoalsMicroObjective(models.Model):
    """Microobjetivo operativo vinculado a tareas de proyecto.

    Representa la hoja de ejecución de la jerarquía de objetivos. Su avance
    se calcula directamente a partir de las tareas completadas que contiene.
    """

    _name = 'goals.micro.objective'
    _description = 'Microobjetivo'
    _order = 'priority desc, date_end, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATES = [
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('done', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]

    IMPACTS = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
    ]

    PROGRESS_MODES = [
        ('auto', 'Automático'),
        ('manual', 'Manual'),
    ]

    # -------------------------------------------------------------------------
    # Campos principales
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        index=True,
        tracking=True,
    )
    description = fields.Html(
        string='Descripción',
        sanitize=True,
    )
    goal_id = fields.Many2one(
        comodel_name='goals.goal',
        string='Objetivo Semanal',
        domain="[('period_type', '=', 'week')]",
        index=True,
        required=True,
        tracking=True,
    )
    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='micro_objective_id',
        string='Tareas',
    )

    # -------------------------------------------------------------------------
    # Planificación y responsables
    # -------------------------------------------------------------------------
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        index=True,
        required=True,
        tracking=True,
    )
    team_member_ids = fields.Many2many(
        comodel_name='res.users',
        relation='goals_micro_objective_team_members_rel',
        column1='micro_objective_id',
        column2='user_id',
        string='Equipo',
    )
    date_start = fields.Date(
        string='Fecha de inicio',
        required=True,
        index=True,
    )
    date_end = fields.Date(
        string='Fecha de fin',
        required=True,
        index=True,
    )
    state = fields.Selection(
        selection=STATES,
        string='Estado',
        default='draft',
        tracking=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Priorización y categorización
    # -------------------------------------------------------------------------
    priority = fields.Selection(
        selection=[
            ('0', 'Ninguna'),
            ('1', 'Baja'),
            ('2', 'Media'),
            ('3', 'Alta'),
            ('4', 'Muy alta'),
            ('5', 'Crítica'),
        ],
        string='Prioridad',
        default='0',
        help='Prioridad del 0 al 5.',
    )
    impact = fields.Selection(
        selection=IMPACTS,
        string='Impacto',
        default='medium',
        tracking=True,
    )
    weight = fields.Float(
        string='Peso',
        default=1.0,
        help='Peso relativo dentro del objetivo semanal.',
    )
    category_id = fields.Many2one(
        comodel_name='goals.category',
        string='Categoría',
        index=True,
    )
    tag_ids = fields.Many2many(
        comodel_name='goals.tag',
        relation='goals_micro_objective_tag_rel',
        column1='micro_objective_id',
        column2='tag_id',
        string='Etiquetas',
    )
    color = fields.Integer(
        string='Color',
        default=0,
    )

    # -------------------------------------------------------------------------
    # Progreso
    # -------------------------------------------------------------------------
    progress_mode = fields.Selection(
        selection=PROGRESS_MODES,
        string='Modo de progreso',
        default='auto',
        tracking=True,
    )
    manual_progress = fields.Float(
        string='Progreso manual (%)',
        default=0.0,
    )
    progress = fields.Float(
        string='Progreso (%)',
        compute='_compute_progress',
        store=True,
        help='Porcentaje de avance calculado desde las tareas vinculadas.',
    )

    # -------------------------------------------------------------------------
    # Indicadores
    # -------------------------------------------------------------------------
    tasks_count = fields.Integer(
        string='Cantidad de tareas',
        compute='_compute_tasks_count',
        store=True,
    )
    completed_tasks_count = fields.Integer(
        string='Tareas completadas',
        compute='_compute_tasks_count',
        store=True,
    )
    is_overdue = fields.Boolean(
        string='Vencido',
        compute='_compute_is_overdue',
        store=True,
    )

    # -------------------------------------------------------------------------
    # Multiempresa
    # -------------------------------------------------------------------------
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        index=True,
        default=lambda self: self.env.company,
        required=True,
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        index=True,
    )

    _check_date_range = models.Constraint(
        "CHECK (date_end >= date_start)",
        "La fecha de fin debe ser mayor o igual a la fecha de inicio.",
    )
    _check_weight_positive = models.Constraint(
        "CHECK (weight > 0)",
        "El peso debe ser mayor a cero.",
    )
    _check_progress_range = models.Constraint(
        "CHECK (progress >= 0 AND progress <= 100)",
        "El progreso debe estar entre 0 y 100.",
    )

    @api.constrains('goal_id')
    def _check_goal_is_weekly(self):
        for micro in self:
            if micro.goal_id and micro.goal_id.period_type != 'week':
                raise ValidationError(_(
                    "El microobjetivo debe estar vinculado a un objetivo semanal."
                ))

    # -------------------------------------------------------------------------
    # Cómputo de progreso
    # -------------------------------------------------------------------------
    @api.depends(
        'progress_mode',
        'manual_progress',
        'task_ids.is_closed',
        'task_ids.stage_id',
    )
    def _compute_progress(self):
        for micro in self:
            if micro.progress_mode == 'manual':
                micro.progress = max(0.0, min(100.0, micro.manual_progress))
                continue
            completed, total = micro._get_progress_contributions()
            micro.progress = (
                (completed / total) * 100.0 if total else 0.0
            )

    def _get_progress_contributions(self):
        """Retorna (completados, total) de elementos de avance.

        Diseñado para ser extendido por otros módulos (por ejemplo, helpdesk)
        agregando más fuentes de progreso.
        """
        self.ensure_one()
        tasks = self.task_ids
        completed = sum(1 for task in tasks if task.is_closed)
        return completed, len(tasks)

    # -------------------------------------------------------------------------
    # Indicadores
    # -------------------------------------------------------------------------
    @api.depends('task_ids', 'task_ids.is_closed')
    def _compute_tasks_count(self):
        for micro in self:
            micro.tasks_count = len(micro.task_ids)
            micro.completed_tasks_count = sum(
                1 for task in micro.task_ids if task.is_closed
            )

    @api.depends('date_end', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for micro in self:
            micro.is_overdue = (
                micro.state in {'draft', 'active'}
                and micro.date_end
                and micro.date_end < today
            )

    # -------------------------------------------------------------------------
    # Write y automatización
    # -------------------------------------------------------------------------
    def write(self, vals):
        result = super(GoalsMicroObjective, self).write(vals)
        if vals.get('state') == 'done':
            self._goals_grant_completion_xp()
            self._goals_try_complete_weekly_goal()
        return result

    def _goals_grant_completion_xp(self):
        """Otorga XP al completar un microobjetivo si la gamificación está activa."""
        if not self.env['ir.config_parameter'].sudo().get_param(
            'goals_management.gamification_enabled'
        ):
            return
        xp = int(self.env['ir.config_parameter'].sudo().get_param(
            'goals_management.xp_micro', default=50
        ))
        if self.user_id:
            self.user_id.goals_grant_xp(
                xp,
                source='micro_objective_completed',
                source_model='goals.micro.objective',
                source_res_id=self.id,
                description=f"Microobjetivo completado: {self.name}",
            )

    def _goals_try_complete_weekly_goal(self):
        """Marca el objetivo semanal como completado si todos sus micros lo están."""
        for micro in self:
            if not micro.goal_id:
                continue
            siblings = micro.goal_id.micro_objective_ids.filtered(
                lambda m: m.state != 'cancelled'
            )
            if siblings and all(m.state == 'done' for m in siblings):
                micro.goal_id.action_done()

    # -------------------------------------------------------------------------
    # Acciones
    # -------------------------------------------------------------------------
    def action_activate(self):
        self.filtered(lambda m: m.state == 'draft').write({'state': 'active'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
