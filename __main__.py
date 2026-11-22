# Lets you start the development server with:  python -m pnnatlas
# (run from the folder that contains the pnnatlas folder).
# Production servers don't use this file: they load "pnnatlas:server" through WSGI.
from .pnnatlas import app

app.run(debug=True)
