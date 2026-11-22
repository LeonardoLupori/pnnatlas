# The app itself lives in pnnatlas.py. Re-exporting it here keeps both WSGI entry
# points working: "pnnatlas:server" (used by existing deployments) and
# "pnnatlas.pnnatlas:server".
from .pnnatlas import app, server

__all__ = ["app", "server"]
