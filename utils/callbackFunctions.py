# from matplotlib.pyplot import axis
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm
import pandas as pd
import os

def id_factory(page: str):
    def func(_id: str):
        """
        Dash pages require each component in the app to have a totally
        unique id for callbacks. This is easy for small apps, but harder for larger 
        apps where there is overlapping functionality on each page. 
        For example, each page might have a div that acts as a trigger for reloading;
        instead of typing "page1-trigger" every time, this function allows you to 
        just use id('trigger') on every page.
        
        How:
            prepends the page to every id passed to it
        Why:
            saves some typing and lowers mental effort
        **Example**
        # SETUP
        from system.utils.utils import id_factory
        id = id_factory('page1') # create the id function for that page
        
        # LAYOUT
        layout = html.Div(
            id=id('main-div')
        )
        # CALLBACKS
        @app.callback(
            Output(id('main-div'),'children'),
            Input(id('main-div'),'style')
        )
        def funct(this):
            ...
        """
        return f"{page}-{_id}"
    return func

    
def dataFrame_to_labelDict(df,indexName,structuresDf):
    """dataFrame_to_labelDict(df,indexName,structuresDf)
    
    Creates a list of dictionaries {label:areaName, value=areaID} that is used 
    to populate dropdown menus in Dash
    """
    # Get the IDs of all the areas in the dataframe at the correct index level
    regionIDs = df.index.get_level_values(indexName).to_list()
    
    # Convert IDs to names
    regionNames = structuresDf.loc[regionIDs,'name'].tolist()
    
    # Build a dictionary
    labelDict = [dict(label=k, value=v) for (k,v) in zip(regionNames,regionIDs)]
    # Sort the region names alphabetically
    labelDict = sorted(labelDict, key= lambda x: x['label'])
    return labelDict


