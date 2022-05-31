from cProfile import label
from pydoc import classname
from dash import dcc, html
import dash_bootstrap_components as dbc


# ------------------------------------------------------------------------------
# TYPOGRAPHY
# ------------------------------------------------------------------------------

def makeSubtitle(string):
    """
    Makes a subtitle with a line underneath to divide sections
    """
    subtitle = html.Div([
        html.H2(string,
            className="mt-2 mb-0 fw-bolder"),
        html.Hr(className="my-0")   
    ])
    return subtitle

def makeNavBar():
    """
    Makes the navigation bar
    """
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink('WFA', href='/wfa')),
            dbc.NavItem(dbc.NavLink('PV', href='/pv')),
            dbc.NavItem(dbc.NavLink('Interactions', href='/interactions')),
            dbc.NavItem(dbc.NavLink('Genes', href='/genes')),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem('Cite', href='#'),
                    dbc.DropdownMenuItem('About Us', href='#'),
                ],
                nav=True,
                in_navbar=True,
                label='More',
            ),
        ],
        brand='PNN Atlas',
        brand_href='/wfa',
        color='primary',
        fixed='top',
        dark=True,
        style={'height':'40px'},
        className=''
    )
    return navbar

def makeWfaHeader(idFunc):
    """
    Makes the header for the WFA page
    """
    # Main Title
    header = html.Div(
        dbc.Container([
            html.Div([
                html.H2("Perineuronal Nets", className="display-4"),
                dbc.Button("Cite", id=idFunc("btn_citeHeader"),color="success", outline=True)
            ], className='d-flex justify-content-between align-items-center mb-0'),
            
            html.Hr(className="mt-0 mb-1"),
            html.P("An atlas for WFA-positive PNNs in the mouse brain"
            )
            ],
            fluid=True,
            className="py-1 bg-light rounded-3",
        ),
        className="p-0 my-1",
    )
    return header

def makeInteractionHeader(idFunc):
    """
    Makes the header for the WFA page
    """
    # Main Title
    header = html.Div(
        dbc.Container([
            html.Div([
                html.H2("Interactions", className="display-4"),
                dbc.Button("Cite", id=idFunc("btn_citeHeader"),color="success", outline=True)
                ], className='d-flex justify-content-between align-items-center mb-0'
            ),
            html.Hr(className="mt-0 mb-1"),
            html.P("Explore the relationship between perineuronal nets and PV-cells"),  
            ],
            fluid=True,
            className="py-1 bg-light rounded-3",
        ),
        className="p-0 my-1",
    )
    return header

def makePVHeader():
    """
    Makes the header for the PV page
    """
    # Main Title
    header = html.Div(
        dbc.Container([
                html.H1("Parvalbumin", className="display-3"),
                html.P("An atlas for PV-positive cells in the mouse brain",
                    className="lead",
                ),
                html.Hr(className="my-2"),
                html.P(["Mouse brains were stained with Weisteria Floribunda Agglutinin (WFA). "
                "Brain sections were aligned to the ",
                html.A("Allen Brain Atlas", href="https://atlas.brain-map.org/", target="_blank"),
                " Common Coordinate Framework version3 (CCFv3) and for each brain area:"
                ]),
                html.P(dbc.Button("Cite", id="btn_citeHeader",color="primary"), className="lead"
                ),
            ],
            fluid=True,
            className="py-3 bg-light rounded-3",
        ),
        className="p-0 my-3",
    )
    return header

def makeAreasChecklist(idFunc,coarseDict):
    checklist = dbc.Checklist(
        id=idFunc('chklst_areasCorr'),
        options=coarseDict,
        value=[x['value'] for x in coarseDict],
        inline=True,
        className='ms-5'
    )
    return checklist

def makeInteractionSelectionMenu(idFunc):
    """
    Makes the left-side menu of the correlation plot in the interaction page
    """

    # Create a list of dicts for the dropdown of WFA vs PV
    wfaPvDictList = [{'label':'WFA', 'value':'wfa'},{'label':'Parvalbumin', 'value':'pv'}]

    # Create a list of dicts for the dropdown of the different metrics
    metricsDictList = [
        {'label':'Diffuse Fluorescence','value':'diffuse'},
        {'label':'Cell Density','value':'density'},
        {'label':'Cell Intensity','value':'intensity'},
        {'label':'Cell Energy','value':'energy'},
    ]

    
    menu = html.Div([

        # X AXIS
        dbc.Row([
            html.Div([
                html.H4("X axis", className='my-1 mt-2'),
                html.H6("Select a staining", className='mt-3 mb-1'),
                dcc.Dropdown(
                    id=idFunc('drpD_xStaining'),
                    options = wfaPvDictList,
                    value='wfa',
                    multi = False,
                    clearable=False,
                    className=''
                ),
                html.H6("Select a metric", className='mt-3 mb-1'),
                dcc.Dropdown(
                    id=idFunc('drpD_xMetric'),
                    options = metricsDictList,
                    value='diffuse',
                    multi = False,
                    clearable=False,
                    className='mb-2'
                ),

            ],className='my-3 border border-light rounded-3')
        ]),

        # Y AXIS
        dbc.Row([
            html.Div([
                html.H4("Y axis", className='my-1 mt-2'),
                html.H6("Select a staining", className='mt-3 mb-1'),
                dcc.Dropdown(
                    id=idFunc('drpD_yStaining'),
                    options = wfaPvDictList,
                    value='pv',
                    multi = False,
                    clearable=False,
                    className=''
                ),
                html.H6("Select a metric", className='mt-3 mb-1'),
                dcc.Dropdown(
                    id=idFunc('drpD_yMetric'),
                    options = metricsDictList,
                    value='diffuse',
                    multi = False,
                    clearable=False,
                    className='mb-2'
                ),

            ],className='my-3 border border-light rounded-3')
        ]),
    ])
    return menu

