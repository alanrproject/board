from dash import dcc, html, Input, Output, State
from utils.db import DatabaseConnector
import dash_bootstrap_components as dbc

class TableroKanban:
    def __init__(self, app):
        self.app = app
        self.db_connector = DatabaseConnector()
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div([
            dcc.Store(id='kanban-initialized', data=True),  # Trigger para el callback

            # Sección para Estado Retie
            dbc.Row([
                dbc.Col(html.H3('Estado Retie'), width=12),  # Título de la sección
                dbc.Col(id='kanban-retie', className='kanban-column', width=12),  # Contenedor de columnas
            ], className="mb-4"),  # Margen inferior

            # Sección para Estado OR
            dbc.Row([
                dbc.Col(html.H3('Estado OR'), width=12),  # Título de la sección
                dbc.Col(id='kanban-or', className='kanban-column', width=12),  # Contenedor de columnas
            ], className="mb-4"),  # Margen inferior
        ])

    def register_callbacks(self):
        # Callback principal para cargar el contenido de las categorías
        @self.app.callback(
            [Output('kanban-retie', 'children'),
             Output('kanban-or', 'children')],
            [Input('kanban-initialized', 'data')]  # Trigger
        )
        def update_kanban(_):
            # Obtener datos de los proyectos
            query = """SELECT 
                p.id,
                p.name,
                p.code,
                p.start_date AS fecha_inicio, 
                rs.var AS retie_status,
                os.var AS or_status
            FROM 
                projects p
            JOIN 
                project_details_status pds ON p.id = pds.project_id
            LEFT JOIN 
                retie_status rs ON pds.retie_id = rs.id
            LEFT JOIN 
                or_status os ON pds.or_id = os.id
            """
            projects = self.db_connector.fetch_projects(query)

            # Obtener las categorías
            retie_categories = self.get_status_categories('retie_status')
            or_categories = self.get_status_categories('or_status')

            # Crear tarjetas por categoría
            retie_cards = self.create_cards_for_categories(projects, retie_categories, 'retie_status', 5)  # 5 columnas
            or_cards = self.create_cards_for_categories(projects, or_categories, 'or_status', 7)  # 7 columnas

            return retie_cards, or_cards

        # Callbacks dinámicos para expandir/colapsar las categorías
        for i, category_type in enumerate(['retie_status', 'or_status']):
            @self.app.callback(
                Output(f"collapse-{category_type}-{i}", "is_open"),
                Input(f"toggle-button-{category_type}-{i}", "n_clicks"),
                State(f"collapse-{category_type}-{i}", "is_open"),
            )
            def toggle_collapse(n_clicks, is_open):
                if n_clicks:
                    return not is_open
                return is_open

    def get_status_categories(self, status_type):
        query = f"SELECT id, var FROM {status_type}"
        return self.db_connector.fetch_categories(query)

    def create_cards_for_categories(self, projects, categories, status_type, total_columns):
        columns = []
        column_width = max(12 // total_columns, 1)  # Calcula el ancho de cada columna (mínimo 1)

        for i, category in enumerate(categories):
            category_projects = [p for p in projects if getattr(p, status_type) == category['var']]

            # Proyectos visibles y ocultos
            visible_projects = category_projects[:4]
            hidden_projects = category_projects[4:]

            # Tarjetas visibles
            visible_cards = [
                dbc.Card(
                    dbc.CardBody([
                        html.H5(proj.name, className="card-title"),
                        html.P(f"Inicio: {proj.fecha_inicio}", className="card-text"),
                        html.P(f"Código: {proj.code}", className="card-text"),
                    ]),
                    className="mb-2",
                )
                for proj in visible_projects
            ]

            # Tarjetas ocultas (en Collapse)
            hidden_cards = [
                dbc.Card(
                    dbc.CardBody([
                        html.H5(proj.name, className="card-title"),
                        html.P(f"Inicio: {proj.fecha_inicio}", className="card-text"),
                        html.P(f"Código: {proj.code}", className="card-text"),
                    ]),
                    className="mb-2",
                )
                for proj in hidden_projects
            ]

            # Collapse para proyectos ocultos
            collapse = dbc.Collapse(
                hidden_cards,
                id=f"collapse-{status_type}-{i}",
                is_open=False,
            )

            # Botón para mostrar/ocultar
            toggle_button = dbc.Button(
                "Mostrar más",
                id=f"toggle-button-{status_type}-{i}",
                color="link",
                n_clicks=0,
            )

            # Construcción de la columna por categoría
            columns.append(
                dbc.Col([
                    dbc.Card(
                        dbc.CardHeader(html.H5(category['var'], className="text-white bg-primary text-center")),
                        className="mb-3",
                    ),
                    *visible_cards,
                    collapse,
                    toggle_button,
                ], width=column_width, className="px-1")  # Reducimos espacio horizontal
            )

        # Aseguramos que todas las columnas estén en una sola fila sin envolver
        return dbc.Row(columns, className="g-1 d-flex flex-nowrap overflow-auto")