def emptyGraph():
    figure = {
        "layout": {
            "xaxis": {
                "visible": False
            },
            "yaxis": {
                "visible": False
            },
            "annotations": [
                {
                    "text": "No matching data found",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }
    return figure


def emptyDiffuseDf():
    emptyDf = pd.DataFrame(columns=['regionName','acronym','regionID','mean','sem','color'])
    return emptyDf


def combineDiffuseDataframes(major_selection, addCoarse_selection, addMid_selection, addFine_selection,
        coarseDf, midDf, fineDf):
    """
    combineDiffuseDataframes(major_selection, addCoarse_selection, addMid_selection, addFine_selection)

    Takes the user selection on the dropdown menus and returns a combined dataframe
    with all the selected areas on each row.
    """
    emptyDf = emptyDiffuseDf()

    # Dataframe with all the regions in the selected major subdivision
    if major_selection:
        d1 = midDf.loc[major_selection,:]
    else:
        d1 = emptyDf

    # Df with the selected coarse regions
    if addCoarse_selection: 
        d2 = coarseDf.loc[addCoarse_selection]
    else:
        d2 = emptyDf

    # Df with the selected mid regions
    if addMid_selection:
        idx = pd.IndexSlice
        d3 = midDf.loc[idx[:,addMid_selection],:]
        d3.index = d3.index.droplevel(level=0)
    else:
        d3 = emptyDf

    # Df with the selected fine regions
    if addFine_selection:
        idx = pd.IndexSlice
        d4 = fineDf.loc[idx[:,:,addFine_selection],:]
        d4.index = d4.index.droplevel(level=[0,1])
    else:
        d4 = emptyDf

    # Concatenate all the dataframes together
    dfList = [d1,d2,d3,d4]
    if all([x.empty for x in dfList]):
        combinedDf = emptyDf
    else:
        combinedDf = pd.concat([x for x in dfList if not x.empty], axis=0)

    return combinedDf


def loadStructuresDf(structuresPath):
    """
    Loads the structures json as a DataFrame and performs some processing
    to make it more usable.
    It sets the region ID as the index of the df and creates a column 'rgb_plotly'
    with the color of that region in the plotly format.
    """
    # Load the file
    structuresDf = pd.read_json(structuresPath)
    # Set the region ID as the index
    structuresDf = structuresDf.set_index('id') 
    # Create a column with the RGB color in the plotly format e.g., "rgb(100,200,8)"
    rgb_to_strRgb = lambda x: f"rgb({x[0]},{x[1]},{x[2]})"
    structuresDf['rgb_plotly'] = structuresDf['rgb_triplet'].apply(rgb_to_strRgb)

    return structuresDf

def aggregateFluoDataframe(combinedDf, structuresDf):
    """
    Takes a combined DataFrame of a multiple selection of regions and aggregate it
    to calculate mean and SEM and add color, name and acronym information for all 
    the regions
    """
    if combinedDf.empty:
        return emptyDiffuseDf()

    # Aggregate data and calculate statistics and display options for all the areas 
    aggrDf = combinedDf.aggregate(func=['mean','sem'], axis=1)
    # Merge combinedDf with some columns of the structures Df
    aggrDf = aggrDf.join(structuresDf.loc[:,['acronym','name','rgb_plotly']], how='inner')
    # Change column names
    aggrDf = aggrDf.rename(dict(rgb_plotly='color', name='regionName'),axis=1)
    # Add column with the region ID
    aggrDf['regionId'] = aggrDf.index.tolist()
    # Reorder columns (this df will be displayed as tabular data in the webapp)
    aggrDf = aggrDf[['regionName','acronym','regionId','mean','sem','color']]

    return aggrDf


def diffuseFluoHistogram(aggrDf):

    # Return an empty graph with a warning if no regions are selected
    if aggrDf.empty:
        return emptyGraph()

    # Assemble a dict that links regiona names to colors
    colorDict = {k:v for (k,v) in zip(aggrDf['regionName'], aggrDf['color'])}

    # Create the barplot
    fig = px.bar(data_frame=aggrDf, x='mean', y='regionName',
        color='regionName',
        error_x='sem',
        template='plotly_white',
        color_discrete_map=colorDict,
        orientation='h',

        # Customization of the Hovers
        hover_name='regionName',
        hover_data={'regionName':False,
            'mean':':.3f',
            'sem':':.3f'},
        )

    fig.update_layout(
        font_family="arial",
        xaxis_title="WFA diffuse intensity (A.U.)",
        yaxis_title="",
        showlegend=False,
        height= calculateGraphHeight(aggrDf.shape[0]),
        )

    fig.update_xaxes(
        title_font = {"size":16}
    )
    return fig


def makeAnatExplorerScatter():
    """
    Draws the Anatomical Explorer for the first time so that boring features of the
    figure layout do not have to be recomputed every time the plot updates.

    This function is called only at graph creation while the graph update is 
    performed through the function redrawAnatExplorerScatter()
    """
    # Creates a go figure
    fig = go.Figure()

    # Customize the general layout of the figure
    fig.update_layout(
        template='simple_white',
        height=650,
        showlegend=False
    )

    # X-axis
    fig.update_xaxes(
        visible=False,
        # showticklabels=False,
        # ticks='',
        range=(0,11400) # Maximum range in micrometers for the 25um mouse Allen atlas 
    )

    # Y-axis
    fig.update_yaxes(
        visible=False,
        # showticklabels=False,
        # ticks='',
        scaleanchor = "x",  
        scaleratio = 1,         # Makes the scale of the axis equal
        autorange="reversed"    # Since the atlas is upside-down
    )

    return fig


def redrawAnatExplorerScatter(fig, dataFrame, cmap, vmin, vmax):
    """
    Updates the data of the figure fig.

    This function is used to update the Anatomical Explorer
    """
    
    # Add the color column to the dataframe based on the colormap and vmin vmax
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cmap)
    # mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    rgb = mapper.to_rgba(dataFrame['mean_diffWfa'])
    rgb = [f'rgb({x[0]},{x[1]},{x[2]})' for x in rgb]
    dataFrame['color'] = rgb

    # Empty List that will contain all the go.Scatter traces for the brain regions
    newData = []

    # Draw a shape for each area in the dataframe
    for _, area in dataFrame.iterrows():

        # Create and format the hover string of this area
        if area['acronym']!='root':
            hoverString = ("<b>" + area['acronym'] + "</b>" + "<br>" + "<i>" + area['name'] + "</i>" + "<br>" +
                f"Mean: {area['mean_diffWfa']:.3f}" + "<br>" + f"sem: {area['sem_diffWfa']:.3f}"
            )
        else:
            hoverString='root'

        # Create the go.Scatter trace
        thisTrace = go.Scatter(
            x=np.array(area['coord'])[:, 0],
            y=np.array(area['coord'])[:, 1],
            
            mode='lines',
            line=dict(
                width=1,
                color='rgb(0,0,0)',
            ),
            fill="toself",
            fillcolor= area['color'] if area['acronym']!='root' else 'rgb(0,0,0)',
            # Customize the hover labels
            hoverlabel=dict(
                namelength=0,
                bgcolor='rgb(255,255,255)',
                font=dict(color='black')),
            text=hoverString,
            # Name of this specific Scatter Trace
            name=area['acronym'],
            opacity=0.3 if area['acronym'] == "root" else None,
        )
        # Add this trace to the list
        newData.append(thisTrace)

    # Reorder data so that root is first (drawn below all the other areas)
    idx = []
    for i,scatter  in enumerate(newData):
        if 'root' in scatter['name']:
            idx.append(i)   
    [newData.insert(0,newData.pop(x)) for x in idx]
    fig['data'] = newData

    return fig


# Calculates the figure height based on the number of rows to display
def calculateGraphHeight(numRows):
    if numRows<3:
        height = numRows*200
    elif numRows<5:
        height = numRows*120
    elif numRows<10:
        height = numRows*55
    elif numRows<15:
        height = numRows*40
    elif numRows<25:
        height = numRows*30
    else:
        height = numRows*20
    return height



def loadAllSlices(folderPath):
    """
    loadAllSlices(folderPath)

    Loads all the json files in a folder in a list of pandas dataframes and 
    returns the list
    """
    fileNames = sorted(os.listdir(folderPath))
    dfList = []
    for fileName in fileNames:
        df = pd.read_json(os.path.join(folderPath,fileName))
        dfList.append(df)
    return dfList

