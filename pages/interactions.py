from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

from pathlib import Path
import pandas as pd

from utils import layoutFunctions as lf
from utils import callbackFunctions as cf

# ------------------------------------------------------------------------------
# Initialize utility objects and useful functions
# ------------------------------------------------------------------------------

# id function that helps manage component id names. It pre-pends
# the name of the page to a string so that writing ids specific for each page is easier 
id = cf.id_factory('inter')          

# Full path of the data folder where to load raw data
dataFolder = Path(__file__).parent.parent.absolute() / 'data'

# Load the Atlas dataframe with all structures, acronyms, colors etc
structuresDf = cf.loadStructuresDf(dataFolder/'structures.json')

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------

# Diffuse Fluorescence data for single areas
D = cf.loadData(dataFolder/'fluorescence', resolution='mid')


# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------

# Create lists of dictionaries {label:areaName, value=areaID}
# coarseDict = cf.dataFrame_to_labelDict(D['wfa_diffuse_coarse'],'coarse',structuresDf)


# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------


layout = dbc.Container([
    lf.makeCitationOffCanvas(id),
    dbc.Row(lf.makeNavBar()),               # Navigation Bar
    dbc.Row(lf.makeInteractionHeader(id)),            # Big header


    dbc.Row([
        dbc.Col([
            lf.makeInteractionSelectionMenu(id)
        ],xs=12,lg=3),
        dbc.Col([
            
            dbc.Spinner(
                dcc.Graph(
                    figure=cf.makeInteractionScatter(),
                    id=id('scatter'),
                ),color='primary'
            ),
            # lf.makeAreasChecklist(id, coarseDict),
        ])
    ], className = 'align-items-center'),
    dbc.Row([],style={"margin-top": "500px"}),
])



@callback(
    Output(component_id=id('scatter'), component_property='figure'),
    State(component_id=id('scatter'), component_property='figure'),
    Input(component_id=id('drpD_xStaining'), component_property='value'),
    Input(component_id=id('drpD_xMetric'), component_property='value'),
    Input(component_id=id('drpD_yStaining'), component_property='value'),
    Input(component_id=id('drpD_yMetric'), component_property='value'),
)
def updateScatter(fig, xStaining,xMetric,yStaining,yMetric):    
    xData = cf.selectData(D, xStaining, xMetric, 'mid')
    yData = cf.selectData(D, yStaining, yMetric, 'mid')
    aggrDf = cf.intScattAggregateData(structuresDf, xData, yData)

    fig = cf.redrawIntScatter(fig, aggrDf, structuresDf, xStaining,xMetric,yStaining,yMetric)

    return fig

@callback(
    Output(component_id=id('offCanv_cite'), component_property='is_open'),
    Input(component_id=id('btn_citeHeader'),component_property='n_clicks'),
    State(component_id=id('offCanv_cite'), component_property='is_open'),
    prevent_initial_call=True
)
def invertCiteMenuVisibility(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open