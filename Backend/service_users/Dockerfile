FROM python:3.11-slim
WORKDIR /app
# Install build deps needed if you enable bcrypt (passlib[bcrypt])
# These packages are required to build the optional 'bcrypt' wheel during pip install.
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	libffi-dev \
	libssl-dev \
 && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app /app/app
RUN mkdir -p /data
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
