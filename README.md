# 9559 TP Backend

# Requirements

- [uv](https://github.com/astral-sh/uv)
- `python`
- [docker](https://docs.docker.com/engine/install/) with `docker compose`

# Technologies

- Database: PostgreSQL
- Backend: Python with [FastAPI](https://fastapi.tiangolo.com/)
- Migrations: Alembic

# Development

Run the following command to develop with hot-reloading (every change made to the code will automatically be reloaded in the container):

```
docker compose watch
```

or use `make`

```
make watch
```

# API

The app will be running on `localhost:8000`. To use OpenAPI (which provides an interface to interact with the API) use `localhost:8000/docs`
