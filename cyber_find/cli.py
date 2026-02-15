#!/usr/bin/env python3
"""
CyberFind CLI - Advanced OSINT search tool
Built-in site lists support
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Setup logging first
try:
    from cyber_find.logging_config import setup_logging

    setup_logging()
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)

try:
    from cyber_find import CyberFind, OutputFormat, SearchMode, run_api_server, run_gui
except ImportError:
    # Alternative import for development
    sys.path.insert(0, os.path.join(current_dir, "cyber_find"))
    try:
        from api import run_api_server as _run_api_server
        from core import CyberFind as _CyberFind
        from core import OutputFormat as _OutputFormat
        from core import SearchMode as _SearchMode
        from gui import run_gui as _run_gui

        run_api_server = _run_api_server  # type: ignore
        CyberFind = _CyberFind  # type: ignore
        OutputFormat = _OutputFormat  # type: ignore
        SearchMode = _SearchMode  # type: ignore
        run_gui = _run_gui  # type: ignore
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)


def print_banner():
    """Show application banner"""
    banner = """
    ╔══════════════════════════════════════════════╗
    ║           🕵️♂️ CYBERFIND v0.3                 ║
    ║      Advanced OSINT Search Tool              ║
    ╚══════════════════════════════════════════════╝
    """
    print(banner)


def show_builtin_lists():
    """Show available built-in site lists"""
    print("\n📚 AVAILABLE BUILT-IN SITE LISTS:")
    print("=" * 50)

    categories = {
        "quick": "25 most popular sites (default)",
        "social_media": "70+ social networks",
        "programming": "25+ IT and programming",
        "gaming": "20+ gaming platforms",
        "blogs": "20+ blogs and publications",
        "ecommerce": "20+ stores and commerce",
        "forums": "12+ forums",
        "russian": "18+ Russian-language platforms",
        "all": "200+ all sites",
    }

    for name, desc in categories.items():
        print(f"  {name:15} - {desc}")

    print("\n📖 USAGE EXAMPLES:")
    print("-" * 40)
    print("  cyberfind username                    # Quick check")
    print("  cyberfind username --list all         # All sites")
    print("  cyberfind username -f sites.txt       # From file")
    print("  cyberfind --show-lists                # Show lists")
    print("  cyberfind --gui                       # GUI interface")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="CyberFind - search for user accounts by username",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  # Quick check (25 most popular sites)
  cyberfind username

  # Use built-in lists
  cyberfind username --list social_media
  cyberfind username --list programming
  cyberfind username --list all

  # Multiple users
  cyberfind user1 user2 user3 --list quick

  # From sites file
  cyberfind username -f sites/social_media.txt

  # Advanced options
  cyberfind username --mode deep --format html -o report
  cyberfind username --format csv --threads 50 --timeout 15

  # Additional commands
  cyberfind --show-lists
  cyberfind --gui
  cyberfind --api
        """,
    )

    # Main arguments
    parser.add_argument(
        "usernames",
        nargs="*",
        help="Username to search for (multiple can be specified)",
    )

    parser.add_argument("-f", "--file", help="File with list of sites to check")

    parser.add_argument(
        "-l",
        "--list",
        choices=[
            "quick",
            "social_media",
            "programming",
            "gaming",
            "blogs",
            "ecommerce",
            "forums",
            "russian",
            "email",
            "phone",
            "all",
        ],
        help="Use built-in site list",
    )

    # Search modes
    parser.add_argument(
        "--mode",
        choices=[m.value for m in SearchMode],
        default="standard",
        help="Search mode (standard, deep, stealth, aggressive)",
    )

    parser.add_argument(
        "--format",
        choices=[f.value for f in OutputFormat],
        default="json",
        help="Output format for results",
    )

    parser.add_argument("-o", "--output", help="Filename to save results")

    # Performance settings
    parser.add_argument(
        "-t", "--threads", type=int, default=30, help="Number of concurrent requests"
    )

    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    # Email / Phone support
    parser.add_argument("--email", help="Search by email address")

    parser.add_argument("--phone", help="Search by phone number (E.164 format: +1234567890)")

    # Passive mode
    parser.add_argument(
        "--engines",
        default="google,bing,wayback",
        help="Comma-separated passive engines: google, bing, wayback",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Additional commands
    parser.add_argument("--show-lists", action="store_true", help="Show available built-in lists")

    parser.add_argument("--gui", action="store_true", help="Launch graphical interface")

    parser.add_argument("--api", action="store_true", help="Launch API server")

    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")

    parser.add_argument("--version", action="version", version="CyberFind v0.3")

    return parser.parse_args()


async def run_search(args, cyberfind):
    """Run search"""
    try:
        start_time = datetime.now()

        # Determine source of sites
        if args.list:
            print(f"📋 Using built-in list: {args.list}")
            builtin_list = args.list
            sites_file = None
        elif args.file:
            print(f"📋 Using file: {args.file}")
            builtin_list = None
            sites_file = args.file
        else:
            print("📋 Using default list: quick (25 sites)")
            builtin_list = "quick"
            sites_file = None

        # Run search
        results = await cyberfind.search_async(
            usernames=args.usernames,
            sites_file=sites_file,
            builtin_list=builtin_list,
            mode=SearchMode(args.mode),
            output_format=OutputFormat(args.format),
            output_file=args.output,
            max_concurrent=args.threads,
        )

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        return results, total_time

    except KeyboardInterrupt:
        print("\n\n⏹️ Search interrupted by user")
        raise
    except Exception as e:
        print(f"\n❌ Search error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        raise


async def run_passive_search(args, cyberfind):
    """Run passive reconnaissance"""
    try:
        start_time = datetime.now()

        # Build queries
        queries = []
        if args.usernames:
            for u in args.usernames:
                queries.append(f'"{u}"')
        if args.email:
            queries.append(f'site:gravatar.com "{args.email}"')
            queries.append(f'site:haveibeenpwned.com "{args.email}"')
        if args.phone:
            queries.append(f'site:t.me "{args.phone}"')
            queries.append(f'site:wa.me "{args.phone}"')

        engines = [e.strip() for e in args.engines.split(",")]

        results = await cyberfind.passive_search_async(
            queries=queries, engines=engines, max_concurrent=args.threads
        )

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        return results, total_time

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"\n❌ Passive search error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        raise


def print_results(results, total_time, args):
    """Print search results"""
    print(f"\n{'=' * 60}")
    print(f"✅ SEARCH COMPLETED in {total_time:.1f} seconds")
    print(f"{'=' * 60}")

    if "statistics" in results:
        stats = results["statistics"]
        print("\n📊 STATISTICS:")
        print(f"  Total checks: {stats.get('total_checks', 0)}")
        print(f"  Accounts found: {stats.get('found_accounts', 0)}")
        print(f"  Errors: {stats.get('errors', 0)}")

    if "results" in results:
        for username, data in results["results"].items():
            print(f"\n👤 USER: {username}")

            if data and "found" in data and data["found"]:
                found_count = len(data["found"])
                print(f"  ✅ FOUND {found_count} accounts:")

                # Group by categories
                categories = {}
                for account in data["found"]:
                    category = account.get("metadata", {}).get("category", "other")
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(account)

                # Print by categories
                for category, accounts in categories.items():
                    print(f"    📁 {category.upper()}:")
                    for i, account in enumerate(accounts, 1):
                        status_code = account.get("status_code", "N/A")
                        response_time = account.get("response_time", 0)
                        print(f"      {i:2d}. {account['site']}")
                        print(f"          URL: {account.get('url', 'N/A')}")
                        print(f"          Status: {status_code}, Time: {response_time:.2f}s")
            else:
                print("  ❌ No accounts found")

            # Show errors in verbose mode
            if args.verbose and data and "errors" in data and data["errors"]:
                error_count = len(data["errors"])
                if error_count > 0:
                    print(f"  ⚠️  Errors: {error_count}")
                    for i, error in enumerate(data["errors"][:5], 1):  # First 5 errors
                        print(
                            f"      {i}. {error.get('site', 'Unknown')}: {error.get('error', 'Unknown')}"
                        )
                    if error_count > 5:
                        print(f"      ... and {error_count - 5} more errors")

    # Recommendations from report
    if "report" in results and "recommendations" in results["report"]:
        recommendations = results["report"]["recommendations"]
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

    # Save information
    if args.output:
        output_path = args.output
        if not output_path.endswith(f".{args.format}"):
            output_path = f"{output_path}.{args.format}"
        print(f"\n💾 Results saved to: {output_path}")


def main():
    """Main function"""
    args = parse_arguments()

    has_search_target = bool(args.usernames or args.email or args.phone)
    has_command = bool(args.show_lists or args.gui or args.api)

    if not (has_search_target or has_command):
        print("❌ No search target or command specified")
        print("Use --help for help")
        return

    print_banner()

    if args.show_lists:
        show_builtin_lists()
        return

    if args.gui:
        run_gui()
        return

    if args.api:
        run_api_server()
        return

    search_targets = []
    if args.usernames:
        search_targets.extend(args.usernames)
    if args.email:
        search_targets.append(args.email)
    if args.phone:
        search_targets.append(args.phone)

    if not search_targets:
        print("❌ No search target specified")
        print("Examples:")
        print("  cyberfind username")
        print("  cyberfind --email target@example.com --list email")
        print("  cyberfind --phone +1234567890 --list phone")
        return

    # Print search information
    search_type = []
    if args.usernames:
        search_type.append(f"users: {', '.join(args.usernames)}")
    if args.email:
        search_type.append(f"email: {args.email}")
    if args.phone:
        search_type.append(f"phone: {args.phone}")

    if not search_type:
        print("❌ No search target specified")
        return

    # Print search information
    print(f"🔍 Searching: {' | '.join(search_type)}")
    print(f"📊 Mode: {args.mode}, Threads: {args.threads}, Timeout: {args.timeout}s")

    # Create CyberFind instance
    try:
        cyberfind = CyberFind(args.config)

        if args.timeout:
            cyberfind.config["general"]["timeout"] = args.timeout

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            if args.mode == "passive":
                # Passive mode
                results, total_time = loop.run_until_complete(run_passive_search(args, cyberfind))
            else:
                # Standard or email/phone mode
                results, total_time = loop.run_until_complete(run_search(args, cyberfind))

            print_results(results, total_time, args)

        except KeyboardInterrupt:
            print("\n\n⏹️ Search interrupted by user")
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
        finally:
            try:
                loop.close()
            except Exception:
                pass

    except Exception as e:
        print(f"❌ Initialization error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
