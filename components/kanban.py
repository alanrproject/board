from dash import dcc, html, Input, Output
from utils.db import DatabaseConnector

class TableroKanban:
    def __init__(self, app):
        self.app = app
        self.db_connector = DatabaseConnector()
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div([
            # Este es el trigger para el callback
            dcc.Store(id='kanban-initialized', data=True),  # Esto dispara el callback
            # Contenedor principal que será horizontal
            html.Div([
                # Contenedor para Estado Retie
                html.Div([
                    html.H3('Estado Retie'),
                    html.Div(id='kanban-retie', className='kanban-column')  # Contenedor para las categorías de retie
                ], className='kanban-column-container'),

                # Contenedor para Estado OR
                html.Div([
                    html.H3('Estado OR'),
                    html.Div(id='kanban-or', className='kanban-column')  # Contenedor para las categorías de or
                ], className='kanban-column-container'),
            ], className='kanban-sections')  # Usamos 'flex' para alinearlos horizontalmente
        ])


    def register_callbacks(self):
        @self.app.callback(
            [Output('kanban-retie', 'children'),
             Output('kanban-or', 'children')],
            [Input('kanban-initialized', 'data')]  # Este Input es solo para disparar el callback
        )
        def update_kanban(_):
            print("Actualizando Kanban sin filtro dinámico...")
            
            # Query para obtener los datos de los proyectos
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
            
            # Obtener los proyectos desde la base de datos
            projects = self.db_connector.fetch_projects(query)
            print("Proyectos obtenidos:", projects)

            # Obtener categorías de estado de retie_status
            retie_categories = self.get_status_categories('retie_status')
            print(f"Categorías de retie_status: {[category['var'] for category in retie_categories]}")

            # Obtener categorías de estado de or_status
            or_categories = self.get_status_categories('or_status')
            print(f"Categorías de or_status: {[category['var'] for category in or_categories]}")

            # Crear las tarjetas para las categorías de retie_status y or_status
            retie_cards = self.create_cards_for_categories(projects, retie_categories, 'retie_status')
            or_cards = self.create_cards_for_categories(projects, or_categories, 'or_status')

            print(f"Tarjetas Retie creadas: {len(retie_cards)}")
            print(f"Tarjetas OR creadas: {len(or_cards)}")

            return retie_cards, or_cards

    def get_status_categories(self, status_type):
        print(f"Obteniendo categorías de {status_type}...")
        query = f"SELECT id, var FROM {status_type}"
        categories = self.db_connector.fetch_categories(query)
        print(f"Categorías obtenidas: {[category['var'] for category in categories]}")
        return categories

    def create_cards_for_categories(self, projects, categories, status_type):
        print(f"Creando tarjetas para las categorías de {status_type}...")
        cards = []
        
        for category in categories:
            category_projects = [p for p in projects if getattr(p, status_type) == category['var']]
            print(f"Categoría {category['var']} - Proyectos encontrados: {len(category_projects)}")

            # Si no se encuentran proyectos, muestra un mensaje
            if len(category_projects) == 0:
                print(f"No hay proyectos en la categoría: {category['var']}")

            card_elements = [
                html.Div([
                    html.H4(proj.name),  # Usando 'name' en lugar de 'nombre'
                    html.P(f"Inicio: {proj.fecha_inicio}"),
                    html.P(f"Código: {proj.code}")
                ], className="kanban-card") for proj in category_projects
            ]
            
            cards.append(html.Div([
                html.H5(category['var']),
                html.Div(card_elements, className="kanban-card-container")
            ], className="kanban-category"))
        
        print(f"Tarjetas creadas para {status_type}: {len(cards)}")
        return cards



