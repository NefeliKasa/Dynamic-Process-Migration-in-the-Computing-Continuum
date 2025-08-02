FROM --platform=linux/arm64 python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    gcc \
    python3-dev \
    build-essential \
    tar \
  && curl -sL https://packages.confluent.io/deb/7.6/archive.key | apt-key add - \
  && echo "deb [arch=arm64] https://packages.confluent.io/deb/7.6 stable main" > /etc/apt/sources.list.d/confluent.list \
  && apt-get update && apt-get install -y librdkafka-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./orchestration_layer/sidecar_controller/requirements.txt /tmp/requirements.txt
RUN pip install --prefix=/install --no-cache-dir -r /tmp/requirements.txt

COPY ./orchestration_layer/sidecar_controller /app
COPY ./container_migration /app/container_migration
COPY ./nats_prod /app/nats_prod
COPY ./k8s_utils /app/k8s_utils
COPY ./utils /app/utils

FROM --platform=linux/arm64 python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    buildah \
    runc \
    uidmap \
    tar \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY --from=builder /app /app

CMD ["python", "-u", "main.py"]
