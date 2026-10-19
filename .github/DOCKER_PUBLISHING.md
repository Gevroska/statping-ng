# Docker publishing for this fork

The development branch is `dev`. It is the default branch in both this fork and
upstream, and its initial commit `c02149f0a5f67fec1e60cfa3537478cd50899b15` is also
tagged `v0.93.0`. The inherited `stable` and `unstable` branches are older; they
are not the starting point for future fixes.

## Automatic publishing

The `Statping build` workflow builds the existing Dockerfile for `linux/amd64`,
`linux/arm64`, `linux/arm/v7`, and `linux/arm/v6`. Images are uploaded only after
the Docker build and the SQLite, MySQL, and PostgreSQL API tests succeed.

| Event | Image tags at `ghcr.io/gevroska/statping-ng` |
| --- | --- |
| Push to `dev`, or manual run on `dev` | `dev`, `br-dev`, `sha-<full-commit>` |
| Push a stable version tag such as `v0.93.1` | `0.93.1`, `0.93`, `0`, `latest`, `sha-<full-commit>` |
| Push a prerelease version tag such as `v0.93.1-beta.1` | Prerelease version and commit tags; no `latest` |
| Pull request or push to another branch | Build and test artifacts only; no registry upload |

Publishing uses the repository's temporary `GITHUB_TOKEN` with `packages: write`
permission. No Docker Hub password or personal access token is required. Images
are published into this fork's namespace, never the upstream namespace.

GitHub Actions must be enabled on the fork. A newly created GHCR package can be
private initially; set its visibility to public to permit pulls without a login.

## Future fixes and deployment

1. Base fixes on `dev` and merge or push them to `dev`.
2. Wait for `docker-publish` to succeed and verify the published image digest.
3. Test that exact image before changing the deployment. Use the immutable
   `sha-<full-commit>` tag or digest when a reproducible deployment is needed.
4. Create a new version tag on the tested commit to publish a versioned release
   and move `latest`. Existing tags should not be moved.
5. Updating this fork or publishing its image does not update a running container.
   Change the deployment image and recreate the container as a separate step.

This workflow configuration does not fix any application vulnerability. The
initial image still contains the upstream `v0.93.0` application code and must
not be treated as a patched release.
