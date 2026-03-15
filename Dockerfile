# base image
FROM python:3.11-slim

#  for preventing creation of .pyc file  
ENV PYTHONDONTWRITEBYTECODE=1
#for logging
ENV PYTHONUNBUFFERED=1


WORKDIR /app

# istall linux system dependencies
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# installing python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . .

# checking if services are ready
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

