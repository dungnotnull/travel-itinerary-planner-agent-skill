#!/usr/bin/env python3
"""knowledge_updater.py — Personalized Travel Itinerary Planner (Idea 66)

Crawl tourism/advisory/travel sources, score by recency + relevance, append
deduplicated entries to SECOND-KNOWLEDGE-BRAIN.md. Prices are flagged volatile.

Production features:
- Retry logic with exponential backoff
- Comprehensive logging
- Rate limiting
- Graceful degradation
- Data validation

Run: python knowledge_updater.py [--dry-run] [--verbose] [--source=SOURCE]
Schedule: weekly cron (0 2 * * 0)
Dependencies: crawl4ai (optional; degrades gracefully), requests, beautifulsoup4
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import pathlib
import re
import sys
import time
from typing import Any, Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_updater.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BRAIN = pathlib.Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # Initial delay in seconds
RATE_LIMIT_DELAY = 2.0  # Seconds between requests
TIMEOUT = 30  # Request timeout in seconds

# Data sources with fallback fetch strategies
SOURCES = [
    {
        "name": "UNWTO",
        "url": "https://www.unwto.org/news",
        "category": "research",
        "volatility": "LOW"
    },
    {
        "name": "US Travel Advisories",
        "url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html",
        "category": "advisory",
        "volatility": "HIGH"
    },
    {
        "name": "UK FCDO Travel Advice",
        "url": "https://www.gov.uk/foreign-travel-advice",
        "category": "advisory",
        "volatility": "HIGH"
    },
    {
        "name": "Lonely Planet News",
        "url": "https://www.lonelyplanet.com/news",
        "category": "guide",
        "volatility": "MEDIUM"
    },
    {
        "name": "Travel + Leisure",
        "url": "https://www.travelandleisure.com/latest-news",
        "category": "guide",
        "volatility": "MEDIUM"
    }
]

QUERIES = [
    "travel advisory 2026",
    "tourist attraction prices",
    "travel trends destination",
    "seasonal travel",
    "transit updates",
    "visa requirements 2026"
]

KEYWORDS = [
    "travel", "tourism", "destination", "itinerary", "flight",
    "advisory", "attraction", "season", "transit", "budget", "visa",
    "hotel", "accommodation", "transport", "airport", "airline"
]


class RateLimiter:
    """Simple rate limiter to prevent overwhelming servers."""

    def __init__(self, delay: float = RATE_LIMIT_DELAY):
        self.delay = delay
        self.last_call = 0.0

    def wait(self) -> None:
        """Wait if necessary to maintain rate limit."""
        now = time.time()
        time_since_last = now - self.last_call

        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_call = time.time()


rate_limiter = RateLimiter()


def retry_with_backoff(func, max_retries: int = MAX_RETRIES, initial_delay: float = RETRY_DELAY):
    """Decorator for retry with exponential backoff."""

    def wrapper(*args, **kwargs):
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")

                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All {max_retries} attempts failed")

        raise last_exception

    return wrapper


@retry_with_backoff
def fetch_with_crawl4ai(source: dict) -> list[dict]:
    """Fetch using crawl4ai if available."""
    try:
        from crawl4ai import WebCrawler

        logger.info(f"Fetching {source['name']} with crawl4ai")
        crawler = WebCrawler()
        crawler.warmup()

        result = crawler.run(url=source["url"])
        if not result:
            logger.warning(f"crawl4ai returned no result for {source['name']}")
            return []

        text = getattr(result, "markdown", "") or getattr(result, "html", "")
        return parse_content(text, source)

    except ImportError:
        logger.warning("crawl4ai not installed, will use fallback")
        raise ImportError("crawl4ai not available")
    except Exception as e:
        logger.error(f"crawl4ai fetch failed for {source['name']}: {e}")
        raise


@retry_with_backoff
def fetch_with_requests(source: dict) -> list[dict]:
    """Fallback fetch using requests + beautifulsoup4."""
    try:
        import requests
        from bs4 import BeautifulSoup

        logger.info(f"Fetching {source['name']} with requests (fallback)")
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; TravelItineraryPlanner/1.0; +https://github.com/travel-planner)'
        }

        response = requests.get(
            source["url"],
            headers=headers,
            timeout=TIMEOUT
        )
        response.raise_for_status()

        # Extract text content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator='\n', strip=True)
        return parse_content(text, source)

    except Exception as e:
        logger.error(f"requests fetch failed for {source['name']}: {e}")
        raise


def parse_content(text: str, source: dict) -> list[dict]:
    """Parse raw content into structured entries."""
    entries = []
    source_name = source["name"]
    source_url = source["url"]

    for line in text.splitlines():
        line = line.strip("#*•-").strip()

        # Basic validation
        if not (20 < len(line) < 300):
            continue

        if not any(k.lower() in line.lower() for k in KEYWORDS):
            continue

        # Extract potential title
        title = line
        if len(title) > 150:
            title = title[:147] + "..."

        entries.append({
            "title": title,
            "source": source_name,
            "url": source_url,
            "category": source.get("category", "general"),
            "volatility": source.get("volatility", "MEDIUM"),
            "length": len(line)
        })

    logger.debug(f"Parsed {len(entries)} entries from {source_name}")
    return entries


def fetch(source: dict) -> list[dict]:
    """Fetch content from source with fallback strategies."""
    rate_limiter.wait()

    # Try crawl4ai first (better markdown extraction)
    try:
        return fetch_with_crawl4ai(source)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"crawl4ai failed, falling back to requests: {e}")

    # Fallback to requests + beautifulsoup4
    return fetch_with_requests(source)


def score(entry: dict) -> float:
    """Score entry by relevance to travel planning."""
    score = 0.0
    title_lower = entry["title"].lower()

    # Keyword matches
    for keyword in KEYWORDS:
        if keyword in title_lower:
            score += 1.0

    # Category bonus
    if entry.get("category") == "advisory":
        score += 2.0  # Advisories are high value
    elif entry.get("category") == "research":
        score += 1.5  # Research is valuable

    # Volatility penalty (volatile content is less valuable long-term)
    volatility = entry.get("volatility", "MEDIUM")
    if volatility == "HIGH":
        score *= 0.7
    elif volatility == "LOW":
        score *= 1.2

    # Length normalization (prefer moderate length)
    length = entry.get("length", 0)
    if 50 <= length <= 150:
        score *= 1.2

    return score


def validate_entry(entry: dict) -> bool:
    """Validate entry has required fields and reasonable values."""
    required_fields = ["title", "source", "url"]

    # Check required fields
    if not all(field in entry for field in required_fields):
        logger.warning(f"Entry missing required fields: {entry.get('title', 'Unknown')}")
        return False

    # Validate title
    title = entry.get("title", "")
    if len(title) < 10 or len(title) > 300:
        logger.debug(f"Entry title invalid length: {len(title)}")
        return False

    # Validate URL
    try:
        result = urlparse(entry["url"])
        if not all([result.scheme, result.netloc]):
            logger.warning(f"Entry has invalid URL: {entry['title']}")
            return False
    except Exception as e:
        logger.warning(f"Entry URL parse failed: {e}")
        return False

    return True


def existing_hashes(text: str) -> set[str]:
    """Extract existing entry hashes from brain file."""
    hashes = set(re.findall(r"<!--h:([0-9a-f]{12})-->", text))
    logger.debug(f"Found {len(hashes)} existing hashes")
    return hashes


def entry_hash(entry: dict) -> str:
    """Generate stable hash for entry deduplication."""
    hash_input = f"{entry['url']}|{entry['title']}"
    return hashlib.sha1(hash_input.encode('utf-8')).hexdigest()[:12]


def format_entry(entry: dict, date: str) -> str:
    """Format entry for markdown output."""
    volatility = entry.get("volatility", "MEDIUM")
    h = entry_hash(entry)

    return f"- [{date}] {entry['title']} — {entry['source']} — {entry['url']} — Volatility:{volatility} <!--h:{h}-->"


def write_entry_block(fh, entries: list[dict], date: str) -> int:
    """Write entries to file in markdown block format."""
    if not entries:
        return 0

    fh.write(f"\n### Auto-update {date}\n")

    count = 0
    for entry in entries:
        if validate_entry(entry):
            fh.write(format_entry(entry, date) + "\n")
            count += 1
        else:
            logger.debug(f"Skipped invalid entry: {entry.get('title', 'Unknown')}")

    fh.write("\n")
    return count


def load_existing_entries(brain_path: pathlib.Path) -> str:
    """Load existing brain file content."""
    if brain_path.exists():
        content = brain_path.read_text(encoding="utf-8")
        logger.info(f"Loaded existing brain file: {len(content)} characters")
        return content
    else:
        logger.warning(f"Brain file not found, will create: {brain_path}")
        return ""


def main() -> None:
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Update travel knowledge base from authoritative sources"
    )
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without writing to file")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--source", type=str,
                       help="Fetch from specific source only")
    parser.add_argument("--output", type=str,
                       help=f"Output file (default: {BRAIN})")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    output_path = pathlib.Path(args.output) if args.output else BRAIN
    logger.info(f"Starting knowledge update, output: {output_path}")

    # Filter sources if specified
    sources_to_fetch = SOURCES
    if args.source:
        sources_to_fetch = [s for s in SOURCES if s["name"] == args.source]
        if not sources_to_fetch:
            logger.error(f"Source '{args.source}' not found")
            logger.info(f"Available sources: {', '.join(s['name'] for s in SOURCES)}")
            sys.exit(1)

    # Load existing content
    brain_content = load_existing_entries(output_path)
    seen_hashes = existing_hashes(brain_content)

    # Collect entries from all sources
    all_entries = []
    successful_sources = 0
    failed_sources = 0

    for source in sources_to_fetch:
        logger.info(f"Fetching from {source['name']}...")

        try:
            entries = fetch(source)
            logger.info(f"Fetched {len(entries)} raw entries from {source['name']}")
            all_entries.extend(entries)
            successful_sources += 1
        except Exception as e:
            logger.error(f"Failed to fetch {source['name']}: {e}")
            failed_sources += 1
            continue

    # Score and sort entries
    logger.info(f"Scoring {len(all_entries)} entries...")
    for entry in all_entries:
        entry["score"] = score(entry)

    all_entries.sort(key=lambda e: e["score"], reverse=True)
    logger.info(f"Top entry score: {all_entries[0]['score'] if all_entries else 0:.2f}")

    # Deduplicate and prepare new entries
    today = dt.date.today().isoformat()
    new_entries = []

    for entry in all_entries:
        h = entry_hash(entry)
        if h not in seen_hashes:
            seen_hashes.add(h)  # Prevent duplicates within this batch
            new_entries.append(entry)

    logger.info(f"After deduplication: {len(new_entries)} new entries")

    if not new_entries:
        logger.info("No new entries to add")
        return

    # Generate output
    block = f"\n### Auto-update {today}\n"
    block += "\n".join(format_entry(e, today) for e in new_entries if validate_entry(e))
    block += "\n"

    if args.dry_run:
        logger.info("DRY RUN — would write:")
        print(block)
        logger.info(f"Total new entries: {len(new_entries)}")
        logger.info(f"Successful sources: {successful_sources}/{len(sources_to_fetch)}")
        if failed_sources > 0:
            logger.warning(f"Failed sources: {failed_sources}/{len(sources_to_fetch)}")
        return

    # Write to file
    try:
        with output_path.open("a", encoding="utf-8") as fh:
            count = write_entry_block(fh, new_entries, today)

        logger.info(f"Wrote {count} entries to {output_path}")
        logger.info(f"Successful sources: {successful_sources}/{len(sources_to_fetch)}")
        if failed_sources > 0:
            logger.warning(f"Failed sources: {failed_sources}/{len(sources_to_fetch)}")

    except Exception as e:
        logger.error(f"Failed to write to {output_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
