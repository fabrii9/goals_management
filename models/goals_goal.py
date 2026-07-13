# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GoalsGoal(models.Model):
    """Objetivo estratégico con jerarquía recursiva.

    Un mismo modelo representa los niveles anual, trimestral, mensual y
    semanal. La relación padre/hijo define la jerarquía y el progreso se
    propaga automáticamente desde las hojas operativas (microobjetivos y
    tareas) hasta la meta anual.
    """

    _name = 'goals.goal'
    _description = 'Objetivo'
    _order = 'period_type desc, date_start desc, priority desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    PERIOD_TYPES = [
        ('year', 'Anual'),
        ('quarter', 'Trimestral'),
        ('month', 'Mensual'),
        ('week', 'Semanal'),
    ]

    PERIOD_RANK = {
        'year': 4,
        'quarter': 3,
        'month': 2,
        'week': 1,
    }

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
    period_type = fields.Selection(
        selection=PERIOD_TYPES,
        string='Tipo de Período',
        required=True,
        index=True,
        default='week',
        tracking=True,
    )
    parent_id = fields.Many2one(
        comodel_name='goals.goal',
        string='Objetivo Padre',
        index=True,
        tracking=True,
        domain="[('period_type', 'in', allowed_parent_period_types)]",
        help='Objetivo de nivel superior al que contribuye este objetivo.',
    )
    child_ids = fields.One2many(
        comodel_name='goals.goal',
        inverse_name='parent_id',
        string='Subobjetivos',
    )
    allowed_parent_period_types = fields.Json(
        string='Tipos de padre permitidos',
        compute='_compute_allowed_parent_period_types',
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
        relation='goals_goal_team_members_rel',
        column1='goal_id',
        column2='user_id',
        string='Equipo',
        help='Miembros del equipo que participan en este objetivo.',
    )
    date_start = fields.Date(
        string='Fecha de inicio',
        required=True,
        index=True,
        tracking=True,
    )
    date_end = fields.Date(
        string='Fecha de fin',
        required=True,
        index=True,
        tracking=True,
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
        help='Prioridad del 0 al 5. Mayor valor indica mayor prioridad.',
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
        help='Peso relativo al calcular el progreso del objetivo padre.',
    )
    category_id = fields.Many2one(
        comodel_name='goals.category',
        string='Categoría',
        index=True,
    )
    tag_ids = fields.Many2many(
        comodel_name='goals.tag',
        relation='goals_goal_tag_rel',
        column1='goal_id',
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
        recursive=True,
        help='Porcentaje de avance calculado automáticamente o definido '
             'manualmente.',
    )
    micro_objective_ids = fields.One2many(
        comodel_name='goals.micro.objective',
        inverse_name='goal_id',
        string='Microobjetivos',
    )
    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='objective_id',
        string='Tareas',
    )

    # -------------------------------------------------------------------------
    # Indicadores computados
    # -------------------------------------------------------------------------
    tasks_count = fields.Integer(
        string='Tareas vinculadas',
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
    # IA-ready (preparación para futuras funciones de inteligencia artificial)
    # -------------------------------------------------------------------------
    ai_suggested_priority = fields.Integer(
        string='Prioridad sugerida por IA',
        default=0,
        help='Campo reservado para futuras recomendaciones de IA.',
    )
    ai_stuck_score = fields.Float(
        string='Índice de estancamiento',
        default=0.0,
        help='Campo reservado para detectar objetivos estancados.',
    )
    ai_estimated_end_date = fields.Date(
        string='Fecha estimada de fin (IA)',
        help='Campo reservado para estimaciones de IA.',
    )

    # -------------------------------------------------------------------------
    # Multiempresa y utilidades
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

    # -------------------------------------------------------------------------
    # Constraints y validaciones
    # -------------------------------------------------------------------------
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

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        """Evita ciclos y garantiza que el padre sea de nivel superior."""
        for goal in self:
            if not goal.parent_id:
                continue
            # El padre debe tener un periodo de mayor jerarquía.
            if (self.PERIOD_RANK[goal.parent_id.period_type]
                    <= self.PERIOD_RANK[goal.period_type]):
                raise ValidationError(_(
                    "El objetivo padre debe ser de un período superior."
                ))
            # Evitar ciclos.
            current = goal.parent_id
            visited = {goal.id}
            while current:
                if current.id in visited:
                    raise ValidationError(_(
                        "No se permite crear ciclos en la jerarquía de objetivos."
                    ))
                visited.add(current.id)
                current = current.parent_id

    @api.depends('period_type')
    def _compute_allowed_parent_period_types(self):
        """Determina qué tipos de periodo pueden ser padre del actual."""
        for goal in self:
            rank = self.PERIOD_RANK.get(goal.period_type, 0)
            goal.allowed_parent_period_types = [
                key for key, value in self.PERIOD_RANK.items() if value > rank
            ]

    # -------------------------------------------------------------------------
    # Cómputo de progreso
    # -------------------------------------------------------------------------
    @api.depends(
        'progress_mode',
        'manual_progress',
        'child_ids.progress',
        'child_ids.weight',
        'micro_objective_ids.progress',
        'micro_objective_ids.weight',
        'task_ids.is_closed',
    )
    def _compute_progress(self):
        """Calcula el progreso según el modo y los hijos/microobjetivos/tareas."""
        for goal in self:
            if goal.progress_mode == 'manual':
                goal.progress = max(0.0, min(100.0, goal.manual_progress))
                continue

            if goal.period_type == 'week':
                goal.progress = goal._compute_progress_from_weekly_items()
            else:
                goal.progress = goal._compute_progress_from_children()

    def _compute_progress_from_children(self):
        """Promedio ponderado de progresos de subobjetivos."""
        self.ensure_one()
        children = self.child_ids.filtered(lambda g: g.state != 'cancelled')
        if not children:
            return 0.0
        total_weight = sum(children.mapped('weight'))
        if not total_weight:
            return 0.0
        weighted_progress = sum(
            child.weight * child.progress for child in children
        )
        return min(100.0, max(0.0, weighted_progress / total_weight))

    def _compute_progress_from_weekly_items(self):
        """Promedio ponderado de microobjetivos, tareas y tickets."""
        self.ensure_one()
        contributions = self._get_weekly_progress_contributions()
        if not contributions:
            return 0.0
        total_weight = sum(weight for _, _, weight in contributions)
        if not total_weight:
            return 0.0
        weighted_progress = sum(
            ((completed / total) * 100.0 if total else 0.0) * weight
            for completed, total, weight in contributions
        )
        return min(100.0, max(0.0, weighted_progress / total_weight))

    def _get_weekly_progress_contributions(self):
        """Retorna lista de (completados, total, peso) para el cálculo.

        Diseñado para ser extendido por el módulo de helpdesk y agregar
        contribuciones de tickets.
        """
        self.ensure_one()
        contributions = []
        micros = self.micro_objective_ids.filtered(
            lambda m: m.state != 'cancelled'
        )
        for micro in micros:
            contributions.append((micro.progress / 100.0, 1.0, micro.weight))
        tasks = self.task_ids.filtered(lambda t: t.active)
        if tasks:
            completed = sum(1 for task in tasks if task.is_closed)
            contributions.append((completed, len(tasks), 1.0))
        return contributions

    # -------------------------------------------------------------------------
    # Indicadores
    # -------------------------------------------------------------------------
    @api.depends(
        'micro_objective_ids.task_ids',
        'micro_objective_ids.task_ids.is_closed',
        'task_ids',
        'task_ids.is_closed',
    )
    def _compute_tasks_count(self):
        for goal in self:
            tasks = goal.micro_objective_ids.mapped('task_ids') | goal.task_ids
            goal.tasks_count = len(tasks)
            goal.completed_tasks_count = sum(
                1 for task in tasks if task.is_closed
            )

    @api.depends('date_end', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for goal in self:
            goal.is_overdue = (
                goal.state in {'draft', 'active'}
                and goal.date_end
                and goal.date_end < today
            )

    def _goals_weekly_can_be_completed(self):
        """Verifica si el objetivo semanal puede marcarse como completado.

        Retorna True si todas las tareas directas están cerradas y todos los
        microobjetivos activos están completos. El módulo puente de helpdesk
        extiende este método para incluir tickets.
        """
        self.ensure_one()
        if self.period_type != 'week':
            return False
        tasks = self.task_ids.filtered(lambda t: t.active)
        all_tasks_closed = all(task.is_closed for task in tasks) if tasks else True
        micros = self.micro_objective_ids.filtered(lambda m: m.state != 'cancelled')
        all_micros_done = all(m.state == 'done' for m in micros) if micros else True
        has_items = tasks or micros
        return has_items and all_tasks_closed and all_micros_done

    # -------------------------------------------------------------------------
    # Write y automatización
    # -------------------------------------------------------------------------
    def write(self, vals):
        result = super(GoalsGoal, self).write(vals)
        if vals.get('state') == 'done':
            self._goals_grant_completion_xp()
            self._goals_try_complete_parent()
        return result

    def _goals_grant_completion_xp(self):
        """Otorga XP según el tipo de período al completar un objetivo."""
        if not self.env['ir.config_parameter'].sudo().get_param(
            'goals_management.gamification_enabled'
        ):
            return
        param_map = {
            'week': 'goals_management.xp_week',
            'month': 'goals_management.xp_month',
            'quarter': 'goals_management.xp_month',
            'year': 'goals_management.xp_month',
        }
        param = param_map.get(self.period_type, 'goals_management.xp_week')
        xp = int(self.env['ir.config_parameter'].sudo().get_param(
            param, default=300
        ))
        if self.user_id:
            self.user_id.goals_grant_xp(
                xp,
                source=f'{self.period_type}_objective_completed',
                source_model='goals.goal',
                source_res_id=self.id,
                description=f"Objetivo {self.period_type} completado: {self.name}",
            )

    def _goals_try_complete_parent(self):
        """Marca el padre como completado si todos sus hijos activos lo están."""
        for goal in self:
            parent = goal.parent_id
            if not parent:
                continue
            siblings = parent.child_ids.filtered(
                lambda g: g.state != 'cancelled'
            )
            if siblings and all(g.state == 'done' for g in siblings):
                parent.action_done()

    # -------------------------------------------------------------------------
    # Métodos de utilidad
    # -------------------------------------------------------------------------
    def action_activate(self):
        self.filtered(lambda g: g.state == 'draft').write({'state': 'active'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    # -------------------------------------------------------------------------
    # IA-ready stubs
    # -------------------------------------------------------------------------
    def action_suggest_priority(self):
        """Hook para futura sugerencia de prioridades mediante IA."""
        self.ensure_one()
        # TODO: integrar modelo de IA en futura versión.
        return True

    def action_detect_stuck(self):
        """Hook para detectar objetivos estancados."""
        self.ensure_one()
        # TODO: integrar heurística o modelo de IA en futura versión.
        return True

    def action_estimate_end_date(self):
        """Hook para estimar fecha de finalización mediante IA."""
        self.ensure_one()
        # TODO: integrar modelo de IA en futura versión.
        return True
