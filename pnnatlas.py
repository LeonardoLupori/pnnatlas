if not __package__:
    # Run as a plain script (e.g. "python pnnatlas.py"): the relative imports below
    # would fail with a cryptic ImportError, so explain how to start the atlas instead.
    raise SystemExit(
        "Start the atlas with:  python -m pnnatlas\n"
        "(run it from the folder that contains the pnnatlas folder)"
    )

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from .pages import wfa, genes, pv, blankPage, interactions


app = Dash(__name__,
    title="PNN Atlas",
    external_stylesheets=[dbc.icons.FONT_AWESOME]
)

indexLayout = html.Div([
    # No initial pathname here: setting one would override the URL the user opened,
    # breaking direct links to /pv, /genes, etc. The root path is routed to WFA below.
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Create a "complete" layout for validating all callbacks. Otherwise when dash tries
# to validate them, most of them will throw an error since they are linked to
# components that are not currently on the displayed page and so are not part of the 
# current layout
app.validation_layout = html.Div([
    indexLayout,
    wfa.layout,
    pv.layout,
    interactions.layout,
    genes.layout,
    blankPage.layout
])

# This is the actual layout of the app
app.layout = indexLayout

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname in ('/', '/wfa', None):
        return wfa.layout
    elif pathname == '/pv':
        return pv.layout
    elif pathname == '/interactions':
        return interactions.layout
    elif pathname == '/genes':
        return genes.layout
    else:
        return blankPage.layout


# This server object will be loaded by the WSGI script to be served as a webapp
# in a production server. It is also re-exported by __init__.py, so both
# "pnnatlas:server" and "pnnatlas.pnnatlas:server" work as WSGI entry points.
server = app.server


# This module only defines the app. To run the development server locally use
# "python -m pnnatlas" (see __main__.py). Running this file directly would load
# the app twice, so point people to the right command instead.
if __name__ == '__main__':
    raise SystemExit(
        "Start the atlas with:  python -m pnnatlas\n"
        "(run it from the folder that contains the pnnatlas folder)"
    )
