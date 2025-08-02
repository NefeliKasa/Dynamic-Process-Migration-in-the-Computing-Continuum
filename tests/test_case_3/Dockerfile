FROM python:3.13-alpine

WORKDIR /app

RUN apk update && apk add --no-cache gcc

COPY ./tests/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./tests /app/tests
COPY ./k8s_utils /app/k8s_utils
COPY ./utils /app/utils

ENV PYTHONPATH=/app

CMD ["python", "-u", "tests/test_case_3/main.py"]