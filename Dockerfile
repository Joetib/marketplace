# Pull base image
FROM python:3.8-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code



# Install dependencies
COPY requirements.txt /code/
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    && pip install -r requirements.txt

# Copy project
COPY . /code/
EXPOSE 80
CMD [ "python", "/code/manage.py", "runserver", "0.0.0.0:80"]