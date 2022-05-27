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
        html.H1(string,
            className="h-1 my-3 fw-bolder"),
        html.Hr(className="my-2")   
    ])
    return subtitle

def makeNavBar():
    """
    # Makes the navigation bar
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
        className=''
    )
    return navbar

def makeWfaHeader():
    """
    Makes the header for the WFA page
    """
    # Main Title
    header = html.Div(
        dbc.Container([
                html.H1("Perineuronal Nets", className="display-4"),
                html.P("An atlas for WFA-positive PNNs in the mouse brain",
                    className="lead",
                ),
                html.Hr(className="my-2"),
                html.P(["Brain sections, stained with Weisteria Floribunda Agglutinin (WFA), were aligned to the ",
                    html.A("Allen Brain Atlas", href="https://atlas.brain-map.org/", target="_blank"),
                    " Common Coordinate Framework version3 (CCFv3)."
                ]),
                dbc.Row([
                    dbc.Col([dbc.Button("Cite", id="btn_citeHeader",color="primary")])
                ],className="my-3")
            ],
            fluid=True,
            className="py-1 bg-light rounded-3",
        ),
        className="p-0 my-3",
    )
    return header

def makeInteractionHeader(idFunc):
    """
    Makes the header for the WFA page
    """
    # Main Title
    header = html.Div(
        dbc.Container([
                html.H1("PNN-PV Interactions", className="display-4"),
                html.P("Explore the relationship between perineuronal nets and PV-cells",
                    className="lead",
                ),
                html.Hr(className="my-2"),
                html.P(["Brain sections, stained with Weisteria Floribunda Agglutinin (WFA), were aligned to the ",
                    html.A("Allen Brain Atlas", href="https://atlas.brain-map.org/", target="_blank"),
                    " Common Coordinate Framework version3 (CCFv3)."
                ]),
                dbc.Row([
                    dbc.Col([dbc.Button("Cite", id=idFunc("btn_citeHeader"),color="primary")])
                ],className="my-3")
            ],
            fluid=True,
            className="py-1 bg-light rounded-3",
        ),
        className="p-0 my-3",
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

    ## X
    # wfa o PV
    # Dataset (diffuso, density ecc)
    menu = html.Div([
        dbc.Row([
            html.Div([


            ],className='my-3 bg-light rounded-3')
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
        html.H6(["Select a dataset to show:"],className='my-1'),
        dcc.Dropdown(
            id=idFunc('drpD_anatomDataset'),
            options = [
                {'label':'Diffuse Fluorescence','value':'diffuse'},
                {'label':'PNN density','value':'density'},
                {'label':'PNN intensity','value':'intensity'},
                {'label':'PNN energy','value':'energy'},    
                ],
            value='diffuse',
            multi = False,
            clearable=False,
            className="my-1 mb-5"
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

def makeCitationOffCanvas():
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
        id="offCanv_cite",
        title="Cite us",
        is_open=False,
    )
    return offcanvas


# ------------------------------------------------------------------------------
# 
# ------------------------------------------------------------------------------