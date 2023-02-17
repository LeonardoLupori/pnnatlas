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

def emptyMetricsDf():
    emptyDf = pd.DataFrame(columns=['regionName','acronym','regionID','mean','sem','color'])
    return emptyDf

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

def mergeCoordinatesAndData(coordDf, dataDf):
    aggrData = dataDf.aggregate(func=['mean','sem'], axis=1)
    mergedDf = coordDf.merge(aggrData,how='left',left_on='regionID',right_on='mid')

    return mergedDf

def calculateGraphHeight(numRows):
    """
    Calculates the figure height based on the number of rows to display
    """
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

def getClimsAnatomicalExplorer(selMetric, staining='wfa'):
    """
    Based on the selected metric this function returns reasonable default values
    to use to set various properties of slider for min and max in the anatomical explorer
    """
    if staining =='wfa':
        if selMetric=='density':
            min = 0
            max = 120
        elif selMetric=='intensity':
            min = 0
            max = 0.7
        elif selMetric=='energy':
            min = 0
            max = 2.5
        elif selMetric=='diffuseFluo':
            min = 0
            max = 2.3
    elif staining == 'pv':
        if selMetric=='density':
            min = 0
            max = 200
        elif selMetric=='intensity':
            min = 0
            max = 0.7
        elif selMetric=='energy':
            min = 0
            max = 3
        elif selMetric=='diffuseFluo':
            min = 0
            max = 2.2

    return min,max

def loadAllSlices(folderPath:str):
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

def selectData(dataWfa, dataPv, selStaining, selMetric, resolution):

    if selStaining=='wfa':
        output = dataWfa[resolution].xs(selMetric, axis=1, level='params')
        return output
    elif selStaining=='pv':
        output = dataPv[resolution].xs(selMetric, axis=1, level='params')
        return output
    return []


# ------------------------------------------------------------------------------
# Page-Specific Functions
# ------------------------------------------------------------------------------

# WFA and PV
# ------------------------------------------------------------------------------

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
        height=500,
        showlegend=False,
        margin=dict(
                l=2,
                r=2,
                b=2,
                t=2,
                pad=0
            )
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
    rgb = mapper.to_rgba(dataFrame['mean'])
    rgb[rgb == 1] = 0.999
    rgb = [f'rgb({x[0]},{x[1]},{x[2]})' for x in rgb]
    dataFrame['color'] = rgb

    # Empty List that will contain all the go.Scatter traces for the brain regions
    newData = []

    # Draw a shape for each area in the dataframe
    for _, area in dataFrame.iterrows():
        # Do not draw Areas that have NaN as a mean value
        if (np.isnan(area['mean'])) and (area['acronym']!='root'):
            continue

        # Create and format the hover string of this area
        if area['acronym']!='root':
            hoverString = ("<b>" + area['acronym'] + "</b>" + "<br>" + "<i>" + area['regionName'] + "</i>" + "<br>" +
                f"Mean: {area['mean']:.3f}" + "<br>" + f"SEM: {area['sem']:.3f}"
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

    # Somehow here fig is just a dict and not a go.Figure object so here we reinitialize it 
    # as an object
    fig = go.Figure({'data':fig['data'], 'layout':fig['layout']})

    # Add the colorbar
    colorbar_trace  = go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(
            colorscale=cmap, 
            showscale=True,
            cmin=vmin,
            cmax=vmax,
            colorbar=dict(thickness=10, tickvals=[vmin, vmax], ticktext=[f'{vmin}', f'{vmax}'], outlinewidth=0, ypad=200)
        ),
        hoverinfo='none'
    )
    fig.add_trace(colorbar_trace)

    return fig

def combineDiffuseDataframes(major_selection, addCoarse_selection, addMid_selection, addFine_selection,
        coarseDf, midDf, fineDf):
    """
    combineDiffuseDataframes(major_selection, addCoarse_selection, addMid_selection, addFine_selection)

    Takes the user selection on the dropdown menus and returns a combined dataframe
    with all the selected areas on each row.
    """
    emptyDf = emptyMetricsDf()

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

def aggregateFluoDataframe(combinedDf, structuresDf):
    """
    Takes a combined DataFrame of a multiple selection of regions and aggregate it
    to calculate mean and SEM and add color, name and acronym information for all 
    the regions
    """
    if combinedDf.empty:
        return emptyMetricsDf()

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

