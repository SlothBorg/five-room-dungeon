"""
Five-room-dungeon subgraph generator.

Based off the 21 topologically in Steve Lawford's "Counting five-node subgraphs" (2009.11318)
"""

import random

import matplotlib

matplotlib.use("AGG")

import matplotlib.pyplot as plt
import networkx as nx
from networkx.generators.atlas import graph_atlas_g

ROOM_ROLES = {
    1: "Entrance / Guardian",
    2: "Puzzle / Roleplay Challenge",
    3: "Trick / Setback",
    4: "Climax / Big Battle",
    5: "Reward / Revelation",
}

ROLE_COLORS = {
    1: "#e63946",
    2: "#f1a208",
    3: "#2a9d8f",
    4: "#457b9d",
    5: "#8338ec",
}

SHARE_COUNTS = [1, 2, 3]
SHARE_WEIGHTS = [0.5, 0.3, 0.2]


def five_node_topologies():
    atlas = graph_atlas_g()
    topologies = [g for g in atlas if g.number_of_nodes() == 5 and nx.is_connected(g)]

    return topologies


def prompt_for_count():
    while True:
        raw = input("How many dungeon modules do you want? ")
        try:
            n = int(raw)
            if n > 0:
                return n
        except ValueError:
            pass
        print("Please enter a positive integer.")


def build_dungeon(num_subgraphs, topologies):
    """
    Build `num_subgraphs` five-node subgraphs.
    Every subgraph after the first shares 1-3 nodes (see SHARE_COUNTS/SHARE_WEIGHTS)
    Every node contains a room role 1-5; a shared node keeps a single role everywhere it appears.
    Every subgraph contains each role once.

    Returns (master_graph, list_of_subgraph_records).
    """
    master = nx.Graph()
    subgraphs = []
    next_id = 0

    for i in range(num_subgraphs):
        topology = random.choice(topologies)
        edges = list(topology.edges())

        if i == 0:
            roles = [1, 2, 3, 4, 5]
            random.shuffle(roles)
            slot_to_node = {}
            for slot in range(5):
                slot_to_node[slot] = next_id
                master.add_node(next_id, role=roles[slot])
                next_id += 1
        else:
            nodes_by_role = {r: [] for r in ROOM_ROLES}
            for node_id, data in master.nodes(data=True):
                nodes_by_role[data["role"]].append(node_id)

            share_count = random.choices(SHARE_COUNTS, weights=SHARE_WEIGHTS)[0]
            shared_roles = random.sample(list(ROOM_ROLES), share_count)
            shared_slots = random.sample(range(5), share_count)

            slot_to_node = {
                slot: random.choice(nodes_by_role[role])
                for role, slot in zip(shared_roles, shared_slots, strict=True)
            }

            remaining_roles = [r for r in ROOM_ROLES if r not in shared_roles]
            random.shuffle(remaining_roles)

            free_slots = [s for s in range(5) if s not in shared_slots]
            for slot, role in zip(free_slots, remaining_roles, strict=True):
                slot_to_node[slot] = next_id
                master.add_node(next_id, role=role)
                next_id += 1

        for u, v in edges:
            master.add_edge(slot_to_node[u], slot_to_node[v])

        subgraphs.append(
            {
                "index": i + 1,
                "nodes": {master.nodes[slot_to_node[s]]["role"]: slot_to_node[s] for s in range(5)},
            }
        )

    return master, subgraphs


def print_summary(master, subgraphs):
    print(
        f"\nGenerated {len(subgraphs)} five-node subgraphs, "
        f"{master.number_of_nodes()} total nodes, "
        f"{master.number_of_edges()} total edges.\n"
    )
    for sg in subgraphs:
        node_str = ", ".join(
            f"{role}({ROOM_ROLES[role]})=node{node_id}"
            for role, node_id in sorted(sg["nodes"].items())
        )
        print(f"Subgraph {sg['index']}: {node_str}")
    print()


def room_markdown(master):
    """Render the rooms table as a Markdown string."""
    lines = [
        "# Dungeon Rooms",
        "",
        "| Room | Role | Connects To |",
        "|------|------|-------------|",
    ]
    for node in sorted(master.nodes):
        role = master.nodes[node]["role"]
        neighbors = sorted(master.neighbors(node))
        connections = ", ".join(f"Room {n}" for n in neighbors)
        lines.append(f"| Room {node} | {role} - {ROOM_ROLES[role]} | {connections} |")
    return "\n".join(lines) + "\n"


def write_room_markdown(master, out_path="dungeon_rooms.md"):
    with open(out_path, "w") as f:
        f.write(room_markdown(master))
    print(f"Saved room list to {out_path}")


def build_figure(master, subgraphs):
    """Build (but do not save) the matplotlib figure for the dungeon graph."""
    pos = nx.spring_layout(master, seed=1)
    node_colors = [ROLE_COLORS[master.nodes[n]["role"]] for n in master.nodes]
    labels = {n: f"{n}\n[{master.nodes[n]['role']}]" for n in master.nodes}

    fig = plt.figure(figsize=(9, 7))
    nx.draw(
        master,
        pos,
        with_labels=True,
        labels=labels,
        node_color=node_colors,
        node_size=700,
        font_size=8,
        font_weight="bold",
        edgecolors="black",
    )
    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=f"{r}: {ROOM_ROLES[r]}",
            markerfacecolor=ROLE_COLORS[r],
            markersize=10,
        )
        for r in ROOM_ROLES
    ]
    plt.legend(handles=handles, loc="upper left", bbox_to_anchor=(1, 1), title="Room role")
    plt.title(
        f"Five-room dungeon graph ({len(subgraphs)} modules, {master.number_of_nodes()} nodes)"
    )
    return fig


def draw_dungeon(master, subgraphs, out_path="dungeon_graph.png"):
    fig = build_figure(master, subgraphs)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved graphical representation to {out_path}")


def main():
    n = prompt_for_count()
    topologies = five_node_topologies()
    master, subgraphs = build_dungeon(n, topologies)
    print_summary(master, subgraphs)
    write_room_markdown(master)
    draw_dungeon(master, subgraphs)


if __name__ == "__main__":
    main()
