Prometheus stack (repo-first)
==============================

This folder contains a minimal Prometheus configuration and a small compose stack that uses a repo-relative bind mount so the stack can be deployed from Portainer in non-Swarm environments.

What is included

- `prometheus.yml` — minimal Prometheus configuration. Adjust `scrape_configs` to point to your exporters/targets.
- `docker-compose.prometheus.yml` — compose file which mounts the repo file into the container. This avoids absolute host path mounts and works with Portainer's non-Swarm deploy.

How to deploy in Portainer (non-Swarm)

1. Deploy as a stack from repository and choose this compose file path: `monitoring/prometheus/docker-compose.prometheus.yml`.
2. Portainer will use the repository files as the stack working dir; the compose file mounts `./prometheus/prometheus.yml` into the container.

Notes and alternatives

- If you *can* use Swarm, a cleaner approach is to use Docker configs. The repo also contains a `prometheus.yml` which you can wire up as a Swarm config. For Swarm mode, use a compose file that contains `configs:` instead of a bind mount.

- If you prefer the config baked into an image, create a small Dockerfile which copies `prometheus.yml` into `/etc/prometheus/` and refer to that image in the compose file.

Security

- Avoid exposing Prometheus to the public internet. Use reverse proxies with authentication, firewall rules, or private networks.
