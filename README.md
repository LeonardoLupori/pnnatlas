# PNN Atlas

> 🧠 A **free** and **open-source** atlas for Perineuronal Nets in the mouse brain.
>

## Installation on your computer

You can access this atlas for free at www.pnnatlas.sns.it, however, if you prefer,
you can also run it locally on your computer so that you can access it even offline.

Follow the steps on this [tutorial page](docs/01_installation.md) to install the necessary components and run your own atlas.

### Requirements

- Python >= 3.11 (tested with Python 3.12)
- All the required packages, with tested versions, are listed in [requirements.txt](requirements.txt):  
`pip install -r requirements.txt`

### Running

The repository is a Python package: keep the repository folder named `pnnatlas` and run the
atlas from the folder that *contains* it:

```
python -m pnnatlas
```

Then open the address printed in the terminal (usually http://127.0.0.1:8050/) in your browser.
