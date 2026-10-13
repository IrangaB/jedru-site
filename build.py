#!/usr/bin/env python3
"""Build the static Jedru marketing site into dist/ (ready for Cloudflare Pages).
usage: python3 build.py [--portal https://app.jedru.com]"""
import shutil, sys, pathlib
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = pathlib.Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "dist"
PORTAL = sys.argv[sys.argv.index("--portal") + 1] if "--portal" in sys.argv else "https://app.jedru.com"
# Until the customer portal (app.jedru.com) is deployed, trial/sign-in buttons go to the quote form instead of a dead link.
# Flip with `--portal-live` (or set PORTAL_LIVE=1 in the Cloudflare build command) once the VPS is up.
import os
PORTAL_LIVE = "--portal-live" in sys.argv or os.environ.get("PORTAL_LIVE") == "1"
RELATIVE = "--relative" in sys.argv  # relative links (for previews); default absolute "/" for Cloudflare Pages
OUT = pathlib.Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None

PRODUCTS = [
    dict(slug="vortex", url="vortex", nav="vortex", name="Vortex", abbr="V", grad="linear-gradient(135deg,#0ea5a4,#1f6fff)",
         category="Wash-plant chemical & recipe management",
         tagline="Chemical inventory and recipe management for garment wash plants. Dose accurately, track every gram, and keep recipes consistent across shifts.",
         bullets=["Live weighing-scale integration", "Recipe bank with approvals and versions", "Batch tracking from scan to dryer", "Stock, FEFO, MSDS and cost reports"],
         headline="Every gram of chemical, every batch, every machine — accounted for.",
         lede="Vortex runs the chemical side of a garment wash plant: approved recipes, scale-verified dosing, live machine status and the reports auditors and finance ask for.",
         unit="user", unit_label="per user", usd=64, featured=False, short="Wash-plant chemistry and recipes.",
         plan_bullets=["Unlimited recipes, batches and machines", "Weighing-scale and barcode integration", "Approvals workflow and audit trail", "12 report types, PDF and CSV", "Email support"],
         features_title="From recipe bank to dryer, one system",
         features=[("Recipe bank", "Categorised, versioned recipes with sections, steps, chemicals and auto-calculated quantities from weight and liquor ratio. Approval workflow before a recipe can be used."),
                   ("Scale-verified dosing", "Scan the batch, weigh each chemical against its target with ±0.5% tolerance, cross-check the chemical barcode. No more guesswork at the scale."),
                   ("Live floor", "Every washer and dryer with its running batch, queue and timer. Scan the batch sheet at each stage: dye in, dye out, dryer start, finish."),
                   ("Chemical inventory", "Containers, lots, expiry (FEFO), MSDS revision dates, ZDHC level and bluesign status. Low-stock and critical alerts on the dashboard."),
                   ("Reports", "Daily production, consumption by batch, user and shift, stock valuation and compliance. Ask for a report in plain language and Vortex opens it."),
                   ("Roles and approvals", "Seven roles from system admin to data entry; recipe, chemical and mapping changes go through approval with a full audit trail.")],
         who_title="For wash plants that cannot afford a wrong batch",
         who="Garment and denim washing units, laundries serving multiple factories and development labs that need repeatable recipes across shifts and sites.",
         specs=[("Deployment", "Cloud (Jedru-hosted) or self-hosted"), ("Access", "Web, mobile browser, PWA"), ("Scale support", "Serial/USB weighing scales via local bridge"), ("Barcode", "Any USB or Bluetooth scanner"), ("Exports", "PDF, CSV, Excel"), ("Languages", "English")]),
    dict(slug="imonitor", url="imonitor", nav="imonitor", name="iMonitor", abbr="iM", grad="linear-gradient(135deg,#1f6fff,#6d4dff)",
         category="Workforce productivity insight",
         tagline="A lightweight agent on each PC reports working hours and application usage to your dashboard, so you see how time and licences are really spent.",
         bullets=["Hours worked per person, per day", "Application and idle-time tracking", "Live view of who is working, idle or offline", "Shift, user, date and software reports"],
         headline="Know where the working day goes.",
         lede="iMonitor shows how much time each person spends in the applications you care about, live and over any period, with one-click PDF reports. Runs on your LAN with no internet required.",
         unit="PC", unit_label="per monitored PC", usd=37, featured=True, short="Workforce productivity monitoring.",
         plan_bullets=["Unlimited dashboard users", "Hours, apps and idle-time reports", "Live activity view", "Windows agent, central configuration", "Priority support"],
         features_title="Agent on the PC, answers on the dashboard",
         features=[("Utilization dashboard", "Working time per person and per application for any date range, with a colour-coded utilization bar against the shift length."),
                   ("Live activity", "Who is online, working, idle, locked or offline right now, which application is in front, and today's total. Refreshes every few seconds."),
                   ("Central configuration", "Assign shifts and the applications to track from the dashboard; agents pick up changes within a minute. Pause or resume monitoring per person."),
                   ("Any application", "Track any program by its Windows process name: CAD, knitting software, ERP, Office. Give each a colour and it appears in every report."),
                   ("Reports and PDF", "Software, user, date and shift utilization, highest and lowest performers, downloadable as PDF for management."),
                   ("Agent management", "See every PC, agent version and last heartbeat. Silent install with an enrollment key; usage is buffered locally if the server is unreachable.")],
         who_title="For teams paying for expensive software seats",
         who="Design and programming offices, IT managers justifying licence renewals, and operations leaders who want attendance and productivity facts instead of estimates.",
         specs=[("Deployment", "On-premises server (Windows, SQL Server Express) or Jedru-hosted"), ("Agent", "Windows 10/11; macOS planned"), ("Network", "LAN only; outbound HTTP from agents"), ("Privacy", "Application names and active time only; no screenshots or keystrokes"), ("Reports", "PDF"), ("Languages", "English")]),
    dict(slug="craftstudio", url="craft-studio", nav="craft", name="Craft Studio", abbr="CS", grad="linear-gradient(135deg,#e0538a,#6d4dff)",
         category="Knitwear engineering",
         tagline="Knitwear engineering software. Enter garment shape, measurements and density; get the full flat-knit fashioning chart for any machine type.",
         bullets=["All machine gauges and garment shapes", "Grading by cm rules, every size in one click", "Fashioning rules you define", "Craft text ready for the knit room"],
         headline="Measurements and density in. Knitting chart out.",
         lede="Craft Studio turns a measurement sheet and a swatch density into the complete fashioning chart, craft text and graded sizes, in minutes, for any flat-knit machine.",
         unit="user", unit_label="per user", usd=52, featured=False, short="Knitwear engineering and charts.",
         plan_bullets=["All machine types and garment shapes", "Grading by cm rules", "Craft text export", "Production header and materials", "Email support"],
         features_title="The knit technician's calculator, done properly",
         features=[("Panel drawing", "Front, back, sleeve and pants panels drawn from your meters with dimension lines and fashioning notes. Change a measurement and the panel redraws."),
                   ("Density per panel", "Needles/cm and rows/cm per panel from your swatch; every meter converts to needles and rows instantly."),
                   ("Craft text", "Quick-to-slow or slow-to-quick fashioning with configurable segments, needles per step, bind-offs and hem rows. One click to copy for the machine programmer."),
                   ("Pattern grading", "A cm rule per meter per size; generate all sizes and get cast-on, widest, armhole, neck and top needle counts in a table."),
                   ("Production header", "Customer, style, gauge, linking, yarn and materials on every chart, saved per order."),
                   ("Licensing", "Trial, then per-user subscription; licence key with expiry notice; EULA on first use.")],
         who_title="For knitwear factories and sample rooms",
         who="Flat-knit manufacturers, sample rooms and technical designers who build fashioning charts by hand today and need them faster, consistent and graded.",
         specs=[("Deployment", "Jedru-hosted or installed on your server"), ("Machines", "All flat-knit gauges; chart notation rows-needles-times"), ("Units", "cm; grading by cm steps"), ("Export", "Craft text, chart tables"), ("Languages", "English")]),
]

