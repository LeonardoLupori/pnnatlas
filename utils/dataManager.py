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


def readSupplDataColoc(pathToFile:str):
    # TODO
    pass

def readSupplDataGenes(pathToFile:str):
    # TODO
    pass

