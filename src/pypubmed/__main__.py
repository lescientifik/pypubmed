"""Command-line interface for pypubmed."""
import argparse
import sys

from pypubmed import PubMed, save_json, save_csv


def main():
    parser = argparse.ArgumentParser(
        prog="pypubmed",
        description="Search and fetch articles from PubMed",
    )
    parser.add_argument(
        "--api-key",
        help="NCBI API key for higher rate limits",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search PubMed")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--max", "-m",
        type=int,
        default=10,
        dest="max_results",
        help="Maximum results (default: 10)",
    )
    search_parser.add_argument("--csv", dest="csv_file", help="Save to CSV file")
    search_parser.add_argument("--json", dest="json_file", help="Save to JSON file")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch articles by PMID")
    fetch_parser.add_argument("ids", nargs="+", help="PubMed IDs")
    fetch_parser.add_argument("--csv", dest="csv_file", help="Save to CSV file")
    fetch_parser.add_argument("--json", dest="json_file", help="Save to JSON file")

    args = parser.parse_args()

    # Create client
    pubmed = PubMed(api_key=args.api_key)

    # Execute command
    if args.command == "search":
        articles = pubmed.search_and_fetch(args.query, max_results=args.max_results)
    elif args.command == "fetch":
        articles = pubmed.fetch(args.ids)

    # Output
    if args.csv_file:
        save_csv(articles, args.csv_file)
        print(f"Saved {len(articles)} articles to {args.csv_file}")
    elif args.json_file:
        save_json(articles, args.json_file)
        print(f"Saved {len(articles)} articles to {args.json_file}")
    else:
        # Print summary to stdout
        for article in articles:
            print(f"[{article.pmid}] {article.title[:80]}...")
            if article.authors:
                print(f"  Authors: {', '.join(article.authors[:3])}", end="")
                if len(article.authors) > 3:
                    print(f" et al. ({len(article.authors)} total)")
                else:
                    print()
            print()


if __name__ == "__main__":
    main()
