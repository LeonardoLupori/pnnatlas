from dash import Dash, dcc, html, Input, Output
from pages import wfa, pv, interactions, genes


app = Dash(__name__)

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', pathname='/wfa', refresh=False),
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/wfa':
        return wfa.layout
    elif pathname == '/pv':
        return pv.layout
    elif pathname == '/interactions':
        return interactions.layout
    elif pathname == '/genes':
        return genes.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)