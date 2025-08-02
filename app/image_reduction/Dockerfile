FROM python:3.11-slim
WORKDIR /app

RUN pip install tensorflow keras scikit-learn numpy

COPY ./app/image_reduction/image_reduction.py /app/

CMD ["python", "image_reduction.py"]