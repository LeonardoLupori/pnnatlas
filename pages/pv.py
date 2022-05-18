from dash import dcc, Input, Output, State, callback
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

# iDify function that helps manage component id names. It preprends
# the name of the page to a string so that writing ids specific for each page is easier 
id = cf.id_factory('pv')          

# Full path of the data folder where to load raw data
dataFolder = Path(__file__).parent.parent.absolute() / 'data'

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------

# Naming is a shorthand for PV _ Diffuse _ Coarse/Mid/Fine
p_d_c = pd.read_csv(dataFolder / 'pv_diff_coarse.csv', header=[0,1], index_col=[0])
p_d_m = pd.read_csv(dataFolder / 'pv_diff_mid.csv', header=[0,1], index_col=[0,1])
p_d_f = pd.read_csv(dataFolder / 'pv_diff_fine.csv', header=[0,1], index_col=[0,1,2])



# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------
coarseDict = cf.dataFrame_to_labelDict(p_d_c,'coarse',nameMap)
midDict = cf.dataFrame_to_labelDict(p_d_m,'mid',nameMap)
fineDict = cf.dataFrame_to_labelDict(p_d_f,'fine',nameMap)



# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------
layout = dbc.Container([
    lf.makeCitationOffCanvas(),
    dbc.Row(lf.makeNavBar()),           # Navigation Bar
    dbc.Row(lf.makePVHeader()),            # Big header
    
    # First portion (Diffuse Fluorescence)
    dbc.Row([lf.makeSubtitle('Diffuse PV Fluorescence')]),
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
    dbc.Row([lf.makeSubtitle('Anatomical explorer')]),
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
    combinedDf = cf.combineDiffuseDataframes(maj_sel,addC_sel,addM_sel,addF_sel,p_d_c,p_d_m,p_d_f)
    aggrDf = cf.aggregateFluoDataframe(combinedDf, A)
    if sortRegions:
        aggrDf = aggrDf.sort_values(by='mean',ascending=False)

    fig = cf.diffuseFluoHistogram(aggrDf)
    tab = dbc.Table.from_dataframe(aggrDf.drop(columns=['color']), striped=True, bordered=True, hover=True)
    return fig, tab

@callback(
    Output(component_id=id('drpD_addCoarse'), component_property='value'),
    Input(component_id=id('btn_allMajorDiff'),component_property='n_clicks'),
    prevent_initial_call=True
)
def addAllCoarseDiffuse(n_clicks):
    coarseIDs = [x['value'] for x in coarseDict]
    return coarseIDs