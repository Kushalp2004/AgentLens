import sys
import argparse
from .server import start_ui

def main():
    parser = argparse.ArgumentParser(description="AgentLens - Multi-Agent Observability")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Define the 'ui' command
    ui_parser = subparsers.add_parser("ui", help="Start the local AgentLens dashboard")
    
    args = parser.parse_args()

    if args.command == "ui":
        start_ui()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()