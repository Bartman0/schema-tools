FROM python:3.9-bookworm

RUN useradd --user-group --system datapunt
RUN apt-get update && apt install -y libgdal32

WORKDIR /app
COPY . ./
RUN pip install psycopg2-binary
RUN pip install -e "."
# So we can use local schemas
RUN git clone https://github.com/Amsterdam/amsterdam-schema.git /tmp/ams-schema
USER datapunt

ENTRYPOINT "/bin/bash"
CMD "schema"
