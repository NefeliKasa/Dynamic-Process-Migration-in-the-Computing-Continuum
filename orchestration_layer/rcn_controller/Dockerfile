FROM python:3.13-alpine

WORKDIR /app

RUN apk update && apk add --no-cache gcc

COPY ./orchestration_layer/rcn_controller/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./orchestration_layer/rcn_controller /app
COPY ./k8s_utils /app/k8s_utils
COPY ./utils /app/utils

CMD ["python", "-u", "main.py"]