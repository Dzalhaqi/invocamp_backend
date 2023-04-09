FROM postgres:14.7-bullseye
RUN apt-get update && \
  apt-get install -y --no-install-recommends postgresql-14-postgis-3 && \
  rm -rf /var/lib/apt/lists/*
