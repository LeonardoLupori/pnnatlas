from dash import html, Input, Output, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1("Sorry! We couldn't find this page! :(", className='text-center'),
            dbc.Card([
                dbc.CardImg(
                    src="assets/image404.png",
                    top=True,
                    style={"opacity": 0.8},
                )
            ]),
            ],width={'size':4,'offset':4}
        )
    ], className='my-5'),

    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button("Go Back!", id='btn_backToWfa', size='lg', color='primary')
            ],className='d-grid gap-2 col-6 mx-auto'
            )
        ],width={'size':8,'offset':2})
    ],className='my-5')
])


@callback(
    Output(component_id='url', component_property='pathname'),
    Input(component_id='btn_backToWfa', component_property='n_clicks'),
    prevent_initial_call=True
)
def goBackToWfa(n_clicks):
    # prevent_initial_call alone is not enough here: the output ('url') lives in the
    # outer layout, so Dash still fires this callback when the 404 page is inserted,
    # which silently rewrote the URL to /wfa while the 404 page stayed on screen.
    if not n_clicks:
        raise PreventUpdate
    return '/wfa'

