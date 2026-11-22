# PNN Atlas

> 🧠 A **free** and **open-source** atlas for Perineuronal Nets in the mouse brain.
>

## Installation on your computer

You can access this atlas for free at www.pnnatlas.sns.it, however, if you prefer,
you can also run it locally on your computer so that you can access it even offline.

Follow the steps on this [tutorial page](docs/01_installation.md) to install the necessary components and run your own atlas.

## Installation on a server

### Requirements

- Python >= 3.11 (tested with Python 3.12)
- All the required packages, with tested versions, are listed in [requirements.txt](requirements.txt):  
`pip install -r requirements.txt`

### Running

The repository is a Python package, so run everything from the folder that *contains*
`pnnatlas/` (keep the repository folder named `pnnatlas`).

- Development server:  
`python -m pnnatlas`
- Production (WSGI): point your WSGI server at `pnnatlas:server`, e.g. with gunicorn:  
`gunicorn pnnatlas:server`  
  (`pnnatlas.pnnatlas:server` works too: both refer to the same app.)
