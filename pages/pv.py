from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

from pathlib import Path
import pandas as pd

from ..utils import dataManager as dm
from ..utils import layoutFunctions as lf
from ..utils import callbackFunctions as cf


# ------------------------------------------------------------------------------
# Initialize utility objects and useful functions
# ------------------------------------------------------------------------------

# id function that helps manage component id names. It pre-pends
# the name of the page to a string so that writing ids specific for each page is easier 
id = cf.id_factory('pv')          

# Full path of the data folder where to load raw data
dataFolder = Path(__file__).parent.parent.absolute() / 'data'

# Load the Atlas dataFrame with all structures, acronyms, colors etc
structuresDf = cf.loadStructuresDf(dataFolder/'structures.json')

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------

# Metrics data for WFA
D = dm.readSupplDataMetrics(dataFolder/'originalData/data_SD2.xlsx', removeAcronyms=True)

# Coronal Slice Coordinates
coronalCoordDfList = cf.loadAllSlices(dataFolder/'coordinates')

# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------

# Create lists of dictionaries {label:areaName, value=areaID} for populating dropDowns
coarseDict = cf.dataFrame_to_labelDict(D['coarse'],'coarse',structuresDf)
midDict = cf.dataFrame_to_labelDict(D['mid'],'mid',structuresDf)
fineDict = cf.dataFrame_to_labelDict(D['fine'],'fine',structuresDf)



# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------
layout = dbc.Container([
    lf.make_CitationOffCanvas(id),
    lf.make_AboutUsOffCanvas(id),
    lf.make_MetricInfoModal(id),
    dbc.Row(lf.make_NavBar()),                  # Navigation Bar
    dbc.Row(lf.make_PvHeader(id)),             # Big header

    # First portion (anatomical explorer)
    dbc.Row([
        dbc.Col(lf.make_AnatomicalExplorerSelectionMenu(id, staining='pv'),
            xs=12,lg=3
        ),
        dbc.Col(
            dbc.Spinner(
                dcc.Graph(
                    figure=cf.makeAnatExplorerScatter(),
                    id=id('scatterSlice'),
                    config={'displaylogo':False}
                ),
                color='primary',
            )
        )
    ], className = 'align-items-center'),

    # Second portion (Histogram)
    dbc.Row([lf.make_Subtitle('Comparative analysis')]),
    dbc.Row([
        dbc.Col(lf.make_MetricsHistogramSelectionMenu(id, coarseDict, midDict, fineDict,'pv'),
            xs=12,lg=4, className='mt-5'
        ),
        dbc.Col(
            dbc.Spinner(
                dcc.Graph(id=id('hist_diffuse'), config={'displaylogo':False}),
                color='primary'
            )
        )
    ]),
    dbc.Row([lf.make_CollapsableTable(id)]),
    dbc.Row([lf.make_CC_licenseBanner(id)]),

    dbc.Row([],style={"margin-top": "500px"}),
])


# ------------------------------------------------------------------------------
# CALLBACKS
# ------------------------------------------------------------------------------

@callback(
    Output(component_id=id('hist_diffuse'), component_property='figure'),
    Output(component_id=id('collps_Tab'), component_property='children'),
    Input(component_id=id('drpD_histogMetric'), component_property='value'),
    Input(component_id=id('drpD_majorSubd'), component_property='value'),
    Input(component_id=id('drpD_addCoarse'), component_property='value'),
    Input(component_id=id('drpD_addMid'), component_property='value'),
    Input(component_id=id('drpD_addFine'), component_property='value'),
    Input(component_id=id('switch_sortDiff'), component_property='value')
)
def updateHistogram(selMetric, maj_sel, addC_sel, addM_sel, addF_sel, sortRegions):
    """
    Update the diffuse fluorescence histogram
    """
    # Filter data for the selected metric only
    slicedCoarse = D['coarse'].xs(selMetric, axis=1, level='params')
    slicedMid = D['mid'].xs(selMetric, axis=1, level='params')
    slicedFine = D['fine'].xs(selMetric, axis=1, level='params')
    # Combine data from all the area selected from multiple menus
    combinedDf = cf.combineDiffuseDataframes(maj_sel,addC_sel,addM_sel,addF_sel,
        slicedCoarse,
        slicedMid,
        slicedFine)
    # Aggregate to calculate Mean and SEM
    aggrDf = cf.aggregateFluoDataframe(combinedDf, structuresDf)
    if sortRegions:
        aggrDf = aggrDf.sort_values(by='mean',ascending=False)

    # Create a new visualization and table and return them
    fig = cf.update_diffuseFluoHistogram(aggrDf, selMetric, 'pv')
    tab = dbc.Table.from_dataframe(aggrDf.drop(columns=['color']), striped=True, bordered=True, hover=True)
    return fig, tab


@callback(
    Output(component_id=id('scatterSlice'), component_property='figure'),
    State(component_id=id('scatterSlice'), component_property='figure'),
    Input(component_id=id('drpD_anatomMetric'),component_property='value'),
    Input(component_id=id('drpD_anatomCmap'),component_property='value'),
    Input(component_id=id('slider_ap'),component_property='value'),
)
def updateAnatomicalExplorer(fig, selMetric, cmap, apIdx):
    """
    Update the anatomical explore plot with the data selected from the multiple
    sliders and dropdown menus on the left.
    """
    # Select which dataset to show
    data = D['mid'].xs(selMetric, axis=1, level='params')
    # Get the correct limits to the colormap
    min, max, = cf.getClimsAnatomicalExplorer(selMetric, staining='pv')

    df = cf.mergeCoordinatesAndData(coronalCoordDfList[apIdx], data)
    fig = cf.redrawAnatExplorerScatter(fig, df, cmap, min, max)

    return fig


@callback(
    Output(component_id=id('collps_Tab'), component_property='is_open'),
    Output(component_id=id('btn_openTabDiffuse'), component_property='children'),
    Output(component_id=id('btn_openTabDiffuse'), component_property='color'),
    Input(component_id=id('btn_openTabDiffuse'),component_property='n_clicks'),
    State(component_id=id('collps_Tab'), component_property='is_open'),
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
    Input(component_id='citeDropdown', component_property='n_clicks'),
    State(component_id=id('offCanv_cite'), component_property='is_open'),
    prevent_initial_call=True
)
def invertCiteMenuVisibility(n_clicks, n_clicks_dropdown, is_open):
    if n_clicks or n_clicks_dropdown:
        return not is_open
    return is_open


@callback(
    Output(component_id=id('offCanv_abtUs'), component_property='is_open'),
    Input(component_id='aboutUsDropdown', component_property='n_clicks'),
    State(component_id=id('offCanv_abtUs'), component_property='is_open'),
    prevent_initial_call=True
)
def invertAboutusMenuVisibility(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output(component_id=id('modal_info'), component_property='is_open'),
    Input(component_id=id('btn_info_anat'),component_property='n_clicks'),
    Input(component_id=id('btn_info'),component_property='n_clicks'),
    State(component_id=id('modal_info'), component_property='is_open'),
)
def invertModalInfoVisibility(n_clicks_anat, n_clicks, is_open):
    if n_clicks or n_clicks_anat:
        return not is_open
    return is_open

@callback(
    Output(component_id=id('moreInfoCollapse'), component_property='is_open'),
    Input(component_id=id('moreInfoIcon'), component_property='n_clicks'),
    State(component_id=id('moreInfoCollapse'), component_property='is_open'),
    prevent_initial_call=True
)
def invertMoreInfoVisibility(n_clicks, is_open):
    if n_clicks:
            return not is_open
    return is_open
