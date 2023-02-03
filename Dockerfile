# Pull base image
FROM python:3.9

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Copy project
COPY . /code/

# Install dependencies
RUN pip install -r requirements.txt
RUN rm -rf /code/api/migrations/*.*

# Create superuser
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh