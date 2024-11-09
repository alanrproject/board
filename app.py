from dash import Dash, dcc, html
from components.schedule import CronogramaSemanal
from components.kanban import TableroKanban

# Inicialización de la aplicación Dash
app = Dash(__name__, suppress_callback_exceptions=True)

# Inicialización de las clases
cronograma = CronogramaSemanal(app)
kanban = TableroKanban(app)

# Estructura de la aplicación con pestañas
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Cronograma Semanal', children=cronograma.layout),
        dcc.Tab(label='Tablero Kanban', children=kanban.layout)
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)


