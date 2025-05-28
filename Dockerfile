FROM python:3.11

WORKDIR /app

COPY poetry.lock pyproject.toml ./
COPY . .  


RUN pip install poetry && poetry config virtualenvs.create false && poetry install

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
