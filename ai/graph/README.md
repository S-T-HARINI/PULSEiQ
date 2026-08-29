# PULSEiQ — Graph Module

## Overview
The `ai.graph` module leverages **NetworkX** to perform advanced electrical topology analysis, centrality rankings, islanding detection, and bridge/cut-point screening.

---

## Key Features

1. **Topology Graph Representation**:
   - **Nodes**: Conventional generators, solar PV, wind turbines, battery storage, substations, normal loads, and critical loads (hospitals, data centers).
   - **Edges**: Transmission and distribution lines with capacities, active power flows, impedance weights, and voltage ratings.

2. **Graph Analytics & Metrics**:
   - Degree centrality, betweenness centrality, closeness centrality.
   - Connected components (electrical islands).
   - Isolated bus and isolated load detection (loads cut off from generation sources).
   - Articulation point (cut vertex) and bridge (cut edge) identification.
   - Low-impedance shortest path analysis.

3. **Structured Analysis Output (`GraphAnalysisResult`)**:
   - Standardized dataclass serializable directly to JSON for FastAPI endpoints.

---

## Example Usage

```python
from ai.models.mock_grid import create_mock_grid
from ai.graph import (
    grid_to_networkx,
    analyze_graph_topology,
    find_connected_components,
    identify_important_nodes,
    find_shortest_path,
)

grid = create_mock_grid()
G = grid_to_networkx(grid)

# Full structured topology analysis
analysis = analyze_graph_topology(G, grid=grid)
print("Total Nodes:", analysis.node_count)
print("Connected:", analysis.is_connected)
print("Articulation Points:", analysis.articulation_points)
print("Bridges:", analysis.bridges)

# Shortest power transfer path
path = find_shortest_path(G, "gen_gas_01", "load_hospital_main")
print("Path to Hospital:", " -> ".join(path))
```
