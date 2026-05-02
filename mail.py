import json
import imaplib
import email
import os
from dotenv import load_dotenv
import re
import argparse

load_dotenv()

username = os.environ["GMAIL_USER"]
app_password = os.environ["APP_PASSWORD"]

AMOUNT_RE = re.compile(
    r"Rs\.?\s*([\dX,]+(?:\.\d{2})?)",
    re.IGNORECASE
)

CREDIT_RE = re.compile(
    r"\bcredited.*?VPA\s+[^\s]+\s+(.+?)\s+on\s+(\d{2}-\d{2}-\d{2})",
    re.IGNORECASE
)

DEBIT_RE = re.compile(
    r"\bdebited.*?to\s+[^\s]+\s+(.+?)\s+on\s+(\d{2}-\d{2}-\d{2})",
    re.IGNORECASE
)

UTR_RE = re.compile(
    r"\bUPI transaction reference number is\s+([A-Za-z0-9]+)",
    re.IGNORECASE
)


def extract_html_bodies(msg):
    bodies = []

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                charset = part.get_content_charset() or "utf-8"
                bodies.append(
                    part.get_payload(decode=True).decode(charset, errors="replace")
                )
    else:
        if msg.get_content_type() == "text/html":
            charset = msg.get_content_charset() or "utf-8"
            bodies.append(
                msg.get_payload(decode=True).decode(charset, errors="replace")
            )

    return bodies


def fetch_transactions(username, app_password, limit, want_credit, want_debit):
    results = []

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, app_password)
    imap.select("inbox")

    search_queries = []

    if want_credit:
        search_queries.append(
            '(SUBJECT "Account update for your HDFC Bank A/c")'
        )

    if want_debit:
        search_queries.append(
            '(SUBJECT "You have done a UPI txn. Check details!")'
        )

    for query in search_queries:
        status, messages = imap.search(None, query)
        if status != "OK":
            continue

        email_ids = messages[0].split()[-limit:]
        print(f"[DEBUG] Fetching {len(email_ids)} emails (requested: {limit})", file=os.sys.stderr)

        for eid in reversed(email_ids):
            status, msg_data = imap.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            for part in msg_data:
                if not isinstance(part, tuple):
                    continue

                msg = email.message_from_bytes(part[1])
                bodies = extract_html_bodies(msg)

                for body in bodies:
                    amount = AMOUNT_RE.search(body)
                    utr = UTR_RE.search(body)

                    if want_credit:
                        m = CREDIT_RE.search(body)
                        if m and amount:
                            results.append({
                                "type": "credit",
                                "name": m.group(1).strip(),
                                "amount": amount.group(1).replace(",", ""),
                                "date": m.group(2),
                                "utr": utr.group(1) if utr else None
                            })

                    if want_debit:
                        m = DEBIT_RE.search(body)
                        if m and amount:
                            results.append({
                                "type": "debit",
                                "name": m.group(1).strip(),
                                "amount": amount.group(1).replace(",", ""),
                                "date": m.group(2),
                                "utr": utr.group(1) if utr else None
                            })

    imap.logout()
    print(f"[DEBUG] Found {len(results)} valid transactions from {limit} emails requested", file=os.sys.stderr)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract HDFC UPI credit/debit transactions from Gmail"
    )

    parser.add_argument(
        "--noe",
        type=int,
        default=50,
        help="Number of emails per category (default: 50)"
    )

    parser.add_argument("--credit", action="store_true")
    parser.add_argument("--debit", action="store_true")

    args = parser.parse_args()

    if not args.credit and not args.debit:
        parser.error("Specify at least one of --credit or --debit")

    data = fetch_transactions(
        username=username,
        app_password=app_password,
        limit=args.noe,
        want_credit=args.credit,
        want_debit=args.debit
    )

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
