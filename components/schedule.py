from dash import dcc, html, Input, Output
from datetime import datetime, timedelta
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
                    {'label': 'Opción 1', 'value': 'value1'},
                    {'label': 'Opción 2', 'value': 'value2'}
                ],
                placeholder="Selecciona una opción"
            ),
            html.Div(id='schedule-output', className='tab-content')
        ])


    def register_callbacks(self):
        # Define el callback para actualizar el cronograma semanal
        @self.app.callback(
            Output('schedule-output', 'children'),
            [Input('schedule-dropdown', 'value')]
        )
        def update_schedule(_):
            # Obtener los proyectos programados para la semana actual de lunes a sábado
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())  # Lunes
            end_of_week = start_of_week + timedelta(days=5)  # Sábado

            query = f"""
            SELECT pt.project_id, pt.start_date, pt.end_date, pt.notes
            FROM `project-tasks` pt
            JOIN projects p ON pt.project_id = p.id
            WHERE pt.start_date >= '{start_of_week.strftime('%Y-%m-%d')}'
            AND pt.start_date <= '{end_of_week.strftime('%Y-%m-%d')}'
            AND pt.is_deleted != 1
            """

            data = self.db_connector.fetch_project_tasks(query)
            print("Datos obtenidos de la base de datos:", data)

            # Crear elementos HTML para mostrar los proyectos
            schedule_content = []
            for projecttask in data:
                # Accede a los atributos de cada objeto ProjectTask
                project_id = projecttask.project_id
                start_date = projecttask.start_date  # O 'start_date' si usas ese nombre en la clase
                end_date = projecttask.end_date  # O 'end_date' si usas ese nombre en la clase
                notes = projecttask.notes  # O 'notes' si usas ese nombre en la clase

                schedule_content.append(html.Div([
                    html.H4(f"Proyecto ID: {project_id}"),
                    html.P(f"Fecha de inicio: {start_date.strftime('%d/%m/%Y')}"),
                    html.P(f"Fecha de fin: {end_date.strftime('%d/%m/%Y')}"),
                    html.P(f"Notas: {notes}"),
                    html.Hr()
                ]))

            return schedule_content if schedule_content else "No hay proyectos programados esta semana."
