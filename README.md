# ProChessGame

A real‑time, multiplayer chess platform built with **Django 5**, **Django Channels 5**, **Redis**, and **WebSockets**.
Players can register, challenge other online users, and play turn‑based chess that updates instantly across the board.

---

## Features

* **Live Gameplay** – moves and resignations broadcast over WebSockets
* **Online Presence** – sidebar shows only users who are currently logged‑in
* **Invite System** – send / accept invites; auto‑spawns a new game
* **Game History & Journal** – track results and add post‑game notes
* **Autoscaling Docker Images** – multi‑arch (arm64 + amd64) images pushed to GCP Artifact Registry
* **CI / CD** – GitHub Actions lint + tests → Docker Buildx → GCP deploy

---

## Quick Start (Local)

```bash
# Clone & set‑up
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate && python manage.py createsuperuser
redis-server &              # separate terminal
python manage.py runserver 0.0.0.0:8000
```

Open [http://127.0.0.1:8000/chess/join/](http://127.0.0.1:8000/chess/join/) in two browser windows and play!

---

## Docker

```bash
# build multi‑arch image (amd64 target)
docker buildx build \
  --platform linux/amd64 \
  -t rishi2772001/prochessgame:v2-amd64 \
  --push .
# run with redis sidecar
docker compose up -d
```

`docker-compose.yml` exposes **host 80 → container 8000**.

---

## Google Cloud Deployment (summary)

1. **Artifact Registry**
   `REGION-docker.pkg.dev/PROJECT/REPO/prochessgame:v2-amd64`
2. **Instance Template** – “Deploy container” → image above; env `REDIS_HOST=redis`
3. **Managed Instance Group** – min 2, max 4, health‑check **GET /chess/join/ 80**
4. **Global HTTP(S) Load Balancer** – frontend port 80/443; backend MIG
5. **Cloud DNS** – `A  game.prochessgame.com → LB_IP`

Full step‑by‑step is in [`docs/gcp_deploy.md`](docs/gcp_deploy.md).

---

## Project Layout

```
Chess_Game/
├─ Chess_app/         # Django app (models, views, consumers)
│  └─ templates/
├─ static/            # CSS + JS
├─ docker‑compose.yml # dev stack (web + redis)
├─ Dockerfile         # multi‑arch build
└─ README.md          # you are here
```

---

## Contributing

Pull‑requests are welcome!
Please run `ruff --fix` and `pytest` before opening a PR.

---

## License

MIT © 2025 Rishi Ganji
