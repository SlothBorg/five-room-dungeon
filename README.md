# Five Room Dungeon generator

A script to procedurally generates a dungeon made of interconnected
five-node modules, each node being one of the five rooms in the the classic Five Room Dungeon.

| Room | Meaning |
|---|---------|
| 1 | Entrance / Guardian |
| 2 | Puzzle / Roleplay Challenge |
| 3 | Trick / Setback |
| 4 | Climax / Big Battle |
| 5 | Reward / Revelation |

## Background

I came across the idea via the Gnome Stew blog post [*The Twenty-One Forms of the Five Room Dungeon*](https://gnomestew.com/the-twenty-one-forms-of-the-five-room-dungeon/), which references Steve Lawford's paper ["Counting five-node subgraphs"](https://enac.hal.science/hal-03097484/document). 
The paper proves there are 21 distinct simple graphs of five nodes, see table 1 in the paper.
The blog post points out how this maps neatly onto the "five room dungeon" design pattern.

This script pulls those 21 topologies from `networkx`'s built-in graph
atlas, rather than trying to wrap my mind around the math in the paper, and uses them to build a full dungeon out of five-room modules.

## What it does

1. Prompts you for an integer `n`.
2. Generates `n` five-node subgraphs, each randomly chosen from the 21 topologies.
3. Assigns each node a room role 1–5, ee table below; every module contains each role exactly once.
  
4. Connects each subgraph, after the first, to 1–3 of the existing modules.
   1. The connection chance is weighted: 50% 1, 30% 2, 20% 1.
5. Creates an image of the dungeon with lables, saved to `dungeon_graph.png`.
6. Creates a markdown table listing every room, its role, and what rooms it connects to, saved to `dungeon_rooms.md`.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
```
