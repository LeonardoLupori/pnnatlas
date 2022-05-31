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
id = cf.id_factory('wfa')          

# Full path of the data folder where to load raw data
dataFolder = Path(__file__).parent.parent.absolute() / 'data'

# Load the Atlas dataFrame with all structures, acronyms, colors etc
structuresDf = cf.loadStructuresDf(dataFolder/'structures.json')

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------

D = cf.loadData(dataFolder/'fluorescence', staining='wfa')

# Coronal Slice Coordinates
coronalCoordDfList = cf.loadAllSlices(dataFolder/'coordinates')

# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------

# Create lists of dictionaries {label:areaName, value=areaID} for populating dropDowns
coarseDict = cf.dataFrame_to_labelDict(D['wfa_diffuse_coarse'],'coarse',structuresDf)
midDict = cf.dataFrame_to_labelDict(D['wfa_diffuse_mid'],'mid',structuresDf)
fineDict = cf.dataFrame_to_labelDict(D['wfa_diffuse_fine'],'fine',structuresDf)



# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------
layout = dbc.Container([
    lf.makeCitationOffCanvas(id),
    lf.makeMetricInfoModal(id),
    dbc.Row(lf.makeNavBar()),               # Navigation Bar
    dbc.Row(lf.makeWfaHeader(id)),            # Big header

    # First portion (anatomical explorer)
    dbc.Row([
        dbc.Col(lf.makeAnatomicalExplorerSelectionMenu(id),
            xs=12,lg=3
        ),
        dbc.Col(
            dbc.Spinner(
                dcc.Graph(
                    figure=cf.makeAnatExplorerScatter(),
                    id=id('scatterSlice'),
                ),
                color='primary',
            )
        )
    ], className = 'align-items-center'),

    # Second portion (Histogram)
    dbc.Row([lf.makeSubtitle('Comparative analysis')]),
    dbc.Row([
        dbc.Col(lf.makeDiffuseHistogramSelectionMenu(id, coarseDict, midDict, fineDict),
            xs=12,lg=4, className='mt-5'
        ),
        dbc.Col(
            dbc.Spinner(
                dcc.Graph(id=id('hist_diffuse')),
                color='primary'
            )
        )
    ]),
    dbc.Row([lf.makeCollapsableTable(id)]),

    dbc.Row([],style={"margin-top": "500px"}),
])


# ------------------------------------------------------------------------------
# CALLBACKS
# ------------------------------------------------------------------------------

@callback(
    Output(component_id=id('hist_diffuse'), component_property='figure'),
    Output(component_id=id('collps_diffTab'), component_property='children'),
    Input(component_id=id('drpD_majorSubd'), component_property='value'),
    Input(component_id=id('drpD_addCoarse'), component_property='value'),
    Input(component_id=id('drpD_addMid'), component_property='value'),
    Input(component_id=id('drpD_addFine'), component_property='value'),
    Input(component_id=id('switch_sortDiff'), component_property='value')
)
def updateHistogram(maj_sel,addC_sel,addM_sel,addF_sel, sortRegions):
    """Update the diffuse fluorescence histogram"""
    combinedDf = cf.combineDiffuseDataframes(maj_sel,addC_sel,addM_sel,addF_sel,
        D['wfa_diffuse_coarse'],
        D['wfa_diffuse_mid'],
        D['wfa_diffuse_fine'])
    aggrDf = cf.aggregateFluoDataframe(combinedDf, structuresDf)
    if sortRegions:
        aggrDf = aggrDf.sort_values(by='mean',ascending=False)

    fig = cf.diffuseFluoHistogram(aggrDf)
    tab = dbc.Table.from_dataframe(aggrDf.drop(columns=['color']), striped=True, bordered=True, hover=True)
    return fig, tab

@callback(
    Output(component_id=id('scatterSlice'), component_property='figure'),
    State(component_id=id('scatterSlice'), component_property='figure'),
    Input(component_id=id('drpD_anatomDataset'),component_property='value'),
    Input(component_id=id('drpD_anatomCmap'),component_property='value'),
    Input(component_id=id('slider_clims'),component_property='value'),
    Input(component_id=id('slider_ap'),component_property='value'),
)
def updateAnatomicalExplorer(fig, datasetLabel, cmap, clims, apIdx):

    # Select which dataset to show
    if datasetLabel=='diffuse':
        data = D['wfa_diffuse_mid']
    elif datasetLabel=='density':
        pass
        # data = w_den_m
    elif datasetLabel=='intensity':
        pass
        # data = w_int_m
    elif datasetLabel=='energy':
        pass
        # data = w_ene_m

    df = cf.mergeCoordinatesAndData(coronalCoordDfList[apIdx], data)
    fig = cf.redrawAnatExplorerScatter(fig, df, cmap, clims[0],clims[1])
    return fig

@callback(
    Output(component_id=id('collps_diffTab'), component_property='is_open'),
    Output(component_id=id('btn_openTabDiffuse'), component_property='children'),
    Output(component_id=id('btn_openTabDiffuse'), component_property='color'),
    Input(component_id=id('btn_openTabDiffuse'),component_property='n_clicks'),
    State(component_id=id('collps_diffTab'), component_property='is_open'),
    prevent_initial_call=True
)
def invertTabVisibility( _ , previousState):
    newState = not previousState
    if newState:
        text = 'Collapse Tabular Data'
        color = 'info'
    else:
        text = 'Open Tabular Data'
        color = 'primary'
    return newState, text, color
    

@callback(
    Output(component_id=id('drpD_addCoarse'), component_property='value'),
    Input(component_id=id('btn_allMajorDiff'),component_property='n_clicks'),
    prevent_initial_call=True
)
def addAllCoarseDiffuse(n_clicks):
    coarseIDs = [x['value'] for x in coarseDict]
    return coarseIDs


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

@callback(
    Output(component_id=id('modal_info'), component_property='is_open'),
    Input(component_id=id('btn_info'),component_property='n_clicks'),
    State(component_id=id('modal_info'), component_property='is_open'),
)
def invertModalInfoVisibility(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open