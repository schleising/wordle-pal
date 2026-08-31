FROM python:3-alpine
ENV PYTHONUNBUFFERED=1

# Make the code directory
WORKDIR /code

# Install requirements
COPY ./requirements.txt /code/
RUN pip install --no-cache-dir -r ./requirements.txt

# Run as a non-root user; /storage must be writable at runtime
RUN adduser -D -u 1000 appuser \
    && mkdir -p /storage \
    && chown -R appuser:appuser /storage /code

USER appuser

CMD [ "python", "wordlepalbot.py" ]