def makeDiffuseHistogramSelectionMenu(idFunc, coarseDict, midDict, fineDict):
    """
    Makes the left-side menu with dropdowns for the diffuse fluorescence histogram,
    """
    menu = html.Div([
        html.H6(["Select a major brain subdivision:"],className='my-1'),
        dcc.Dropdown(
            id=idFunc('drpD_majorSubd'),
            options = coarseDict,
            value=315, # Defaults to Isocortex
            multi = False,
            className='my-1 mb-5'
        ),
        html.H6(["Add ",html.B("coarse-ontology")," region(s):"], className='my-1'),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id=idFunc('drpD_addCoarse'),
                    options = coarseDict,
                    multi = True,
                )],
                style={'flex-grow':'1'},
            ),
            html.Div([
                dbc.Button("All",id=idFunc('btn_allMajorDiff'))], 
            )],
            className='mt-1 mb-3', 
            style={'display':'flex','flex-direction':'row', 'column-gap':'5px'}
        ),
        html.H6(["Add ", html.B("mid-ontology"), " region(s):"],className='my-1'),
        dcc.Dropdown(
            id=idFunc('drpD_addMid'),
            options = midDict,
            multi = True,
            className="mt-1 mb-3"
        ),
        html.H6(["Add ", html.B("fine-ontology"), " region(s):"],className='my-1'),
        dcc.Dropdown(
            id=idFunc('drpD_addFine'),
            options = fineDict,
            multi = True,
            className="mt-1 mb-3"
        ),
        html.Div([
            # dbc.Button("Reset", id="btn-reset", color="primary", className="my-1"),
            dbc.Switch(
                label="Sort regions",
                value=False,
                id=idFunc("switch_sortDiff"),
                # class_name="mt-1"
                )],
            className="d-flex"
        ),

        # TOOLTIPS
        dbc.Tooltip("Add all the 12 major brain subdivisions.", target=idFunc("btn_allMajorDiff")),
        dbc.Tooltip(["Sort on intensity.", html.Br(), "Otherwise, sorted on region ontology."],
            target=idFunc("switch_sortDiff"),placement='bottom'
        ),
        dbc.Tooltip("Add all the regions of a selected major brain subdivision",
            target=idFunc("drpD_majorSubd"),placement="right"
        ),
        dbc.Tooltip("Major brain subdivisions",target=idFunc("drpD_addCoarse"),placement="right"),
        dbc.Tooltip("Regions at single-area level",target=idFunc("drpD_addMid"),placement="right"),
        dbc.Tooltip("Regions at single-layer level",target=idFunc("drpD_addFine"),placement="right"),
    ])
    return menu

def makeCollapsableTable(idFunc):
    """
    Makes the collapsable tabular data section
    """
    collapsTable = html.Div([
        dbc.Button("Open Tabular Data",
            id=idFunc("btn_openTabDiffuse"),
            className="mb-1",
            color="primary",
        ),
        dbc.Collapse(
            id=idFunc("collps_diffTab"),
            is_open=False,
        )],
        className='mt-3'
    )
    return collapsTable

