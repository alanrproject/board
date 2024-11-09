from dash import dcc, html, Input, Output
from utils.db import DatabaseConnector

class TableroKanban:
    def __init__(self, app):
        self.app = app
        self.db_connector = DatabaseConnector()
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        # Define el layout para la pestaña Kanban
        return html.Div([
            dcc.Dropdown(
                id='kanban-status-dropdown',
                options=[
                    {'label': 'Pendiente', 'value': 'pending'},
                    {'label': 'En Progreso', 'value': 'in_progress'},
                    {'label': 'Completado', 'value': 'completed'},
                ],
                placeholder="Selecciona un estado"
            ),
            html.Div(id='kanban-output', className='tab-content')
        ])

    def register_callbacks(self):
        # Define el callback para actualizar el tablero Kanban
        @self.app.callback(
            Output('kanban-output', 'children'),
            [Input('kanban-status-dropdown', 'value')]
        )
        def update_kanban(selected_status):
            # Lógica para actualizar el tablero Kanban basado en el estado seleccionado
            query = f"SELECT * FROM tasks WHERE status = '{selected_status}'"
            data = self.db_connector.fetch_data(query)
            return f"Tareas para el estado {selected_status}: {data}"


