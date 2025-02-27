FROM python:3.12.9-slim-bookworm

RUN apt-get -y update && apt-get install -y --no-install-recommends git

WORKDIR /usr/src/app

COPY . .
RUN pip install . --no-cache-dir

COPY . .

EXPOSE 8000
ENTRYPOINT [ "clinical-recommendations-server" ]