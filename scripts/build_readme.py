"""Rebuild README.md from the live Block4Roots tools list (approved tools with a free plan).

Reads the public, read-only tools table the website itself uses (publishable key, row-level security).
Run: SUPABASE_URL=... SUPABASE_KEY=... python3 scripts/build_readme.py
"""
import json, os, urllib.request
from datetime import datetime, timezone, timedelta

URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_KEY", "")
SITE = "https://block4roots.com"
FIELDS = "id,name,category,what_it_does,free_limits,price_note,price_from_inr,price_from_usd,works_in_hindi,platforms,price_checked_at"

CATS = [
    ("chat", "Ask AI and chat"), ("write", "Write and edit"), ("research", "Research and summarise"),
    ("learn", "Learn and exam prep"), ("image", "Make images"), ("video", "Make and edit video"),
    ("audio", "Voice and music"), ("design", "Design and slides"), ("marketing", "Grow on social"),
    ("productivity", "Notes and productivity"), ("automation", "Automate work"), ("code", "Code"),
]


def fetch():
    if os.environ.get("TOOLS_JSON"):
        with open(os.environ["TOOLS_JSON"], encoding="utf-8") as f:
            return json.load(f)
    q = f"{URL}/rest/v1/tools?select={FIELDS}&approved=eq.true&free_plan=eq.true&order=name"
    req = urllib.request.Request(q, headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def cell(s, n=140):
    s = " ".join(str(s or "").split()).replace("|", "/")
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def price(t):
    if t.get("price_from_inr"):
        return f"from ₹{int(float(t['price_from_inr'])):,}"
    if t.get("price_from_usd"):
        return f"from ${float(t['price_from_usd']):g}"
    return "free / see site"


def main():
    tools = fetch()
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%d %b %Y")
    out = [
        "# Free AI tools for Indians (2026)",
        "",
        f"A hand-checked list of **{len(tools)} AI tools with a real free plan**, with free limits and paid prices "
        "in ₹ where the maker shows them. Every free plan and price is checked on the tool's own site.",
        "",
        f"Updated automatically every day from [Block4Roots]({SITE}), a beginner-first AI tool finder. "
        f"Last update: **{today}**.",
        "",
        f"- Not sure which one to pick? Tell [Block4Roots]({SITE}) the job (\"make a thumbnail\", \"summarise my notes\") "
        "and get the top 3 tools for it.",
        f"- Hindi users: see [AI tools in Hindi]({SITE}/ai-tools-in-hindi).",
        f"- Prices in ₹ for paid plans: [AI prices]({SITE}/ai-prices).",
        "",
        "Legend: 🇮🇳 = works in Hindi. Prices change often, so always confirm on the tool's site before paying.",
        "",
        "## Contents",
        "",
    ]
    by_cat = {c: [t for t in tools if t.get("category") == c] for c, _ in CATS}
    out += [f"- [{label}](#{label.lower().replace(' ', '-')}) ({len(by_cat[c])})" for c, label in CATS if by_cat[c]]
    for c, label in CATS:
        rows = by_cat[c]
        if not rows:
            continue
        out += ["", f"## {label}", "", f"Top 3 picks for this job: [{SITE}/best-ai-tools/{c}]({SITE}/best-ai-tools/{c})", "",
                "| Tool | What it does | Free plan | Paid |", "|---|---|---|---|"]
        for t in rows:
            hi = " 🇮🇳" if t.get("works_in_hindi") else ""
            out.append(f"| [{cell(t['name'], 40)}]({SITE}/tools/{t['id']}){hi} | {cell(t.get('what_it_does'))} | "
                       f"{cell(t.get('free_limits') or 'Yes', 120)} | {price(t)} |")
    out += ["", "## How this list is made", "",
            "Tools are added by the Block4Roots team after a quality check (real users, a free plan read on the tool's own "
            "pricing page, beginner-friendly, works in India). Prices are re-checked on a rolling basis. "
            f"Spotted something wrong? Email block@block4roots.com or open an issue.", "",
            f"Maintained by [Block4Roots]({SITE}) · [X](https://x.com/Block4Roots)", ""]
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"README.md written: {len(tools)} tools")


if __name__ == "__main__":
    main()
