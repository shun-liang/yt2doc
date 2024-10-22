FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ADD . /app
WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && apt-get install -y git
RUN uv tool install .

ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT ["yt2doc"]
