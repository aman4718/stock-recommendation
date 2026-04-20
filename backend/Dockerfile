FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-generate embeddings if data/ not already committed
# (runs seed.py only when docs.json is missing)
RUN python -c "
import os, pathlib
d = pathlib.Path('data/docs.json')
if not d.exists():
    print('data/docs.json not found — running seed.py ...')
    os.system('python seed.py')
else:
    print(f'data/docs.json exists ({d.stat().st_size} bytes) — skipping seed.')
"

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
