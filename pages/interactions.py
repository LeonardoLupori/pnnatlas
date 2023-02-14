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
id = cf.id_factory('interactions')          

# Full path of the data folder where to load raw data
dataFolder = Path(__file__).parent.parent.absolute() / 'data'

# Load the Atlas dataFrame with all structures, acronyms, colors etc
structuresDf = cf.loadStructuresDf(dataFolder/'structures.json')

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------

# Metrics data for WFA
Dw = dm.readSupplDataMetrics(dataFolder/'originalData/data_SD1.xlsx', removeAcronyms=True)
Dp = dm.readSupplDataMetrics(dataFolder/'originalData/data_SD2.xlsx', removeAcronyms=True)
Dc = dm.readSupplDataMetrics(dataFolder/'originalData/data_SD3.xlsx', removeAcronyms=True)

# Coronal Slice Coordinates
coronalCoordDfList = cf.loadAllSlices(dataFolder/'coordinates')

# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------

# Create lists of dictionaries {label:areaName, value=areaID} for populating dropDowns
coarseDict = cf.dataFrame_to_labelDict(Dc['coarse'],'coarse',structuresDf)
midDict = cf.dataFrame_to_labelDict(Dc['mid'],'mid',structuresDf)
fineDict = cf.dataFrame_to_labelDict(Dc['fine'],'fine',structuresDf)


# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------


layout = dbc.Container([
    lf.make_CitationOffCanvas(id),
    lf.make_ColocInfoModal(id),
    dbc.Row(lf.make_NavBar()),                           # Navigation Bar
    dbc.Row(lf.make_InteractionHeader(id)),            # Big header

    #

    dbc.Row([lf.make_Subtitle('Correlation between metrics')]),
    dbc.Row([
        dbc.Col([
            lf.make_InteractionSelectionMenu(id)
        ],xs=12,lg=3),
        dbc.Col([
            dbc.Spinner(
                dcc.Graph(
                    figure=cf.makeInteractionScatter(),
                    id=id('scatter'),
                    config= {'displaylogo': False}
                ),color='primary'
            ),
            # lf.make_AreasChecklist(id, coarseDict),
        ])
    ], className = 'align-items-center'),

    dbc.Row([lf.make_Subtitle('Colocalization')]),
    dbc.Row([
        dbc.Col(lf.make_ColocalizationHistogramSelectionMenu(id, coarseDict, midDict, fineDict),
            xs=12,lg=4, className='mt-5'
        ),
        dbc.Col(
            dbc.Spinner(
                dcc.Graph(id=id('hist_coloc'), config={'displaylogo':False}),
                color='primary'
            )
        )
    ]),
    dbc.Row([lf.make_CollapsableTable(id)]),


    dbc.Row([],style={"margin-top": "500px"}),
])



@callback(
    Output(component_id=id('scatter'), component_property='figure'),
    State(component_id=id('scatter'), component_property='figure'),
    Input(component_id=id('drpD_xStaining'), component_property='value'),
    Input(component_id=id('drpD_xMetric'), component_property='value'),
    Input(component_id=id('drpD_yStaining'), component_property='value'),
    Input(component_id=id('drpD_yMetric'), component_property='value'),
    Input(component_id=id('switch_zScore'), component_property='value')
)
def updateScatter(fig, xStaining, xMetric, yStaining, yMetric, zScore):    
    xData = cf.selectData(Dw, Dp, xStaining, xMetric, 'mid')
    yData = cf.selectData(Dw, Dp, yStaining, yMetric, 'mid')
    aggrDf = cf.intScattAggregateData(structuresDf, xData, yData, zScore)

    fig = cf.update_IntScatter(fig, aggrDf, structuresDf, xStaining, xMetric, yStaining, yMetric, zScore)

    return fig


@callback(
    Output(component_id=id('hist_coloc'), component_property='figure'),
    Output(component_id=id('collps_Tab'), component_property='children'),
    Input(component_id=id('drpD_Metric'), component_property='value'),
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
    slicedCoarse = Dc['coarse'].xs(selMetric, axis=1, level='params')
    slicedMid = Dc['mid'].xs(selMetric, axis=1, level='params')
    slicedFine = Dc['fine'].xs(selMetric, axis=1, level='params')
    # Combine data from all the area selected from multiple menus
    combinedDf = cf.combineDiffuseDataframes(maj_sel, addC_sel, addM_sel, addF_sel,
        slicedCoarse, slicedMid, slicedFine)
    # Aggregate to calculate Mean and SEM
    aggrDf = cf.aggregateFluoDataframe(combinedDf, structuresDf)
    if sortRegions:
        aggrDf = aggrDf.sort_values(by='mean',ascending=False)

    print(aggrDf)
    # Create a new visualization and table and return them
    fig = cf.update_colocHistogram(aggrDf, selMetric)
    tab = dbc.Table.from_dataframe(aggrDf.drop(columns=['color']), striped=True, bordered=True, hover=True)
    return fig, tab


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
def addAllColocHist(n_clicks):
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
