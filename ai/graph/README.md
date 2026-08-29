# PULSEiQ — Graph Module

## Overview
The `ai.graph` module leverages **NetworkX** to represent and analyze the electricity grid topology.

Capabilities:
1. **Dynamic Topology Mutation**: Add nodes/edges, remove tripped lines/buses, simulate line outages.
2. **Connectivity & Islanding Detection**: Discover connected components, disconnected loads, and isolated generation islands.
3. **Graph Centrality & Hub Identification**: Degree centrality, betweenness centrality, and composite node importance rankings.
4. **Vulnerability Screening**: Find articulation points (cut vertices) and bridges (single lines of failure).
5. **Pathfinding & Serialization**: Low-impedance shortest path search and node-link JSON export.

---

## Example Usage

```python
from ai.models.mock_grid import create_mock_grid
from ai.graph import (
    grid_to_networkx,
    find_connected_components,
    identify_important_nodes,
    find_articulation_points,
    remove_failed_line,
)

grid = create_mock_grid()
G = grid_to_networkx(grid)

# Important nodes
hubs = identify_important_nodes(G, top_n=3)
for hub in hubs:
    print(f"Hub: {hub['name']} (Score: {hub['importance_score']})")

# Simulate line loss
remove_failed_line(G, "line_submain_to_subnorth")
islands = find_connected_components(G)
print("Connected Islands:", len(islands))
```
