# Facebook Group Campaign Manager (Python, PySide6)

A desktop app skeleton for managing Facebook group posting campaigns with persistent Chrome profiles, a batch-concurrency worker pool, libraries for posters/captions/links, scheduling, and logging.

## Quick Start

1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install
```

3) Run the app

```bash
python -m app
```

If the window opens with a left sidebar and multiple sections (Dashboard, Accounts, Groups, Posters, Captions, Links, Campaigns, Scheduler, Console, Logs, Settings), the skeleton is working.

## Packaging (Windows .exe)

1) Install PyInstaller (already in requirements)

```bash
pip install pyinstaller
```

2) Build executable

```bash
pyinstaller --noconfirm --clean \
	--name "FBGroupCampaignManager" \
	--windowed \
	--add-data "app;app" \
	-m app
```

Notes:
- On the target machine, run `python -m playwright install` once to ensure browsers are present, or bundle them by shipping the Playwright cache.
- You may need to add Playwright data directories to the bundle depending on your distribution method.
- The generated executable will be in `dist/FBGroupCampaignManager/`.

## Project Structure

```
app/
  core/
    app_context.py
    config.py
    db.py
    logger.py
    playwright_controller.py
    queue_manager.py
  services/
    account_service.py
    campaign_service.py
    worker_service.py
  ui/
    main_window.py
    views/
      dashboard.py
      accounts.py
      groups.py
      posters.py
      captions.py
      links.py
      campaigns.py
      scheduler.py
      console.py
      logs.py
      settings.py
  __init__.py
  __main__.py (entrypoint)
  main.py
```

## Notes

- This is a runnable skeleton. Posting logic with Playwright is not yet implemented.
- The app creates `data/` and `logs/` folders in the project root by default.
- Add secrets and proxy handling as needed.