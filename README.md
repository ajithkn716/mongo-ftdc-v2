# mongo-ftdc-v2

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Docker Pulls](https://img.shields.io/docker/pulls/ajithkn716/mongo-ftdc-v2)](https://hub.docker.com/r/ajithkn716/mongo-ftdc-v2)  
[![InfluxDB](https://img.shields.io/badge/InfluxDB-v2.7-blue)](https://www.influxdata.com/)  
[![Grafana](https://img.shields.io/badge/Grafana-v10-orange)](https://grafana.com/)  

Analyze and visualize MongoDB FTDC metrics with InfluxDB and Grafana.

**mongo-ftdc-v2** decodes MongoDB FTDC diagnostic data and sends all available metrics to a Dockerized InfluxDB instance. You can then use InfluxDB queries to build custom Grafana dashboards for performance monitoring and troubleshooting.

⚠️ **Credit:** This project is based on [Big-hole](https://github.com/zelmario/big-hole) by @zelmario, inspired by the Keyhole approach for MongoDB metrics visualization.

---

## Table of Contents

- [Author](#author)  
- [Features](#features)  
- [Parallel Processing](#parallel-processing)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Grafana Dashboard](#grafana-dashboard)  
- [InfluxDB Access](#influxdb-access)  
- [Reloading New Data](#reloading-new-data)  
- [License](#license)  
- [Contributing](#contributing)  

---

## Author

- **Author:** Ajithkumar N / ajithkn716  
- **Original Project:** [Big-hole](https://github.com/zelmario/big-hole) by @zelmario

---

## Features

- Decode all MongoDB FTDC metrics from diagnostic data files  
- Store metrics in InfluxDB for querying and visualization  
- Fully Dockerized deployment for quick setup  
- Parallel processing support for faster decoding (multiple worker threads & files processed simultaneously)  
- Enhanced Grafana dashboard with multiple well-organized panels:

| Category                     | Panels |
|-------------------------------|-------|
| System Metrics                | 9     |
| MongoDB - General             | 1     |
| MongoDB - Overview            | 12    |
| MongoDB - WiredTiger          | 8     |
| MongoDB - Oplog               | 2     |
| MongoDB - ReplicaSet          | 4     |
| Available Metrics Reference   | 1     |

---

## Parallel Processing

Configure worker threads and parallel file processing using environment variables:

```bash
# Number of worker threads for decoding metrics
MAX_WORKERS=2

# Number of files to process in parallel
MAX_FILE_PROCESS=1
```

Adjust values according to CPU capacity and dataset size.

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/mongo-ftdc-v2.git
cd mongo-ftdc-v2

# Make the main script executable
chmod +x mongo-ftdc.sh

# Build the Docker containers
docker-compose build
```

## Usage

### 1. Prepare Diagnostic Data

MongoDB FTDC (Full-Time Diagnostic Data Capture) files are required for processing. These files usually have names like `metrics.*` and are generated in the MongoDB `diagnostic.data` directory or a custom folder if you have enabled FTDC.

Steps to prepare:

```bash
# 1. Create a local directory to store FTDC files inside the mongo-ftdc-v2 folder
mkdir -p ./diagnostic.data/

# 2. Copy all FTDC metrics files into the local directory
cp /path/to/ftdc/files/metrics.* ./diagnostic.data/

Replace /path/to/ftdc/files/ with the actual path where your MongoDB FTDC files are stored.
```

### 2. Run the Script

```bash
./mongo-ftdc.sh
```

The script will:

- Decode all FTDC files (may take a few minutes depending on the number of files).
- Launch three Docker containers:
   - InfluxDB: Stores all metrics
   - Metrics Processor: Decodes FTDC files and sends data to InfluxDB
   - Grafana: Visualize metrics

### 3. Access Grafana Dashboard:

`Default Grafana URL: http://localhost:3001/`

Login credentials:

```bash
user: admin
pass: admin
```

#### Dashboard Highlights:

- Metrics grouped into categories: System, MongoDB Overview, Network, WiredTiger, Oplog and ReplicaSet
- Each panel provides detailed insights into MongoDB performance
- Special metric field panel shows all available metrics/fields for reference when creating custom dashboards

#### Dashboard Screenshots:

![Screenshoot](https://github.com/ajithkn716/mongo-ftdc-v2/blob/main/mongo-ftdc-v2.png?raw=true)

![Screenshoot](https://github.com/ajithkn716/mongo-ftdc-v2/blob/main/mongo-ftdc-v2-1.png?raw=true)

## Reloading New Data

To process new FTDC files:

```bash
# Stop the containers (Ctrl-C)
# Replace files in diagnostic.data/
# Run the script again
./mongo-ftdc.sh
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are very welcome! Your feedback and suggestions are especially valuable.  

If you notice any issues, have ideas to improve the script or want to add new features, please feel free to contribute:

1. **Fork the repository**  
2. **Make your changes**  
3. **Submit a pull request**  

Your help will make this project more robust and useful for the MongoDB community. Thank you for contributing! 🙂
