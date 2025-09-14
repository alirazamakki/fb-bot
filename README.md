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
```

3) Install Playwright browsers (one-time per machine)

```bash
python -m playwright install
```

4) Run the app

```bash
python -m app
```

If the window opens with a left sidebar and multiple sections (Dashboard, Accounts, Groups, Posters, Captions, Links, Campaigns, Scheduler, Console, Logs, Settings), the skeleton is working.

## Project Structure

```
app/
  core/
    config.py
    db.py
    logger.py
    playwright_controller.py
    queue_manager.py
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
```

## Notes

- This is a runnable skeleton. Models, worker logic, Playwright posting steps, and full UI are stubs you can extend.
- The app creates `data/` and `logs/` folders in the project root by default.
- Packaging (PyInstaller), encryption, proxies, and full DB models will be added next.