def update_diffuseFluoHistogram(aggrDf, selMetric='diffuseFluo', staining='wfa'):

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

    # Determine the label for the x axis based on the staining and metric selected
    if staining == 'wfa':
        switchName = {
            'diffuseFluo': 'WFA diffuse intensity (A.U.)',
            'energy': 'PNN Energy (A.U.)',
            'intensity': 'PNN Intensity (A.U.)',
            'density': 'PNN Density (PNNs/mm^2)'
        }
    elif staining == 'pv':
        switchName = {
            'diffuseFluo': 'PV diffuse intensity (A.U.)',
            'energy': 'PV Energy (A.U.)',
            'intensity': 'PV Intensity (A.U.)',
            'density': 'PV Density (cells/mm^2)'
        }

    fig.update_layout(
        font_family="arial",
        xaxis_title=switchName[selMetric],
        yaxis_title="",
        showlegend=False,
        height= calculateGraphHeight(aggrDf.shape[0]),
        )

    fig.update_xaxes(
        title_font = {"size":16}
    )
    return fig



# Interactions
# ------------------------------------------------------------------------------
def intScattAggregateData(structuresDf, xData, yData, zScore):
    
    xData = xData.aggregate(func=['mean'], axis=1)
    yData = yData.aggregate(func=['mean'], axis=1)
    structuresDf = structuresDf[['name','acronym','rgb_plotly']]

    merged = xData.join(yData, how='inner', lsuffix='_x', rsuffix='_y')
    merged = merged.join(structuresDf, on='mid', how='left')
    merged = merged.drop(1009, level='mid')

    # Z-score
    if zScore:
        means = merged[['mean_x','mean_y']]
        means = (means - means.mean()).divide(means.std())
        merged[['mean_x','mean_y']] = means        

    return merged

def makeInteractionScatter():
    """
    Draws the Scatter plot in the interaction page for the first time so that 
    boring features of the figure layout do not have to be recomputed every time 
    the plot updates.

    This function is called only at graph creation while the graph update is 
    performed through the function redrawInteractionScatter()
    """
    fig = go.Figure()

    fig.update_layout(
        template='none',
        height=650,
        legend=dict(
            orientation="v",
        ),
        font=dict(
            # family='Arial',
            size=14,
        ),
        margin=dict(
                t=30,
            )
    )

    fig.update_yaxes(
        scaleanchor = "x",  
        scaleratio = 1,
    )


    return fig

def update_IntScatter(fig, aggrDf, structDf, xStaining, xMetric, yStaining, yMetric, zScore):

    # Convert back the figure in a go object
    fig = go.Figure(fig)
    # remove all present data
    fig.data = []

    # Draw a Scatter trace for each area in the dataFrame
    for coarse, new_df in aggrDf.groupby(level='coarse'):
        thisTrace = go.Scatter(
            x = new_df['mean_x'], y = new_df['mean_y'],
            name = structDf.loc[coarse]['name'],
            marker_color = new_df['rgb_plotly'],
            mode='markers',
            marker = dict(
                size=13,
                line_width=1,
                opacity=0.85,
            ),
            customdata  = np.stack((new_df['name'], new_df['acronym']), axis=-1),
            hovertemplate= "<b>%{customdata[1]}</b>" + "<br>" +
                "<i>%{customdata[0]}</i>" + "<br>" + 
                f"{structDf.loc[coarse]['name']}" + "<br>" +
                f"<b>{xStaining}-{xMetric}</b>:" "%{x:.3f}" + "<br>" + 
                f"<b>{yStaining}-{yMetric}</b>:" + "%{y:.3f}" +
                "<extra></extra>",
            
        )
        fig.add_trace(thisTrace)

    # Sort traces alphabetically
    fig.data = sorted(fig.data, key=lambda d: d['name']) 

    xLabel = f"{xStaining.upper()} - {xMetric}"
    yLabel = f"{yStaining.upper()} - {yMetric}"
    if zScore:
        xLabel = xLabel + " - (Z-Score)"
        yLabel = yLabel + " - (Z-Score)"
    fig.update_xaxes(
        title=xLabel
    )
    fig.update_yaxes(
        title=yLabel
    )
    return fig

