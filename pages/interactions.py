from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

from pathlib import Path
import pandas as pd
from pyparsing import col

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
# Naming is a shorthand for Wfa _ Diffuse _ Coarse/Mid/Fine
w_d_c = pd.read_csv(dataFolder/'wfa'/'diffuse'/'wfa_diff_coarse.csv', header=[0,1], index_col=[0])
w_d_m = pd.read_csv(dataFolder/'wfa'/'diffuse'/'wfa_diff_mid.csv', header=[0,1], index_col=[0,1])
w_d_f = pd.read_csv(dataFolder/'wfa'/'diffuse'/'wfa_diff_fine.csv', header=[0,1], index_col=[0,1,2])


# ------------------------------------------------------------------------------
# Perform some preprocessing
# ------------------------------------------------------------------------------

# Create lists of dictionaries {label:areaName, value=areaID} for populating dropDowns
coarseDict = cf.dataFrame_to_labelDict(w_d_c,'coarse',structuresDf)


# ------------------------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------------------------


layout = dbc.Container([
    lf.makeCitationOffCanvas(),
    dbc.Row(lf.makeNavBar()),               # Navigation Bar
    dbc.Row(lf.makeInteractionHeader(id)),            # Big header


    dbc.Row([
        dbc.Col([
            lf.makeInteractionSelectionMenu(id)
        ],xs=12,lg=3),
        dbc.Col([
            
            dbc.Spinner([
                dcc.Graph()
            ],color='primary'),
            lf.makeAreasChecklist(id, coarseDict),
        ])
    ]),
    dbc.Row([],style={"margin-top": "500px"}),
])