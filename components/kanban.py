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
            ], className="mb-4 d-flex"),  # Añadimos d-flex a la fila

            # Sección para Estado OR
            dbc.Row([
                dbc.Col(html.H3('Estado OR'), width=12),  # Título de la sección
                dbc.Col(id='kanban-or', className='kanban-column', width=12),  # Contenedor de columnas
            ], className="mb-4 d-flex"),  # Añadimos d-flex a la fila
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

    def get_status_categories(self, status_type):
        query = f"SELECT id, var FROM {status_type}"
        return self.db_connector.fetch_categories(query)

    def create_cards_for_categories(self, projects, categories, status_type, total_columns):
        columns = []
        container_width = 100  # Ancho total del contenedor
        column_width = container_width / total_columns  # Ancho de cada columna

        for i, category in enumerate(categories):
            category_projects = [p for p in projects if getattr(p, status_type) == category['var']]

            # Tarjetas visibles (todas las tarjetas de la categoría)
            visible_cards = [
                dbc.Card(
                    dbc.CardBody([  # Datos del proyecto
                        html.H5(proj.name, className="card-title"),
                        html.P(f"Inicio: {proj.fecha_inicio}", className="card-text"),
                        html.P(f"Código: {proj.code}", className="card-text"),
                    ]),
                    className="mb-2",
                )
                for proj in category_projects
            ]

            # Contenedor para las tarjetas con barra de desplazamiento vertical
            scrollable_container = html.Div(
                visible_cards,
                style={
                    'max-height': '400px',  # Altura máxima antes de que aparezca la barra de desplazamiento
                    'overflow-y': 'auto',  # Habilita la barra de desplazamiento vertical
                }
            )

            # Construcción de la columna por categoría
            columns.append(
                dbc.Col([  # Columna de la categoría
                    dbc.Card(
                        dbc.CardHeader(html.H5(category['var'], className="text-white bg-primary text-center")),
                        className="mb-3",
                    ),
                    scrollable_container,  # Contenedor con desplazamiento
                ], style={'flex': f'1 1 {column_width}%'}, className="px-1")  # Usamos el cálculo del ancho de columna
            )

        # Aseguramos que todas las columnas estén en una sola fila sin envolver
        return dbc.Row(columns, className="g-1 d-flex flex-wrap")
