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
            # Rango de fechas para la semana de lunes a sábado
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())  # Lunes
            end_of_week = start_of_week + timedelta(days=6)  # Sábado

            # Consulta SQL para obtener tareas de la semana
            query = f"""
            SELECT pt.project_id, p.name AS project_name, pt.start_date, pt.end_date, pt.notes
            FROM `project-tasks` pt
            JOIN projects p ON pt.project_id = p.id
            WHERE (pt.start_date >= '{start_of_week.strftime('%Y-%m-%d')}' 
                   AND pt.start_date <= '{end_of_week.strftime('%Y-%m-%d')}')
            OR (pt.end_date >= '{start_of_week.strftime('%Y-%m-%d')}' 
                AND pt.end_date <= '{end_of_week.strftime('%Y-%m-%d')}')
            AND pt.is_deleted != 1
            """
            data = self.db_connector.fetch_project_tasks(query)
            print("Datos obtenidos de la base de datos:", data)

            # Procesar los datos para el gráfico
            task_names = []
            task_start_dates = []
            task_end_dates = []

            for projecttask in data:
                project_name = projecttask.project_name
                start_date = projecttask.start_date
                end_date = projecttask.end_date
                task_names.append(project_name)
                task_start_dates.append(start_date)
                task_end_dates.append(end_date)

            # Crear etiquetas y fechas de lunes a sábado
            dates = [start_of_week + timedelta(days=i) for i in range(7)]  # Incluye el sábado
            date_labels = [f'{day} {date.strftime("%d/%m/%Y")}' for day, date in zip(
                ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'], dates)]

            # Crear los trazos del gráfico
            traces = []
            y_positions = [i * 1.5 for i in range(len(task_names))]  # Espaciado amplio en Y
            for i, task in enumerate(task_names):
                start_day = max(0, (task_start_dates[i] - start_of_week).days)
                end_day = min(6, (task_end_dates[i] - start_of_week).days)  # Incluye hasta el sábado

                if start_day == end_day:
                    traces.append(go.Scatter(
                        x=[start_day, start_day + 0.8],  # Línea de un día de duración
                        y=[y_positions[i], y_positions[i]],
                        mode='lines+markers+text',
                        line=dict(width=20),
                        marker=dict(size=8),
                        text=[task],
                        textposition="middle right"
                    ))
                else:
                    mid_point = (start_day + end_day) / 2
                    traces.append(go.Scatter(
                        x=[start_day, end_day],
                        y=[y_positions[i], y_positions[i]],
                        mode='lines+markers',
                        line=dict(width=20),
                        marker=dict(size=8)
                    ))
                    traces.append(go.Scatter(
                        x=[mid_point],
                        y=[y_positions[i]],
                        mode='text',
                        text=[task],
                        textposition="middle center",
                        showlegend=False
                    ))

            fig = go.Figure(data=traces)

            # Configuración del layout del gráfico
            fig.update_layout(
                xaxis=dict(
                    tickmode="array",
                    tickvals=[i - 0.25 for i in range(7)],  # Desplazar etiquetas a la izquierda
                    ticktext=date_labels,
                    title="Día de la Semana",
                    side='top',  # Etiquetas del eje X en la parte superior
                    range=[-0.5, 6.5]
                ),
                yaxis=dict(
                    title_text="",  # Sin título para el eje Y
                    showticklabels=False,  # Quitar etiquetas del eje Y
                    range=[-1, max(y_positions) + 1],  # Ajuste para dar espacio extra
                ),
                title="Cronograma Semanal",
                showlegend=False,
                height=600
            )

            return dcc.Graph(
                id='schedule-graph',
                figure=fig
            )
