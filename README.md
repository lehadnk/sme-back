# Running dev version
```bash
docker compose -f inf/docker-compose.dev.yml
cat inf/db.sql | docker exec -i spe-postgres psql -U postgres -d postgres
docker exec -i spe-clickhouse clickhouse-client -n < inf/ch.sql
poetry install
cd src
uvicorn app:app --reload
```