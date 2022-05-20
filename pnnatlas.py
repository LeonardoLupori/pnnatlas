from dash import Dash, dcc, html, Input, Output
from pages import wfa, interactions, genes #, pv


app = Dash(__name__)

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
    # elif pathname == '/pv':
    #     return pv.layout
    elif pathname == '/interactions':
        return interactions.layout
    elif pathname == '/genes':
        return genes.layout
    else:
        return '404'

# This server object will be loaded by the WSGI script to be served as a webapp
# in a production server
server = app.server

# This will only be executed during debug since WSGI does not run this as __main__
if __name__ == '__main__':
    app.run_server(debug=True)