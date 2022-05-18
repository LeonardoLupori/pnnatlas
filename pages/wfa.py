from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

from pathlib import Path
import pandas as pd

import layoutFunctions as lf
import callbackFunctions as cf
import AbaTool

# ------------------------------------------------------------------------------
# Initialize utility objects and useful functions
# ------------------------------------------------------------------------------

# Object for managing ABA area names and ontology
A = AbaTool.Atlas()

# Utility dict mapping area Ids to names
nameMap = A.get_name_map()

# id function that helps manage component id names. It preprends
# the name of the page to a string so that writing ids specific for each page is easier 
id = cf.id_factory('wfa')          

# Full path of the data folder where to load raw data
dataFolder = Path(__file__).parent.parent.absolute() / 'data'

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------

# Diffuse Fluorescence data for single areas
# Naming is a shorthand for Wfa _ Diffuse _ Coarse/Mid/Fine
w_d_c = pd.read_csv(dataFolder / 'wfa_diff_coarse.csv', header=[0,1], index_col=[0])
w_d_m = pd.read_csv(dataFolder / 'wfa_diff_mid.csv', header=[0,1], index_col=[0,1])
w_d_f = pd.read_csv(dataFolder / 'wfa_diff_fine.csv', header=[0,1], index_col=[0,1,2])

# Data for the coronal slices heatmaps
w_d_sliceList = cf.loadAllSlices(dataFolder / 'wfa' / 'coronalSlices_diffuse')


# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------

# Create lists of dictionaries {label:areaName, value=areaID} for populating dropdowns
coarseDict = cf.dataFrame_to_labelDict(w_d_c,'coarse',nameMap)
midDict = cf.dataFrame_to_labelDict(w_d_m,'mid',nameMap)
fineDict = cf.dataFrame_to_labelDict(w_d_f,'fine',nameMap)



# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------
layout = dbc.Container([
    lf.makeCitationOffCanvas(),
    dbc.Row(lf.makeNavBar()),           # Navigation Bar
    dbc.Row(lf.makeWfaHeader()),            # Big header
    
    # First portion (Diffuse Fluorescence)
    dbc.Row([lf.makeSubtitle('Diffuse WFA Fluorescence')]),
    dbc.Row([
        dbc.Col(lf.makeDiffuseHistogramSelectionMenu(id, coarseDict, midDict, fineDict),
            xs=12,lg=4
        ),
        dbc.Col(
            dbc.Spinner(
                dcc.Graph(id=id('hist_diffuse')),
                color='primary'
            )
        )
    ]),
    dbc.Row([lf.makeCollapsableTable(id)]),

    # Second portion (single PNNs)
    dbc.Row([lf.makeSubtitle('Perineuronal Nets')]),

    # Third portion (anatomical explorer)
    dbc.Row([lf.makeSubtitle('Anatomical explorer')]),
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
    ]),

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
    combinedDf = cf.combineDiffuseDataframes(maj_sel,addC_sel,addM_sel,addF_sel,w_d_c,w_d_m,w_d_f)
    aggrDf = cf.aggregateFluoDataframe(combinedDf, A)
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
def updateAnatomicalExplorer(fig, dataset, cmap, clims, apIdx):
    fig = cf.redrawAnatExplorerScatter(fig, w_d_sliceList[apIdx], cmap, clims[0],clims[1])
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
    Output(component_id='offCanv_cite', component_property='is_open'),
    Input(component_id='btn_citeHeader',component_property='n_clicks'),
    State(component_id='offCanv_cite', component_property='is_open'),
    prevent_initial_call=True
)
def invertCiteMenuVisibility(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open
