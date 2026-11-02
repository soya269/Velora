# VELORA safe update notes

## Data preservation

- The existing `instance/velora.db` is retained in this package.
- Existing product, category, user, order, and order-item records were checked using SQLite read-only access.
- Do not delete `instance/velora.db` when deploying this update.
- Back up the live database before replacing application files on the VPS.

## Changes in this package

- Fixed invalid Python syntax in `api/user.py` and rewrote the administrator-only user API with validation and transaction rollback handling.
- Added validation for API user roles (`Admin`, `Staff`) and statuses (`Active`, `Inactive`).
- Prevented deleting the currently logged-in administrator through the API.
- Restricted admin login `next` redirects to same-host relative paths.
- Confirmed all Python source files compile successfully.
- Confirmed template `url_for` endpoint references correspond to registered route function names (apart from Flask's built-in `static` endpoint).

## Before deploying on Linux VPS

1. Stop the VELORA service.
2. Back up `/home/ubuntu/Velora/instance/velora.db` and `/home/ubuntu/Velora/static/uploads/`.
3. Back up the existing `.env` separately; do not replace it with `.env.example`.
4. Update application source files without deleting the live database or uploads.
5. Activate the existing virtual environment and install dependencies from `requirements.txt`.
6. Restart the service and inspect `sudo journalctl -u velora -n 100 --no-pager`.

## Important security notes

- Keep `.env` private and never commit it to GitHub.
- Set a long random `SECRET_KEY` in the server's `.env`.
- Rotate any Telegram bot token that has previously been shared or committed.
- The current forgot-password flow still needs a proper emailed, time-limited reset-token implementation before production use. Do not expose the reset endpoint publicly as a secure recovery mechanism until that is implemented.
- Run a full live route, form, upload, checkout, and order workflow test on the VPS before treating the deployment as production-ready.
