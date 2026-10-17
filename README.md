# Spider Trap

A Flask-based honeypot that identifies automated scanners and bots, then redirects them into an auto-generated maze of fake pages rather than serving a standard error response.

## Overview

Most bot-detection approaches stop at identification: flag the traffic, block the IP, move on. This project takes a different approach by keeping flagged clients engaged with the system in a way that costs them time and crawl budget, while leaving legitimate visitors unaffected.

The site presents a small set of normal pages (home, about, contact, facts). Each page contains a hidden link to `/admin` that is invisible to a human visitor but discoverable by any crawler or scanner parsing the raw HTML. A request to that path, or to any URL containing a keyword associated with common scanning behavior (`admin`, `login`, `backup`, `config`, `.env`, etc.), flags the originating client.

Once flagged, requests to unrecognized paths no longer return a standard 404. Instead, the client receives a page populated with a randomized set of links, each pointing to further generated pages that extend the maze indefinitely. These pages link only to one another, so a client that enters the maze has no path back to legitimate content through the links it's served.

All requests, flagged and unflagged, are logged to `requests.jsonl` with timestamp, IP, path, method, user agent, and the action taken, providing a record of trap activity for review.

## Motivation

This project builds on an earlier one, a login anomaly detector that flagged suspicious authentication patterns from log data. That project was retrospective, analyzing logs after the fact. This one is active: it intercepts and responds to suspicious behavior in real time. Together they reflect two complementary approaches to the same underlying problem, recognizing automated and malicious traffic from behavioral patterns.

## Setup

pip install -r requirements.txt
python spider_trap.py


The app runs locally at `http://127.0.0.1:5000`. To observe the trap, visit `/admin`, then request any unrecognized path; subsequent responses will be maze pages rather than 404s.

## Detection logic

- **Keyword-based flagging** — paths containing terms commonly associated with scanning and reconnaissance (`admin`, `login`, `.env`, etc.) trigger an immediate flag.
- **Rate-based flagging** — requests from a single IP arriving faster than approximately 0.3 seconds apart are flagged as inconsistent with normal browsing behavior.
- Flags are maintained per IP in memory for the lifetime of the server process and are not persisted across restarts.

## Design limitations

This is a demonstration project and reflects deliberate scope decisions rather than oversights:

- **Detection is IP-based.** A client operating behind a rotating proxy or VPN would not remain flagged, since detection and flagging apply per address.
- **The trap applies to unrecognized paths only.** A flagged client that already knows the URL of a legitimate page can still request it directly; the maze intercepts unknown paths, not known ones. The maze's internal link structure is self-contained, so clients cannot reach legitimate pages by following generated links.
- **In-memory tracking is unbounded.** IP and request data are held in memory without eviction, which is appropriate for a local demonstration but would require a bounded cache or expiration policy for sustained or production use.

## Stack

Python and Flask. No database or external services; all state is held in memory for the duration of the process.
