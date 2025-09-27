# Personal Finance - Portainer stack deployment

This folder contains example environment variables and notes for deploying the project
as a Docker stack using Portainer (or Docker Compose in non-swarm mode).

Quick steps (Portainer web UI):

1. Create a new Stack in Portainer and choose "Repository" or "Upload" depending on how you want to deploy.

2. If using "Repository", point Portainer to this repository and select the branch you want to deploy.

3. Paste the contents of `docker-compose.yml` as the stack file or reference it if using the repository option.

4. In "Environment variables" upload or paste `stack.env.example` values and replace:

   - `DJANGO_SECRET_KEY` with a secure random secret

   - `DATABASE_URL` with your production DB URL (if using an external DB, set the host and port accordingly). The repo's compose maps host port 52135 -> container 5432.

5. Ensure the build environment in Portainer has sufficient RAM/CPU for building Docker images, or pre-build images and change service `image:` to a prebuilt tag.

6. Start the stack. If `RUN_MIGRATIONS_ON_START=1` migrations will run on container start (this may fail if the DB is not reachable).

Notes:

- The `docker-compose.yml` in the repo aims to be stack-friendly. Avoid `container_name` when running multiple stacks on the same host.

- For Portainer, preferring prebuilt images (push to a registry) provides faster and more reliable deploys; building from repo in Portainer requires build tooling to be available on the Portainer host.

- The project exposes a health endpoint at `/health/` and an alias `/kaithhealth` for platforms that probe that path.
