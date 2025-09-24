FROM python:3.12.10-slim

WORKDIR /code

COPY ./requirements.txt /code/

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app
COPY ./.env /code/
COPY ./temp /code/temp

EXPOSE 8080

# CMD ["fastapi", "run", "app/main.py", "--port", "8080"]