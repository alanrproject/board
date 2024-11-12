from dash import dcc, html, Input, Output
from datetime import datetime, timedelta
import plotly.graph_objects as go
from utils.db import DatabaseConnector

class CronogramaSemanal:
    def __init__(self, app):
        self.app = app
        self.db_connector = DatabaseConnector()
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        # Define el layout para la pestaña de cronograma semanal, agregando el gráfico
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
            SELECT pt.project_id, p.name AS project_name, pt.start_date, pt.end_date, pt.notes
            FROM `project-tasks` pt
            JOIN projects p ON pt.project_id = p.id
            WHERE pt.start_date >= '{start_of_week.strftime('%Y-%m-%d')}'
            AND pt.start_date <= '{end_of_week.strftime('%Y-%m-%d')}'
            AND pt.is_deleted != 1
            """

            data = self.db_connector.fetch_project_tasks(query)
            print("Datos obtenidos de la base de datos:", data)

            # Procesar los datos para el gráfico
            tasks = []
            task_names = []
            task_start_dates = []
            task_end_dates = []
            task_durations = []

            for projecttask in data:
                project_id = projecttask.project_id
                project_name = projecttask.project_name
                start_date = projecttask.start_date
                end_date = projecttask.end_date
                notes = projecttask.notes

                # Calcular la duración de la tarea en días
                task_duration = (end_date - start_date).days + 1  # Duración de la tarea en días

                # Agregar los valores a las listas
                tasks.append(project_id)
                task_names.append(project_name)
                task_start_dates.append(start_date)
                task_end_dates.append(end_date)
                task_durations.append(task_duration)

            # Crear las fechas en formato adecuado para el gráfico
            dates = [start_of_week + timedelta(days=i) for i in range(6)]  # Lunes a Sábado
            date_labels = [date.strftime('%d/%m/%Y') for date in dates]

            # Crear el gráfico de líneas
            traces = []
            for i, task in enumerate(task_names):
                start_day = (task_start_dates[i] - start_of_week).days  # Días desde el inicio de la semana
                end_day = (task_end_dates[i] - start_of_week).days

                # Agregar una línea para cada tarea
                traces.append(go.Scatter(
                    x=[start_day, end_day],
                    y=[i, i],
                    mode='lines+markers',
                    name=task,
                    line=dict(width=4),
                    marker=dict(size=8)
                ))

            fig = go.Figure(data=traces)

            # Actualizar el gráfico
            return dcc.Graph(
                id='schedule-graph',
                figure=fig
            )
