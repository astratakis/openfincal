# Python image for Service keycloak-init
FROM python:3.13

# Working directory
WORKDIR /usr/src/app

# Copy requirements 
COPY requirements.txt .

# Upgrade pip and install all requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy everything to the docker image
COPY . .

ENV PYTHONPATH=/usr/src/app/src

CMD exec uvicorn src.main:api --host 0.0.0.0 --port ${PORT:-8000} --reload