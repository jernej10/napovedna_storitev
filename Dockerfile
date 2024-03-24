FROM python:3.12.2  as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12.2 as runner

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN apt-get update && apt-get install -y libhdf5-dev

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY src /code/src

CMD ["uvicorn", "src.serve.server:app", "--host", "0.0.0.0", "--port", "8000"]