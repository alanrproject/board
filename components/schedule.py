from dash import dcc, html, Input, Output
from utils.db import DatabaseConnector

class CronogramaSemanal:
    def __init__(self, app):
        self.app = app
        self.db_connector = DatabaseConnector()
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        # Define el layout para la pestaña de cronograma semanal
        return html.Div([
            dcc.Dropdown(
                id='schedule-dropdown',
                options=[
                    {'label': 'Semana 1', 'value': 'week1'},
                    {'label': 'Semana 2', 'value': 'week2'},
                ],
                placeholder="Selecciona una semana"
            ),
            html.Div(id='schedule-output', className='tab-content')
        ])

    def register_callbacks(self):
        # Define el callback para actualizar el cronograma
        @self.app.callback(
            Output('schedule-output', 'children'),
            [Input('schedule-dropdown', 'value')]
        )
        def update_schedule(selected_week):
            # Lógica para actualizar el cronograma basado en la semana seleccionada
            query = f"SELECT * FROM schedule WHERE week = '{selected_week}'"
            data = self.db_connector.fetch_data(query)
            return f"Cronograma para la {selected_week}: {data}"

