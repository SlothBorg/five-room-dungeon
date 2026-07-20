"""
Browser glue for the five-room-dungeon generator.

Runs inside Pyodide, reuses the pure generation logic from main.py
(fetched into the virtual filesystem alongside this file) and returns
JSON-serializable results for app.js to render.
"""

import base64
import io
import json

import matplotlib.pyplot as plt

from main import build_dungeon, build_figure, five_node_topologies, room_markdown

_TOPOLOGIES = five_node_topologies()


def generate_dungeon(n):
    n = int(n)
    if n < 1:
        raise ValueError("n must be a positive integer")

    master, subgraphs = build_dungeon(n, _TOPOLOGIES)

    fig = build_figure(master, subgraphs)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    png_base64 = base64.b64encode(buf.getvalue()).decode("ascii")

    result = {
        "png_base64": png_base64,
        "markdown": room_markdown(master),
        "module_count": len(subgraphs),
        "room_count": master.number_of_nodes(),
        "edge_count": master.number_of_edges(),
    }
    return json.dumps(result)
