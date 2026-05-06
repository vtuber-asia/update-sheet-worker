FROM python:3.12-slim AS builder

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

FROM python:3.12-slim AS runtime

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        libxml2 \
        libxslt1.1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home --home-dir /home/app --shell /usr/sbin/nologin app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app \
    auth.py \
    content_platform.py \
    gservices.py \
    main_youtube_by_channel_id.py \
    setup.py \
    upload.py \
    upload_youtube.py \
    upload_youtube_by_channel_ids.py \
    utils.py \
    youtube.py \
    youtube_by_channel_ids.py \
    ./

RUN mkdir -p \
        outputs \
        csv/id/outputs \
        csv/kh/outputs \
        csv/my/outputs \
        csv/ph/outputs \
        csv/sg/outputs \
        csv/th/outputs \
        csv/vn/outputs \
    && chown -R app:app /app

USER app

CMD ["python", "main_youtube_by_channel_id.py"]
