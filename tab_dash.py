


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Tabs(id="app-tabs", value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),
              Input('app-tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Content of Tab one'),
            # Add your components for Tab one here
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Content of Tab two'),
            # Add your components for Tab two here
        ])

if __name__ == '__main__':
    app.run_server(debug=True)