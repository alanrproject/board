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
        # Obtener la estructura del calendario
        days_of_week = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        
        # Crear el layout básico del calendario
        calendar_layout = html.Div([
            # Cabecera con los días de la semana
            html.Div([
                html.Div(day, className="calendar-header") for day in days_of_week
            ], className="calendar-header-row"),

            # Contenedores para cada día de la semana
            html.Div([
                html.Div([], id=f'calendar-day-{i}', className="calendar-day") 
                for i in range(6)
            ], className="calendar-days")
        ], className="calendar-container")

        # Define el layout para la pestaña de cronograma semanal, agregando el calendario
        return html.Div([
            dcc.Dropdown(
                id='schedule-dropdown',
                options=[
                    {'label': 'Opción 1', 'value': 'value1'},
                    {'label': 'Opción 2', 'value': 'value2'}
                ],
                placeholder="Selecciona una opción"
            ),
            html.Div(id='schedule-output', className='tab-content', children=calendar_layout)
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

            # Crear el layout del calendario
            days_of_week = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
            calendar_layout = html.Div([
                # Cabecera con los días de la semana
                html.Div([
                    html.Div(day, className="calendar-header") for day in days_of_week
                ], className="calendar-header-row"),

                # Contenedores para cada día de la semana
                html.Div([
                    html.Div([], id=f'calendar-day-{i}', className="calendar-day") 
                    for i in range(6)
                ], className="calendar-days")
            ], className="calendar-container")

            # Asignar las tareas a los días correspondientes
            for projecttask in data:
                project_id = projecttask.project_id
                project_name = projecttask.project_name
                start_date = projecttask.start_date
                end_date = projecttask.end_date
                notes = projecttask.notes

                # Encontrar el día correspondiente a la fecha de inicio
                day_index = (start_date.weekday())  # 0 = Lunes, 1 = Martes, ..., 5 = Sábado

                # Calcular la duración de la tarea
                task_duration = (end_date - start_date).days + 1  # Duración de la tarea en días

                # Crear el contenido de la tarea
                task_content = html.Div([
                    html.P(f"ID: {project_id}"),
                    html.P(f"Nombre: {project_name}"),
                    html.P(f"Fecha de inicio: {start_date.strftime('%d/%m/%Y')}"),
                    html.P(f"Fecha de fin: {end_date.strftime('%d/%m/%Y')}"),
                    html.P(f"Notas: {notes}"),
                ], className="task-content", style={"width": f"{task_duration * 1}%"} )

                # Colocar la tarea en el día correspondiente
                calendar_layout.children[1].children[day_index].children.append(task_content)

            return calendar_layout
