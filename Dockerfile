# start by pulling the python image
FROM python:3.8-alpine


# copy essential files from the local to the image
COPY smartrade /app/smartrade/
COPY requirements.txt /app
COPY tmp/ext /app/

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# run flask app
#ENTRYPOINT ["python3", "-m", "flask", "run"]
