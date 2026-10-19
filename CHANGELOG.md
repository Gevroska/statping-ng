# 0.93.1 (10-19-2026)
- Fix CVE-2026-50884: ordinary user API keys no longer grant administrator access or expose administrator-only fields.
- Restrict GET /api/users to administrators and omit password hashes from the response.
- Restore the actual session role on startup and preserve regular-user login and dashboard reloads.

# 0.90.80 (01-26-2022)
- Fixed permissions on /app directory - Thanks twouters

# 0.90.79 (01-24-2022)
- Updated Russian Language - Thanks meatlayer
- Docker file fix for BASE_PATH and health checks - Thanks michaelkrieger
- Removed statping emailer notifier (not SMTP Mail)
- Fixes for notification failures (Issue statping#911) - Thanks glanchow
- Updated Home page uptime wording (24hr/7days) - Thanks Jonathanrbarney & thatInfrastructureGuy
- [GITHUB] Removed mailer tests

# 0.90.78 (09-15-2021)
- HTTP Webhooks accept multiple HTTP Headers
- Modified Telegram notifier to allow chat_ids
- New Notifier - Mattermost
- Updated German Language - Thanks Flofeld
- Czech Language - Thanks Fjuro
- Some minor branding Changes
- Moved some asset dependancies from assets.statping.com
- Fixed the (Ubuntu) Snap Store build script
- Retrospectively updated the Changelog
- [GITHUB] Fixed Windows/Mac autobuilds
- [GITHUB] Unstable container build
- [GITHUB] Triggers SNAP builds

# 0.90.77 (08-18-2021)
- More branding changes
- Fix for go statping-ng/email deps (https://github.com/statping-ng/statping-ng/issues/9)
- [GITHUB] Fixed autobuilds

# 0.90.76 (08-13-2021)
- Forked statping and renamed to statping-ng
- Branding changes
