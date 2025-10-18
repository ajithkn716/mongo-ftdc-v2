# Use a base image
FROM ubuntu:20.04

# Allow architecture argument (set automatically by Docker BuildKit)
ARG TARGETARCH

# Set working directory
WORKDIR /app

# Copy architecture-specific binary
# Use conditional logic via a shell RUN command
# Instead of COPY (which doesn’t support runtime conditionals directly)
COPY src/ftdc_decoder_amd64 /tmp/ftdc_decoder_amd64
COPY src/ftdc_decoder_arm64 /tmp/ftdc_decoder_arm64

RUN if [ "$TARGETARCH" = "arm64" ]; then \
        cp /tmp/ftdc_decoder_arm64 /app/ftdc_decoder; \
    else \
        cp /tmp/ftdc_decoder_amd64 /app/ftdc_decoder; \
    fi && chmod +x /app/ftdc_decoder

# Copy other scripts
COPY src/main.sh /scripts/main.sh
COPY src/ftdc_parser.py /scripts/ftdc_parser.py
COPY src/get_url.py /scripts/get_url.py

# Set permissions
RUN chmod +x /scripts/main.sh

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
 && pip3 install ijson influxdb-client tqdm \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set entrypoint
ENTRYPOINT ["/scripts/main.sh"]

