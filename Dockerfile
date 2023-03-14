FROM python:3.10-slim-buster

WORKDIR /app
EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org poetry

COPY . .

RUN poetry config virtualenvs.create false --local && \
    poetry install

CMD ["gunicorn", "validator.wsgi:application", "--bind", "0.0.0.0:8000"]
