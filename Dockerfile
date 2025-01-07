# Dagster libraries to run both dagster-webserver and the dagster-daemon. Does not
# need to have access to any pipeline code.

FROM python:3.12-slim

COPY . .

# Checkout and install dagster libraries needed to run the gRPC server
# exposing your repository to dagster-webserver and dagster-daemon, and to load the DagsterInstance

RUN pip install -e .[dev]
RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-docker

# Set $DAGSTER_HOME and copy dagster instance and workspace YAML there
ENV DAGSTER_HOME=/opt/dagster/dagster_home/

RUN mkdir -p $DAGSTER_HOME

COPY dagster.yaml $DAGSTER_HOME

WORKDIR /opt/dagster/app

COPY dagster_app/ /opt/dagster/app/dagster_app/

COPY workspace.yaml /opt/dagster/app/

EXPOSE 3000

# Copy the entrypoint script
COPY entrypoint.sh /opt/dagster/app/

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]