def update_colocHistogram(aggrDf, selMetric):

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

    # Determine the label for the x axis based on the staining and metric selected
    switchName = {
        'pvPositive_pnn': 'Percentage of PNNs around a PV cell',
        'wfaPositive_pv': 'Percentage of PV cells surrounded by a PNN',
    }
    fig.update_layout(
        font_family="arial",
        xaxis_title=switchName[selMetric],
        yaxis_title="",
        showlegend=False,
        height= calculateGraphHeight(aggrDf.shape[0]),
        )

    fig.update_xaxes(
        title_font = {"size":16}
    )
    return fig


# Genes
# ------------------------------------------------------------------------------

def getMetricDf(selMetric, wfa, pv):
    if selMetric == 'wfa_energy':
        return wfa['energy']
    elif selMetric == 'wfa_diffuseFluo':
        return wfa['diffuseFluo']
    elif selMetric == 'pv_energy':
        return pv['energy']
    else:
        return []

def combineGenesDf(selGene, selMetric, ishData, structuresDf):

    # Prepare the Df with staining metric data
    metricDf = pd.DataFrame(selMetric)
    metricDf.columns=['metric']
    metric = metricDf.reset_index()

    # Prepare the Df with gene expression data
    ishData.index.name = 'mid'
    ish = pd.DataFrame(ishData.loc[selGene])
    ish.columns = ['geneExp']

    # Merge the 2 dataframes
    merged = metric.join(ish, on='mid')

    # Add info about anatomical structures
    structuresDf = structuresDf[['acronym', 'name', 'rgb_plotly']]
    merged = merged.join(structuresDf, on='mid')

    merged = merged.set_index(['coarse','mid'])
    merged = merged.drop(1009, level='mid')

    return merged

def update_GenesScatter(fig, combinedDfCorrDf, structureDf, geneName):
    # Convert back the figure in a go object
    fig = go.Figure(fig)
    # remove all present data
    fig.data = []

    # Draw a Scatter trace for each area in the dataFrame
    for coarse, new_df in combinedDfCorrDf.groupby(level='coarse'):
        thisTrace = go.Scatter(
            x = new_df['geneExp'], y = new_df['metric'],
            name = structureDf.loc[coarse]['name'],
            marker_color = new_df['rgb_plotly'],
            mode='markers',
            marker = dict(
                size=13,
                line_width=1,
                opacity=0.85,
            ),
            customdata  = np.stack((new_df['name'], new_df['acronym']), axis=-1),
            hovertemplate= "<b>%{customdata[1]}</b>" + "<br>" +
                "<i>%{customdata[0]}</i>" + "<br>" + 
                f"{structureDf.loc[coarse]['name']}" + "<br>" +
                f"<b>Staining Metric</b>:" "%{x:.3f}" + "<br>" + 
                f"<b>Gene Expression</b>:" + "%{y:.3f}" +
                "<extra></extra>",
            
        )
        fig.add_trace(thisTrace)

    # Sort traces alphabetically
    fig.data = sorted(fig.data, key=lambda d: d['name']) 

    fig.update_layout(title=geneName)

    return fig

def make_GeneScatter():
    fig = go.Figure()

    fig.update_layout(
        template='none',
        height=650,
        legend=dict(
            orientation="v",
        ),
        font=dict(
            size=14,
        ),
        margin=dict(
                t=30,
            )
    )
    # Customize X axis
    fig.update_xaxes(
        type="log",
        title="Gene Expression Energy"
    )
    # Customize Y axis
    fig.update_yaxes(
        type="log",
        scaleanchor = "x",  
        scaleratio = 1,
        title="Staining Metric"
    )
    return fig

def getGeneInfoTable(selMetric, selGene, geneDict):

    if selMetric=='wfa_energy':
        data = geneDict['wfa_en']
    elif selMetric=='wfa_diffuseFluo':
        data = geneDict['wfa_diff']
    elif selMetric=='pv_energy':
        data = geneDict['pv_en']    
    else:
        return []

    data = data.loc[data['gene_AGEA_id']==selGene]
    geneName = data.iloc[0]['gene_name']
    data = data.T.reset_index()
    data.columns = ['Parameter', 'Value']

    return data, geneName
