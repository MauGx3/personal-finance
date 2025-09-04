# Recreate with a fresh build
docker compose down --remove-orphans
docker compose build --no-cache --pull
docker compose up -d --remove-orphans

# Show running containers
docker compose ps

# Follow app logs (press Ctrl+C to stop)
docker compose logs -f --tail=200 app

# Open a shell in the running app container
docker compose exec app sh

# Quick smoke test from the host (adjust endpoint if different)
curl -sS -X GET http://localhost:8000/positions | jq .