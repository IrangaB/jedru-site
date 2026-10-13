/**
 * Cloudflare Pages Function: POST /api/contact
 * Sends the contact form to support@jedru.com via Resend (https://resend.com).
 * Environment variables (Pages project → Settings → Variables and Secrets):
 *   RESEND_API_KEY   (secret)  — from resend.com → API Keys
 *   CONTACT_TO       (text)    — default support@jedru.com
 *   CONTACT_FROM     (text)    — default "Jedru Website <website@jedru.com>" (domain must be verified in Resend)
 */
const RATE = new Map(); // in-isolate rate limit: ip -> [timestamps]

export async function onRequestPost({ request, env }) {
  const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
  let data;
  try { data = await request.json(); } catch { return json({ ok: false, error: "Bad request" }, 400); }

  // honeypot: real users never fill "website"
  if (data.website) return json({ ok: true });

  const clean = (v, max) => String(v ?? "").trim().slice(0, max);
  const name = clean(data.name, 120), company = clean(data.company, 160), email = clean(data.email, 200), message = clean(data.message, 4000);
  const product = clean(data.product || data.products, 160), phone = clean(data.phone, 40), size = clean(data.size, 60), budget = clean(data.budget, 60), kind = clean(data.kind, 40) || "Enquiry";
  if (!name || !email || !message) return json({ ok: false, error: "Name, email and message are required." }, 422);
  if (name.length < 2 || !/^[\p{L} .'\-]+$/u.test(name)) return json({ ok: false, error: "Please enter your name (letters only)." }, 422);
  if (!/^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/.test(email)) return json({ ok: false, error: "That email address doesn't look right." }, 422);
  if (phone) { const d = (phone.match(/\d/g) || []).length; if (!/^\+?[0-9 ()\-]{7,20}$/.test(phone) || d < 7 || d > 15) return json({ ok: false, error: "Phone: digits only, 7 to 15 digits (e.g. +94 77 123 4567)." }, 422); }
  if (message.length < 10) return json({ ok: false, error: "Please tell us a little more (at least 10 characters)." }, 422);
  if ((kind === "Quote request" || kind === "Free trial request") && !product) return json({ ok: false, error: "Please tick at least one product." }, 422);

  // rate limit: 5 per 10 minutes per IP (best-effort, per edge isolate)
  const ip = request.headers.get("cf-connecting-ip") || "0";
  const now = Date.now(); const hits = (RATE.get(ip) || []).filter(t => now - t < 600000);
  if (hits.length >= 5) return json({ ok: false, error: "Too many messages. Please try again later." }, 429);
  hits.push(now); RATE.set(ip, hits);

  if (!env.RESEND_API_KEY) return json({ ok: false, error: "Email is not configured yet. Please write to support@jedru.com." }, 503);
  const to = env.CONTACT_TO || "support@jedru.com";
  const from = env.CONTACT_FROM || "Jedru Website <website@jedru.com>";
  const country = request.headers.get("cf-ipcountry") || "";
  const esc = s => s.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const html = `<div style="font-family:Segoe UI,Arial,sans-serif;font-size:15px;color:#0b1a33">
    <h2 style="margin:0 0 12px">${esc(kind)} from jedru.com</h2>
    <table cellpadding="6" style="border-collapse:collapse">
      <tr><td><b>Name</b></td><td>${esc(name)}</td></tr>
      <tr><td><b>Company</b></td><td>${esc(company) || "—"}</td></tr>
      <tr><td><b>Email</b></td><td><a href="mailto:${esc(email)}">${esc(email)}</a></td></tr>
      <tr><td><b>Phone / WhatsApp</b></td><td>${esc(phone) || "—"}</td></tr>
      <tr><td><b>Product(s)</b></td><td>${esc(product) || "—"}</td></tr>
      <tr><td><b>Team size</b></td><td>${esc(size) || "—"}</td></tr>
      <tr><td><b>Budget</b></td><td>${esc(budget) || "—"}</td></tr>
      <tr><td><b>Country / IP</b></td><td>${esc(country)} · ${esc(ip)}</td></tr>
      <tr><td><b>Received</b></td><td>${new Date().toISOString()}</td></tr>
    </table>
    <h3 style="margin:16px 0 6px">Message</h3>
    <pre style="white-space:pre-wrap;font:inherit;background:#f4f6fb;padding:12px;border-radius:8px">${esc(message)}</pre></div>`;
  const text = `${kind} from jedru.com\n\nName: ${name}\nCompany: ${company}\nEmail: ${email}\nPhone: ${phone}\nProduct(s): ${product}\nTeam size: ${size}\nBudget: ${budget}\nCountry/IP: ${country} ${ip}\n\n${message}`;

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ from, to: [to], reply_to: email, subject: `[Jedru] ${kind}${product ? ": " + product : ""} — ${name}${company ? " · " + company : ""}`, html, text }),
  });
  if (!r.ok) { const err = await r.text().catch(() => ""); console.log("resend error", r.status, err); return json({ ok: false, error: "Could not send right now. Please email support@jedru.com." }, 502); }
  return json({ ok: true });
}

// Diagnostics: open https://jedru.com/api/contact in a browser. Shows whether the key is visible (never the key itself).
export async function onRequestGet({ env }) {
  const key = env.RESEND_API_KEY || "";
  return new Response(JSON.stringify({ ok: true, function: "contact", configured: key.length > 0, key_prefix: key ? key.slice(0, 3) + "…" : null,
    to: env.CONTACT_TO || "support@jedru.com", from: env.CONTACT_FROM || "Jedru Website <website@jedru.com>", env_keys: Object.keys(env).filter(k => k !== "ASSETS") }),
    { headers: { "content-type": "application/json" } });
}