# ---- Pricing tiers (USD). annual = monthly*12 minus discount; "save" shown on the page.
def tier(name, monthly, annual, blurb, features, recommended=False):
    return dict(name=name, monthly=monthly, annual=annual, save=monthly * 12 - annual, pct=round((monthly * 12 - annual) / (monthly * 12) * 100), blurb=blurb, features=features, recommended=recommended)

TIERS = {
    "vortex": [
        tier("Entry", 64, 760, "Run one wash plant with scale-verified dosing.", ["1 site, up to 5 dye/wash machines", "Recipe bank, batches and live floor", "Weighing-scale and barcode integration", "Standard reports (PDF, CSV)", "30-day chemical issue history", "Email support"]),
        tier("Mid-market", 96, 1037, "Everything a growing plant needs, audit-ready.", ["Unlimited machines and sites", "Approvals workflow with full audit trail", "FEFO, MSDS-expiry and low-stock alerts", "AI report assistant and scheduled reports", "API access for ERP integration", "Priority support (same business day)"], recommended=True),
        tier("Premium", 149, 1609, "For groups that need control, SLA and ownership.", ["Everything in Mid-market", "SSO with Microsoft Entra ID", "Self-hosted option on your own servers", "99.9% uptime SLA", "Dedicated success manager, onboarding and training", "Custom reports and integrations"]),
    ],
    "imonitor": [
        tier("Entry", 37, 400, "See hours and application use on every PC.", ["Working time per person and application", "Live activity view", "30-day history", "PDF reports", "Windows agent, central configuration", "Email support"]),
        tier("Mid-market", 55, 594, "Management-grade reporting across shifts and teams.", ["12-month history", "Shift, department and date reports", "Scheduled email reports to managers", "Agent auto-update and alerts for offline PCs", "API access (HR / payroll)", "Priority support (same business day)"], recommended=True),
        tier("Premium", 85, 918, "Enterprise control for multi-site groups.", ["Everything in Mid-market", "Unlimited history", "Self-hosted server inside your network", "SSO with Microsoft Entra ID", "99.9% uptime SLA", "Dedicated success manager and custom integrations"]),
    ],
    "craftstudio": [
        tier("Entry", 52, 562, "The fashioning calculator for one technician.", ["Panel drawing from measurements", "Density per panel, craft text, grading", "All flat-knit machine types", "Standard garment shapes", "Copy / export craft text", "Email support"]),
        tier("Mid-market", 79, 853, "A shared style library for the whole sample room.", ["Custom shapes and meters", "Team style library with versions and approvals", "PDF charts with production header", "Grading rule sets you define and reuse", "API / machine-program export hooks", "Priority support (same business day)"], recommended=True),
        tier("Premium", 125, 1350, "For factories standardising engineering across sites.", ["Everything in Mid-market", "Self-hosted option", "SSO with Microsoft Entra ID", "Custom fashioning rule packs built with you", "99.9% uptime SLA", "Dedicated success manager, onboarding and training"]),
    ],
}

