# Installation

This file will guide you in installing the necessary components for running the PNN atlas on your computer. It assumes no prior knowledge of python nor any programming experience.

If you are **experienced** with Python, you can just follow the steps in a short-form [down here](#short-form-for-experienced-users).

## Step 1 - Install Anaconda

Anaconda (or its lighter version, Miniconda) installs Python and lets you keep the packages
needed by the atlas in a separate "environment", so they don't interfere with anything else on your computer.

- Download the installer for your operating system from [anaconda.com/download](https://www.anaconda.com/download)
  (or Miniconda from [docs.anaconda.com/miniconda](https://docs.anaconda.com/miniconda/)) and run it with the default options.
- Open a terminal:
  - **Windows**: open *Anaconda Prompt* from the Start menu.
  - **macOS / Linux**: open the *Terminal* app.
- Check that it works by typing `conda --version` and pressing Enter. It should print a version number.

## Step 2 - Download this repository

- **With git** (if you have it installed): move to a folder of your choice and clone the repository:  
`cd full/path/to/folder/`  
`git clone https://github.com/LeonardoLupori/pnnatlas.git`
- **Without git**: on the [GitHub page](https://github.com/LeonardoLupori/pnnatlas) click *Code* → *Download ZIP*,
  then extract it in a folder of your choice. Rename the extracted folder from `pnnatlas-main` to **`pnnatlas`**.

> ⚠️ The folder **must** be called `pnnatlas`: Python uses the folder name to find the atlas code.

You should now have a folder `full/path/to/folder/pnnatlas/` containing `pnnatlas.py`, `pages/`, `utils/`, `data/` and so on.

## Step 3 - Install the requirements to run the atlas

In the terminal, create a new environment called `pnnatlas`, activate it, and install the required packages:

```
conda create -n pnnatlas python=3.12
conda activate pnnatlas
cd full/path/to/folder/pnnatlas
pip install -r requirements.txt
```

## Step 4 - Run the atlas python file

The atlas has to be started from the folder that **contains** the `pnnatlas` folder (not from inside it):

```
cd full/path/to/folder
python -m pnnatlas
```

Loading the data takes a few seconds; then the terminal prints something like
`Dash is running on http://127.0.0.1:8050/`. Leave the terminal open while you use the atlas, and press `Ctrl+C` in it to stop the atlas.

## Step 5 - Access the atlas in your browser

Open any web browser and go to the address printed in the terminal, usually [http://127.0.0.1:8050/](http://127.0.0.1:8050/).
The atlas runs entirely on your computer, so it works offline too.

---

## Short form (for experienced users)

- Clone this repo in a folder of your choice on your pc (keep the folder name `pnnatlas`):  
`cd full/path/to/folder/`  
`git clone https://github.com/LeonardoLupori/pnnatlas.git`
- Create a new conda environment to keep things tidy:  
`conda create -n pnnatlas python=3.12`
- Activate the newly created environment:  
`conda activate pnnatlas`
- Install the required packages:  
`pip install -r pnnatlas/requirements.txt`
- Run the atlas **from the parent folder** (the repo is a Python package):  
`python -m pnnatlas`
- The script will create a local server and will print its address in the terminal (usually `http://127.0.0.1:8050/`). Open that address with any browser and you should be able to navigate the webapp.

After the first installation, you can run the webapp by simply activating the environment, going in the folder that contains the cloned repo, and running the atlas:  

```
conda activate pnnatlas
cd full/path/to/folder/
python -m pnnatlas
```
