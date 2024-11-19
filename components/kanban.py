from dash import dcc, html, Input, Output, State
from utils.db import DatabaseConnector
import dash_bootstrap_components as dbc
import dash

class TableroKanban:
    def __init__(self, app):
        self.app = app
        self.db_connector = DatabaseConnector()
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div([ 
            dcc.Store(id='kanban-initialized', data=True),  # Trigger para el callback

            # Sección para Estado Retie (sin borde y con ícono)
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.I(className="bi bi-r-square-fill me-2"),
                        html.H3('Estado Retie')
                    ], className="d-flex align-items-center"),
                    width=12
                ),  # Título de la sección con ícono
                dbc.Col(id='kanban-retie', className='kanban-column', width=12),  # Contenedor de columnas
            ], className="mb-5 d-flex", style={'margin-top': '20px'}),  # Se eliminan los bordes

            # Sección para Estado OR (sin borde y con ícono)
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.I(className="bi bi-plug-fill me-2"),
                        html.H3('Estado OR')
                    ], className="d-flex align-items-center"),
                    width=12
                ),  # Título de la sección con ícono
                dbc.Col(id='kanban-or', className='kanban-column', width=12),  # Contenedor de columnas
            ], className="mb-5 d-flex", style={'margin-top': '20px'}),  # Se eliminan los bordes
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
                p.id, p.name, p.code, p.start_date AS fecha_inicio, p.notes,
                rs.var AS retie_status, os.var AS or_status
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
                    dbc.CardBody([
                        html.H5(f"{proj.code} - {proj.name}", className="card-title"),
                        html.P(f"Inicio: {proj.fecha_inicio}", className="card-text", style={"font-size": "0.9rem"}),
                        html.P(f"{proj.notes}" if proj.notes else "Sin notas", className="card-text"),
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
                    'margin-top': '10px',
                    'border': '1px solid #ccc',  # Agregar borde alrededor del contenedor de tarjetas
                    'padding': '10px',  # Agregar margen superior al contenedor de tarjetas
                }
            )

            # Encabezado de la categoría con estilo Flatly
            category_header = dbc.Badge(
                category['var'], 
                color="success", 
                style={
                    'textAlign': 'center',  # Centrar el texto
                    'fontSize': '1em',     # Aumentar el tamaño de la fuente
                    'width': '100%'         # Asegura que el badge ocupe todo el ancho disponible para el centrado
                }
            )

            # Construcción de la columna por categoría
            columns.append(
                dbc.Col([  # Columna de la categoría
                    category_header,  # Encabezado de la categoría
                    scrollable_container,  # Contenedor con desplazamiento
                ], style={'flex': f'1 1 {column_width}%', 'border': '1px solid #ccc'}, className="px-1 mb-3")
            )

        # Aseguramos que todas las columnas estén en una sola fila sin envolver
        return dbc.Row(columns, className="g-1 d-flex flex-wrap")
