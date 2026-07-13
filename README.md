# Goals Management System

Sistema de Gestión de Objetivos para Odoo 19.

## Arquitectura

### Modelo recursivo unificado

La jerarquía de objetivos estratégicos (anual, trimestral, mensual, semanal) se
modela con un único modelo `goals.goal` y los campos `period_type`, `parent_id`
y `child_ids`.

**Ventajas:**
- Menor duplicación de código y lógica.
- Reportes unificados (pivot, graph, dashboard).
- Escalable: nuevos períodos solo requieren un valor de selección.
- Propagación de progreso mediante un único método recursivo.

### Microobjetivos como hoja operativa

`goals.micro.objective` es la unidad de ejecución vinculada a `project.task`.
Permite que las tareas apunten a un único microobjetivo sin perder la
jerarquía estratégica.

### Gamificación desacoplada

La gamificación vive en modelos separados (`goals.xp.log`, `goals.badge`,
`goals.user.badge`) y en la extensión de `res.users`. Se activa mediante
configuración global y no afecta la lógica de negocio.

### Módulo puente para helpdesk

La integración con `helpdesk` se realiza en un módulo independiente
`goals_management_helpdesk` con `auto_install`. Esto evita forzar la
dependencia Enterprise y mantiene el módulo core usable en Community.

### Preparación para IA

Se incluyen campos y métodos stub (`ai_suggested_priority`,
`ai_stuck_score`, `ai_estimated_end_date`) para futuras funciones de
inteligencia artificial.

## Estructura

```
goals_management/
├── models/          # Modelos Python
├── security/        # Grupos, ACL y reglas
├── views/           # Vistas XML
├── data/            # Datos demo y secuencias
├── static/src/      # Componentes OWL y SCSS
├── controllers/     # Endpoints para dashboard
├── tests/           # Tests unitarios
└── README.md        # Este archivo
```

## Instalación

```bash
python odoo-bin -c odoo.conf -d <database> -i goals_management
```

Para activar la integración con helpdesk (si está instalado):

```bash
python odoo-bin -c odoo.conf -d <database> -i goals_management_helpdesk
```

## Tests

```bash
python odoo-bin -c odoo.conf -d <database> --stop-after-init --test-enable --test-tags=goals_management
```