PAGES = [
    ("index.html", "index.html", dict(title="Precision software for manufacturers", description="Jedru builds Vortex, iMonitor and Craft Studio: wash-plant chemical management, workforce productivity insight and knitwear engineering. Free 14-day trials.", nav="", path="/")),
    ("quote/index.html", "quote.html", dict(title="Pricing tailored to you", description="Get a tailored quote for Vortex, iMonitor or Craft Studio. Tell us about your factory and a Jedru solutions specialist designs a plan around your budget within one business day.", nav="quote", path="/quote/")),
    ("security/index.html", "security.html", dict(title="Security", description="How Jedru protects accounts, data and software: SSO, one session per user, trusted devices, signed entitlements, PayHere payments.", nav="security", path="/security/")),
    ("company/index.html", "company.html", dict(title="Company", description="About Jedru, a manufacturing software company in Sri Lanka. Contact sales and support.", nav="company", path="/company/")),
    ("privacy/index.html", "legal.html", dict(title="Privacy policy", description="Jedru privacy policy.", nav="", path="/privacy/", kind="privacy", updated="11 October 2026")),
    ("terms/index.html", "legal.html", dict(title="Terms of service", description="Jedru terms of service, EULA and refund policy.", nav="", path="/terms/", kind="terms", updated="11 October 2026")),
]
for p in PRODUCTS:
    PAGES.append((f"{p['url']}/index.html", "product.html", dict(title=p["name"], description=p["tagline"], nav=p["nav"], path=f"/{p['url']}/", p=p)))

def asset_version():
    """Short hash of css+js so browsers fetch new versions immediately (links carry ?v=...)."""
    import hashlib
    h = hashlib.sha1()
    for f in ("static/css/site.css", "static/js/site.js"):
        h.update((SRC / f).read_bytes())
    return h.hexdigest()[:8]


def main():
    global DIST
    if OUT: DIST = OUT
    if DIST.exists(): shutil.rmtree(DIST)
    shutil.copytree(SRC / "static", DIST)
    shutil.copytree(SRC.parent / "functions", DIST / "functions")  # Pages Functions live at the repo root (functions/); copied for wrangler/dashboard too
    env = Environment(loader=FileSystemLoader(SRC / "templates"), autoescape=select_autoescape(["html"]))
    for out, tpl, ctx in PAGES:
        depth = out.count("/")
        base = ("../" * depth if depth else "./") if RELATIVE else "/"
        signup = (lambda slug="": f"{PORTAL}/accounts/signup/" + (f"?product={slug}" if slug else "")) if PORTAL_LIVE else \
                 (lambda slug="": f"{base}quote/?trial=1" + (f"&product={slug}" if slug else "") + "#quote-form")
        html = env.get_template(tpl).render(portal=PORTAL, portal_live=PORTAL_LIVE, signup=signup, products=PRODUCTS, tiers=TIERS, base=base, v=asset_version(), **ctx)
        f = DIST / out; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(html)
    (DIST / "_redirects").write_text("/pricing/ /quote/ 301\n/pricing /quote/ 301\n")  # prices hidden for now; pricing.html + TIERS kept for later
    (DIST / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n  Referrer-Policy: strict-origin-when-cross-origin\n/media/*\n  Cache-Control: public, max-age=31536000, immutable\n/css/*\n  Cache-Control: public, max-age=86400, must-revalidate\n/js/*\n  Cache-Control: public, max-age=86400, must-revalidate\n")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://jedru.com/sitemap.xml\n")
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>https://jedru.com{c['path']}</loc></url>" for _, _, c in PAGES) + "</urlset>\n")
    print("built", len(PAGES), "pages into", DIST)

if __name__ == "__main__":
    main()
