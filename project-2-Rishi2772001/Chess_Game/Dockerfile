FROM python:3.12-slim

# ---------- runtime basics ----------
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# ---------- deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- source ----------
COPY . .
RUN python manage.py collectstatic --noinput

# ---------- serve ----------
EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "Chess_Game.asgi:application"]
