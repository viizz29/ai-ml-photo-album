# image classification based on face

This project uses Docker Compose to run both the API and a PostgreSQL database.

The default database connection in `.env` points the API container at the Compose database service:

```env
DATABASE_URL=postgresql://user:password@db:5432/app
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=app
```

Start the API:

```bash
docker compose up --build
```

Apply database migrations after the containers are up:

```bash
docker compose exec api alembic upgrade head
```

If the Compose database already contains these tables from the earlier `create_all()` setup, mark the initial migration as applied instead:

```bash
docker compose exec api alembic stamp head
```

Create a new migration after changing SQLAlchemy models:

```bash
docker compose exec api alembic revision --autogenerate -m "describe change"
```

Seed default users:

```bash
docker compose exec api python app/seed_users.py
```

You can also run it as a module:

```bash
docker compose exec api python -m app.seed_users
```

# access the database using psql

docker compose exec db psql -U user -d app
