#!/usr/bin/env python3
"""
Author: najith716@gmail.com

Description:
    Fetches the first and last timestamps from the 'ftdc' measurement in InfluxDB,
    then constructs and prints a Grafana dashboard URL using those values.
"""

from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
import urllib.parse
import sys

# ─────────────────────────────────────────────
# InfluxDB Configuration
# ─────────────────────────────────────────────
INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "ftdc"
INFLUX_ORG = "percona"
INFLUX_BUCKET = "ftdc"

# ─────────────────────────────────────────────
# Flux Query Templates
# ─────────────────────────────────────────────
FLUX_QUERY_TEMPLATE = """
from(bucket: "{bucket}")
  |> range(start: -1y)
  |> filter(fn: (r) => r._measurement == "ftdc")
  |> filter(fn: (r) => r._field == "serverStatus.localTime")
  |> group()
  |> {fn}()
  |> yield(name: "{fn}_value")
"""

# ─────────────────────────────────────────────
# Helper Function to Run Query
# ─────────────────────────────────────────────
def get_value(client, org, bucket, fn):
    """Fetch a single value (first or last) using Flux."""
    query = FLUX_QUERY_TEMPLATE.format(bucket=bucket, fn=fn)
    try:
        result = client.query_api().query(org=org, query=query)
        for table in result:
            for record in table.records:
                return record.get_value()
    except InfluxDBError as e:
        print(f"InfluxDB query error ({fn}): {e}", file=sys.stderr)
    return None

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    print("Connecting to InfluxDB...")

    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
        first_value = get_value(client, INFLUX_ORG, INFLUX_BUCKET, "first")
        last_value = get_value(client, INFLUX_ORG, INFLUX_BUCKET, "last")

        if not first_value or not last_value:
            print("Failed to retrieve first or last timestamp.")
            sys.exit(1)

        # Build Grafana dashboard URL
        base_url = "http://localhost:3001/d/ddnw277huiv40ae/ftdc-dashboard"
        params = {
            "orgId": 1,
            "from": first_value,
            "to": last_value
        }

        dashboard_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        print("\nAccess your dashboard at:")
        print(dashboard_url)
        print()

if __name__ == "__main__":
    main()