def makeAnatomicalExplorerSelectionMenu(idFunc):
    """
    Makes the layout for the left-side selection menu of the anatomical explorer
    """
    menu = html.Div([

        html.H6(["Select a metric to show:"],className='my-1'),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id=idFunc('drpD_anatomDataset'),
                    options=[
                        {'label':'Diffuse Fluorescence','value':'diffuse'},
                        {'label':'PNN density','value':'density'},
                        {'label':'PNN intensity','value':'intensity'},
                        {'label':'PNN energy','value':'energy'},
                    ],
                    value='diffuse',
                    multi = False,
                    clearable=False,
                )],
                style={'flex-grow':'1'},
            ),
            html.Div([
                dbc.Button([html.I(className="fa-solid fa-info")],id=idFunc('btn_info'))], 
            )],
            className='mt-1 mb-3', 
            style={'display':'flex','flex-direction':'row', 'column-gap':'5px'}
        ),

        html.H6(["Colormap:"],className='my-1'),
        dcc.Dropdown(
            id=idFunc('drpD_anatomCmap'),
            options = colormapDictListDropdown(),
            value='Blues',
            multi = False,
            clearable=False,
            className="mt-1 mb-3"
        ),
        html.H6(["Color limits:"],className='my-1'),
        dcc.RangeSlider(min=0, max=5,
            step=0.1,
            marks={0:'0',1:'1',2:'2',3:'3',4:'4',5:'5'},
            value=[0,2.3],
            pushable=0.5,
            id=idFunc('slider_clims'),
            tooltip={"placement": "bottom", "always_visible": False},
            className='mt-1 mb-3'
        ),


        html.H6(["Antero-Posterior Axis:"],className='mt-5 mb-1'),
        dcc.Slider(0, 34, 1, value=10, id=idFunc('slider_ap'),
            marks={0:'Anterior',34:'Posterior'},
        ),

        # TOOLTIPS
        dbc.Tooltip("Visualization colormap.", target=idFunc("drpD_anatomCmap")),
        dbc.Tooltip("Set minimum and maximum values.", target=idFunc("slider_clims")),
    ])
    return menu

def colormapDictListDropdown():
    """
    Creates a list of dicts to fill a dropdown to select different colormaps
    """
    cmapDictList = [
        dict(label='Blue',value='Blues'),
        dict(label='Red',value='Reds'),
        dict(label='Green',value='Greens'),
        dict(label='Gray',value='Greys'),
        dict(label='Viridis',value='viridis'),
        dict(label='Magma',value='magma'),
    ]
    return cmapDictList

def makeCitationOffCanvas(idFunc):
    """
    Makes the layout for the offcanvas menu for citations
    """
    offcanvas = dbc.Offcanvas(
        html.P([
            "If you found this atlas to be useful in your research, please consider ", 
            html.B("citing us."),
            html.Br(),
            "Citation info"
        ]),
        id=idFunc("offCanv_cite"),
        title="Cite us",
        is_open=False,
    )
    return offcanvas

def makeMetricInfoModal(idFunc):

    diffuseCard = dbc.Card([
        dbc.CardBody([
            html.H5("Diffuse Fluorescence (A.U.)", className="card-title primary"),
            html.P(html.I("'How much WFA staining is there?'")),
            html.Hr(className="mb-1"),
            html.P(["For each mouse, we calculate the ", html.B("average fluorescence"), 
                " intensity across all the pixels belonging to a brain region. " + 
                "Then, we divide this value by the average fluorescence intensity " + 
                "of the entire brain of this mouse."],
                className="card-text")]
        )],
        style={'height':'100%'},
        outline=True,
        color='info',
    )

    densityCard = dbc.Card([
        dbc.CardBody([
            html.H5(["Cell Density (cells/mm", html.Sup(2) ,")"], className="card-title"),
            html.P(html.I("'How many cells are there?'")),
            html.Hr(className="mb-1"),
            html.P(["For each mouse, we calculate the ", html.B(["number of cells per mm",html.Sup(2)]), 
                " In a brain region. " + 
                "This value is the cell density."],
                className="card-text")]
        )],
        style={'height':'100%'},
        outline=True,
        color='info',
    )

    intensityCard = dbc.Card([
        dbc.CardBody([
            html.H5("Cell Intensity (A.U.)", className="card-title"),
            html.P(html.I("'How intense are the cells here?'")),
            html.Hr(className="mb-1"),
            html.P(["For each cell, we segment pixels belonging to the cell with a ", 
                html.B("random forest classifier."), " The average intensity value is ",
                "the intensity of that cell.", html.Br(), "For each brain region, we compute the ",
                "average of the intensity of all the cells in that region and then we ",
                "normalize this value by dividing it by the average intensity of",
                " the entire brain for this mouse."],
                className="card-text")],        
        )],
        style={'height':'100%'},
        outline=True,
        color='info'
    )

    energyCard = dbc.Card([
        dbc.CardBody([
            html.H5("Cell Energy (A.U.)", className="card-title"),
            html.P(html.I("'What's the overall prevalence of these cells here?'")),
            html.Hr(className="mb-1"),
            html.P(["A composite metric. ", html.Br(), 
                "To be defined!!"],
                className="card-text")]
        )],
        style={'height':'100%'},
        outline=True,
        color='info',
    )

    modal = dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Metrics analyzed")),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([diffuseCard], width=6),
                    dbc.Col([densityCard]),
                ], className=''),
                dbc.Row([
                    dbc.Col([intensityCard], width=6),
                    dbc.Col([energyCard]),
                ], className='my-3')]
        )],
        size='lg',
        id=idFunc('modal_info')
    )

    return modal

# ------------------------------------------------------------------------------
# 
# ------------------------------------------------------------------------------