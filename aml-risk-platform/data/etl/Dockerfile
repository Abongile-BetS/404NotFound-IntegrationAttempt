FROM python:3.12-slim

WORKDIR /etl

COPY requirements.txt .

RUN pip install \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

COPY src ./src

CMD ["sh", "-c", "python src/ingestion.py && python src/normalized_load.py"]

CMD ["sh", "-c", "python src/denormalized_load.py"]

CMD ["sh", "-c", "echo 'hello'"]