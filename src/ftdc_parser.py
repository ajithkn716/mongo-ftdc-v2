#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: najith716@gmail.com

Description:
    Streams MongoDB FTDC JSON metrics, processes them in parallel
    and writes them to InfluxDB efficiently.
"""

import argparse
import ijson
import re
import time
import os
import math
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.exceptions import InfluxDBError

# ─────────────────────────────────────────────
# ⚙️ Constants and Configuration
# ─────────────────────────────────────────────
MAX_INT64 = 2**63 - 1

INFLUX_CONFIG = {
    "url": "http://influxdb:8086",
    "token": "ftdc",
    "org": "percona",
    "bucket": "ftdc",
}

BATCH_SIZE = 5000

# ─────────────────────────────────────────────
# Automatic CPU-based worker calculation
# ─────────────────────────────────────────────
def determine_max_workers(file_idx=None, file_total=None):
    """Determine max worker threads based on env or CPU count."""
    env_max_workers = os.getenv("MAX_WORKERS")
    prefix = f"[{file_idx}/{file_total}] " if file_idx and file_total else ""

    if env_max_workers:
        try:
            max_workers = int(env_max_workers)
            print(f"{prefix}Using MAX_WORKERS from environment variable: {max_workers}")
            return max_workers
        except ValueError:
            print(f"{prefix}Invalid MAX_WORKERS env value '{env_max_workers}', falling back to auto calculation")

    cpu_cores = os.cpu_count() or 1
    if cpu_cores <= 2:
        max_workers = cpu_cores
    else:
        max_workers = max(1, round(cpu_cores / 2))

    print(f"{prefix}Detected {cpu_cores} CPU cores → using {max_workers} worker threads")
    return max_workers

# ─────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="Process a FTDC JSON metrics file.")
    parser.add_argument("file_path", type=str, help="Path to the FTDC-decoded JSON file.")
    parser.add_argument("file_idx", type=int, help="Index of the file being processed")
    parser.add_argument("file_total", type=int, help="Total number of files")
    return parser.parse_args()

def safe_value(value):
    """Safely convert and clamp values for InfluxDB."""
    try:
        if value is None:
            return 0
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return min(value, MAX_INT64)
        return float(value)
    except Exception:
        return 0

def generate_timestamps(metric_set):
    """Extract timestamps from metric set."""
    return metric_set.get("DataPointsMap", {}).get("serverStatus.localTime", [])

# ─────────────────────────────────────────────
# Metrics Processing
# ─────────────────────────────────────────────
def process_metrics(metric_set):
    """Transform metric_set into a list of InfluxDB points."""
    timestamps = generate_timestamps(metric_set)
    data_map = metric_set.get("DataPointsMap", {})
    points_dict = {}

    for key, values in data_map.items():
        for ts, value in zip(timestamps, values):
            points_dict.setdefault(ts, {})[key] = safe_value(value)

    points = []
    for ts, fields in points_dict.items():
        timestamp = datetime.fromtimestamp(ts / 1000)
        point = Point("ftdc").time(timestamp, WritePrecision.MS)
        for key, value in fields.items():
            point = point.field(key, value)
        points.append(point)
    return points

def process_batch(write_api, batch, bucket, org, file_idx, file_total):
    """Process a batch of metrics and write to InfluxDB."""
    all_points = []
    for metric_set in batch:
        all_points.extend(process_metrics(metric_set))
    try:
        write_api.write(bucket=bucket, org=org, record=all_points)
    except InfluxDBError as e:
        print(f"[{file_idx}/{file_total}] InfluxDB write error: {e}")
    except Exception as e:
        print(f"[{file_idx}/{file_total}] Unexpected error: {e}")

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    args = parse_args()
    file_idx = args.file_idx
    file_total = args.file_total

    # Compute max workers based on environment or CPU
    global MAX_WORKERS
    MAX_WORKERS = determine_max_workers(file_idx, file_total)

    print(f"[{file_idx}/{file_total}] Connecting to InfluxDB...")
    with InfluxDBClient(
        url=INFLUX_CONFIG["url"],
        token=INFLUX_CONFIG["token"],
        org=INFLUX_CONFIG["org"]
    ) as client:
        write_api = client.write_api()
        batch = []
        futures = []

        print(f"[{file_idx}/{file_total}] Streaming and processing JSON data...")
        try:
            with open(args.file_path, "r") as file:
                objects = ijson.items(file, "Data.item")

                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    for metric_set in tqdm(objects, desc=f"[{file_idx}/{file_total}] Processing metrics"):
                        batch.append(metric_set)
                        if len(batch) >= BATCH_SIZE:
                            futures.append(executor.submit(
                                process_batch, write_api, batch, INFLUX_CONFIG["bucket"], INFLUX_CONFIG["org"], file_idx, file_total
                            ))
                            batch = []

                    # Submit remaining batch
                    if batch:
                        futures.append(executor.submit(
                            process_batch, write_api, batch, INFLUX_CONFIG["bucket"], INFLUX_CONFIG["org"], file_idx, file_total
                        ))

                    # Wait for all threads to complete
                    for future in as_completed(futures):
                        future.result()
        except Exception as e:
            print(f"[{file_idx}/{file_total}] Error processing file {args.file_path}: {e}")

        # Flush pending writes and close
        time.sleep(1)

    print(f"[{file_idx}/{file_total}] Chunk processed successfully!")
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
