# PULSEiQ Data Directory

This directory stores datasets utilized by PULSEiQ forecasting, simulation, risk analysis, and optimization workflows.

## Directory Structure

```
data/
├── raw/            # Immutable raw source datasets (historical load profiles, weather data, SCADA logs)
└── processed/      # Cleaned, resampled, and feature-engineered datasets ready for model ingestion
```

## Data Types

1. **Load Profiles**: Historical hourly/sub-hourly active (MW) and reactive (MVAR) power demand across customer classes (residential, commercial, industrial, critical).
2. **Renewable Generation Profiles**: Solar irradiance, ambient temperature, wind speeds, and corresponding power outputs.
3. **Grid Topologies & Contingency Logs**: Network interconnection metadata, transformer limits, and historical equipment outage logs.
