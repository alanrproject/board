from dash import Dash, dcc, html
from components.schedule import CronogramaSemanal
from components.kanban import TableroKanban
import dash_bootstrap_components as dbc

# Inicialización de la aplicación Dash
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY, "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"])

# Inicialización de las clases
cronograma = CronogramaSemanal(app)
kanban = TableroKanban(app)

# Estructura de la aplicación
app.layout = html.Div([
    # Encabezado con el logo
    html.Header(
        html.Div([
            html.Img(src='/assets/Logo.png', style={'height': '100px', 'width': 'auto', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
        ], className='text-center', style={'padding': '20px'})
    ),
    
    # Pestañas para Cronograma y Kanban
    dcc.Tabs([
        dcc.Tab(label='Cronograma Semanal', children=cronograma.layout),
        dcc.Tab(label='Tablero Kanban', children=kanban.layout)
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)


