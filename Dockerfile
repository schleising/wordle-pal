FROM python:3-alpine
ENV PYTHONUNBUFFERED=1

# Make the code directory
WORKDIR /code

# requirements.txt is exported by uv on a dev machine. Install it with pip.
COPY ./requirements.txt /code/
RUN apk add --no-cache --virtual .build-deps git \
    && pip install --no-cache-dir -r ./requirements.txt \
    && apk del .build-deps

# Run as a non-root user; /storage must be writable at runtime
RUN adduser -D -u 1000 appuser \
    && mkdir -p /storage \
    && chown -R appuser:appuser /storage /code

USER appuser

CMD [ "python", "wordlepalbot.py" ]
