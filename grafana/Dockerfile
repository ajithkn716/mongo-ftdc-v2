# Start from the official Grafana image
FROM grafana/grafana:main-ubuntu

USER root
# Copy provisioning configuration into the image
COPY grafana/datasources.yaml /etc/grafana/provisioning/datasources/datasources.yaml
COPY grafana/main.yaml /etc/grafana/provisioning/dashboards/main.yaml
COPY grafana/dashboards/ /etc/grafana/provisioning/dashboards/

RUN chown -R grafana /etc/grafana

# Expose Grafana port
EXPOSE 3000
USER grafana
# Start Grafana
ENTRYPOINT ["/run.sh"]
