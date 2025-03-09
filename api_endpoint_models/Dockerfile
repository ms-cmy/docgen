FROM nvidia/cuda:12.1.1-base-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    gcc \
    g++ \
    libgl1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


RUN pip install --no-cache-dir \
    flask \
    torch \
    transformers

EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0"]