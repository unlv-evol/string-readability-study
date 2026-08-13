FROM python:3.10-slim

WORKDIR /app

# Install requirements early so code changes don't invalidate the layer cache
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Responses are written here when RESPONSE_STORAGE=local (the default).
# docker-compose mounts the host repository's data/responses over this path.
ENV RESPONSE_DIR=/data/responses
RUN mkdir -p /data/responses

EXPOSE 5000

# Bind to 0.0.0.0 so the port is reachable from outside the container.
# (app.py's own `app.run()` binds 127.0.0.1, which is unreachable from the host.)
ENV FLASK_APP=app.py
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
