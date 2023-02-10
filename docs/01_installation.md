# Installation

This file will guide you in installing the necessary components for running the PNN atlas on your computer. It assumes no prior knowledge of python nor any programming experience.

If you are **experienced** with Python, you can just follow the steps in a short-form [down here](#short-form).

## Step 1 - Install Anaconda

## Step 2 - Download this repository

## Step 3 - Install the requirements to run the atlas

## Step 4 - Run the atlas python file

## Step 5 - Access the atlas in your browser

---

## Short form (for experienced users)

- Clone this repo in a folder of your choice on your pc:  
`cd full/path/to/folder/`  
`git clone https://github.com/LeonardoLupori/pnnatlas.git`
- Go inside the newly created folder:  
`cd ./pnnatlas`
- Create a new conda environment to keep things tidy:  
`conda create -n pnnatlas Python==3.10`
- Activate the newly created environment:  
`conda activate pnnatlas`
- Install the required packages:  
`conda install --file requirements.txt`
- Run the atlas:  
`python -m pnnatlas.py`
- The script will create a local server and will print its address in the terminal (usually `http://127.0.0.1:8050/`). Open that address with any browser and you should be able to navigate the webapp.

After the first installation, you can run the webapp by simply activating the environment, going in the folder that you cloned, and running the main file:  

```python
conda activate pnnatlas
cd full/path/to/pnnatlas/folder/
python -m pnnatlas.py
```
