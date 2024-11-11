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
        @self.app.callback(
            Output('kanban-output', 'children'),
            [Input('kanban-status-dropdown', 'value')]
        )
        def update_kanban(selected_status):
            projects = self.db_connector.fetch_projects()
            filtered_projects = [p for p in projects if p.estado == selected_status]
            return [
                html.Div([
                    html.H4(proj.nombre),
                    html.P(f"Inicia: {proj.fecha_inicio}, Fin: {proj.fecha_fin}")
                ], className="kanban-card") for proj in filtered_projects
            ]