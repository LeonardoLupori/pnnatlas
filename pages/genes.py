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
id = cf.id_factory('genes')          

# Full path of the data folder where to load raw data
dataFolder = Path(__file__).parent.parent.absolute() / 'data'

# Load the Atlas dataFrame with all structures, acronyms, colors etc
structuresDf = cf.loadStructuresDf(dataFolder/'structures.json')

# ------------------------------------------------------------------------------
# Load the necessary data
# ------------------------------------------------------------------------------

# Metrics data for WFA and PV
wfa = dm.readMetricsDataForGenes(dataFolder/'originalData/data_SD1.xlsx')
pv = dm.readMetricsDataForGenes(dataFolder/'originalData/data_SD2.xlsx')
# Load Genes data
geneDict = dm.readGenesCorrelationSupplData(dataFolder/'originalData/data_SD4.xlsx')
# genesDf = df = pd.read_excel(dataFolder/'originalData/data_SD4.xlsx', header=0, index_col=0)

# Load ISH data
ish_en =  pd.read_csv(dataFolder/'gene_expression_ABA_energy.csv', index_col=0)
ish_en.columns = pd.to_numeric(ish_en.columns)



# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------
layout = dbc.Container([
    lf.make_CitationOffCanvas(id),
    lf.make_AboutUsOffCanvas(id),
    lf.make_GeneInfoModal(id),
    dbc.Row(lf.make_NavBar()),                  # Navigation Bar
    dbc.Row(lf.make_GenesHeader(id)),             # Big header

    # # Second portion (Histogram)
    dbc.Row([lf.make_Subtitle('Explore correlations')]),
    dbc.Row([
        dbc.Col(lf.make_GeneCorrSelectionMenu(id, geneDict['wfa_en']),
            xs=12,lg=4, className='mt-5'
        ),
        dbc.Col(
            dbc.Spinner(
                dcc.Graph(
                    figure=cf.make_GeneScatter(),
                    id=id('corrPlot'), config={'displaylogo':False}, className='mt-3'),
                color='primary'
            )
        )
    ]),
    # dbc.Row([lf.make_CollapsableTable(id)]),
    dbc.Row([lf.make_CC_licenseBanner(id)]),

    dbc.Row([],style={"margin-top": "500px"}),
])



@callback(
    Output(component_id=id('corrPlot'), component_property='figure'),
    Output(component_id=id('collps_Tab'), component_property='children'),
    State(component_id=id('corrPlot'), component_property='figure'),
    Input(component_id=id('drpD_geneSelect'), component_property='value'),
    Input(component_id=id('drpD_metricSelector'), component_property='value'),
)
def updateGenecorr(fig, selGene, selMetric):
    # Update the table with Gene info
    g, geneName = cf.getGeneInfoTable(selMetric, selGene, geneDict)
    tab = dbc.Table.from_dataframe(g, striped=True, bordered=True, hover=True)

    metricData = cf.getMetricDf(selMetric, wfa, pv)
    aggreDf = cf.combineGenesDf(selGene, metricData, ish_en, structuresDf)
    fig = cf.update_GenesScatter(fig, aggreDf, structuresDf, geneName)

    return fig, tab


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
    Output(component_id=id('moreInfoCollapse'), component_property='is_open'),
    Input(component_id=id('moreInfoIcon'), component_property='n_clicks'),
    State(component_id=id('moreInfoCollapse'), component_property='is_open'),
    prevent_initial_call=True
)
def invertMoreInfoVisibility(n_clicks, is_open):
    if n_clicks:
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
        text = 'Collapse Gene Info'
        color = 'info'
    else:
        text = 'Open Gene Info'
        color = 'primary'
    return newState, text, color



@callback(
    Output(component_id=id('modal_info'), component_property='is_open'),
    Input(component_id=id('btn_info'),component_property='n_clicks'),
    State(component_id=id('modal_info'), component_property='is_open'),
)
def invertModalInfoVisibility(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open