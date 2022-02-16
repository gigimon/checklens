# What is this?

This repository created as test task for CheckLens company

# How it?
Project uses poetry for virtualenv and dependency resolution.

This's small flask project with 2 endpoints:
1. "/" - only POST
2. "/ping" - only GET for tests


# Start

To run use docker-compose:

```bash
docker-compose up
```


# Testing

For testing we need to initialize poetry environment and run this:

```bash
poetry run py.test tests
```

Or You can use docker for this:

```bash
docker-compose up
docker exec -it checklens_app_1 poetry run py.test
```