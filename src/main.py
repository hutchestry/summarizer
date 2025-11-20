import argparse
from .service import service_install, service_remove


def cli():
    parser = argparse.ArgumentParser(prog="summarizer", description="Summarizer CLI")
    sub = parser.add_subparsers(dest="command")

    # run once
    sub.add_parser("run", help="Run summarizer immediately")

    # service install/remove
    sub.add_parser("service-install", help="Install macOS LaunchAgent (3AM)")
    sub.add_parser("service-remove", help="Remove macOS LaunchAgent")

    args = parser.parse_args()

    if args.command == "run":
        return run_once()
    elif args.command == "service-install":
        return service_install()
    elif args.command == "service-remove":
        return service_remove()
    else:
        # default: run once
        return run_once()


def run_once():
    import datetime
    from .extractors import get_all_entries
    from .markdown_gen import write_daily, write_weekly
    from .config import DAYS_FOR_WEEKLY

    today = datetime.date.today()
    all_entries = get_all_entries()

    daily = [e for e in all_entries if e["last_visit"].date() == today] or all_entries[:1000]
    write_daily(today, daily)

    start = today - datetime.timedelta(days=DAYS_FOR_WEEKLY - 1)
    weekly = [e for e in all_entries if start <= e["last_visit"].date() <= today]
    write_weekly(start, today, weekly)

    print("✅ Summarizer run complete.")
