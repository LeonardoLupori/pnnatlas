import pandas as pd


################################################################################
# READ AND PARSE SUPPLEMENTARY DATA
################################################################################

def readSupplDataMetrics(pathToFile:str, removeAcronyms:bool=False):
    """
    Parse Excel files from the supplementary data with WFA or PV staining metrics
    to dataframes and return a dictionary of thre different dataframes

    PARAMETERS
    ********************
    pathToFile:str full path to the excel file to load

    RETURNS
    ********************
    dfDict:dict a dictionary of dataframes {dfCoarse, dfMid, dfFine}
    """

    # Read the corase, single animal data
    dfCoarse = pd.read_excel(
        pathToFile,
        sheet_name=0,
        header=[0,1],
        index_col=[0,1])
    if removeAcronyms:
        dfCoarse.index = dfCoarse.index.droplevel('coarse_acro')

    # Read the medium, single animal data
    dfMid = pd.read_excel(
        pathToFile,
        sheet_name=2,
        header=[0,1],
        index_col=[0,1,2,3])
    if removeAcronyms:
        dfMid.index = dfMid.index.droplevel(['coarse_acro','mid_acro'])
    
    # Read the fine, single animal data
    dfFine = pd.read_excel(
        pathToFile,
        sheet_name=4,
        header=[0,1],
        index_col=[0,1,2,3,4,5])
    if removeAcronyms:
        dfFine.index = dfFine.index.droplevel(['coarse_acro','mid_acro','fine_acro'])

    dfDict = {"coarse":dfCoarse, "mid":dfMid, "fine":dfFine}

    return dfDict


def readMetricsDataForGenes(pathToFile:str):
    # Read the medium redolution data (average across mice)
    metricDf = pd.read_excel(
        pathToFile,
        sheet_name=3,
        header=[0],
        index_col=[0,1,2,3])

    metricDf.index = metricDf.index.droplevel(['coarse_acro','mid_acro'])


    return metricDf


def readGenesCorrelationSupplData(pathToFile:str):

    wfa_en = pd.read_excel(pathToFile,
        sheet_name=0,
        header=0,
        index_col=0)
    
    wfa_diff = pd.read_excel(pathToFile,
        sheet_name=2,
        header=0,
        index_col=0)

    pv_en = pd.read_excel(pathToFile,
        sheet_name=1,
        header=0,
        index_col=0)

    dfDict = {"wfa_en":wfa_en, "wfa_diff":wfa_diff, "pv_en":pv_en}

    return dfDict