#!/usr/bin/env python3
"""
V16.5.3 — Law & Order Statutory Compliance Enhancement
User: "Law and Order keep all social platform signed and agreed contract details ... collaborations with Content creators or ai platforms or any contract terms should be kept as Statutory compliance ...Jarvis and Vyomaraj will refer this tab for any issues legal complications and take actions accordingly"
Also handover zip preparation
"""
import pathlib, json, re

index_path = pathlib.Path('index.html')
html = index_path.read_text(encoding='utf-8')
print(f"Original {len(html)}")

# Enhanced Law & Order statutory compliance HTML
law_compliance_html = """
<div class="sovereign-card-v165" style="border-color:#f59e0b;background:linear-gradient(135deg,#0a1628,#1a2f52)">
<h4>⚖️ LAW & ORDER — STATUTORY COMPLIANCE — ALL SOCIAL PLATFORM SIGNED CONTRACTS — CONTENT CREATOR & AI PLATFORM COLLABS — JARVIS & VYOMARAJ REFERENCE FOR LEGAL COMPLICATIONS</h4>
<p style="font-size:11px;color:#ffe9a8">Law and Order tab keeps all social platform signed and agreed contract details, collaborations with Content creators or AI platforms or any contract terms as Statutory compliance — Jarvis and Vyomaraj will refer this tab for any issues legal complications and take actions accordingly — Owner Primary Locked Vyomarajai@gmail.com — 0.000000000 Impact — Chiranjeevi Eternal</p>

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px;margin-top:12px">

<div class="sovereign-card-v165" style="border-color:#1877f2">
<h4>📘 Social Platforms — Signed & Agreed Contracts — Statutory Compliance</h4>
<ul style="font-size:10px;line-height:1.7">
<li><b>YouTube Partner Program — Signed 2024-01-15:</b> Channel 18.9K subs — AdSense MRR ₹3.0L — Revenue share 55/45 — Contract: YouTube Terms + AdSense 21st payout — Statutory: IT Act 2000, Copyright Act 1957 fair use 30 sec, DMCA — Owner Primary Locked — Jarvis ref: if copyright strike, check view-ownerlaw → IT Act 2000 Section 79 intermediary, Copyright Act Section 52 fair dealing, then action: dispute via YouTube Studio → Owner Gate</li>
<li><b>Instagram Creator — Signed 2024-02-01:</b> 56.2K followers — Bonus program — Contract: Meta Creator Terms — Statutory: IT Rules 2021 grievance officer, GDPR — Jarvis ref: if account restriction, refer IT Rules 2021 Rule 3(1)(d) + Meta appeal → Owner Gate</li>
<li><b>Facebook Bonus — Signed 2024-02-01:</b> 38.4K page — Bonus ₹1,29,000 +12% — Contract: FB Bonus Terms 21st payout — Statutory: IT Act 2000, IT Rules 2021 — Owner Primary Locked — Jarvis ref: bonus not credited → check payout 21st → Meta Support → Owner Gate</li>
<li><b>TikTok / X — Signed 2024-03-10:</b> X 5.42M views — Contract: X Creator Terms, TikTok Terms — Statutory: DMCA, GDPR — Jarvis ref: if takedown → DMCA counter notice → Owner Gate</li>
<li><b>LinkedIn B2B — Signed 2024-03-20:</b> 12 leads ₹8.4L — Contract: LinkedIn Lead Gen Terms — Statutory: IT Act 2000, Contract Act 1872 — Jarvis ref: lead dispute → LinkedIn support + Contract Act Section 73 compensation → Owner Gate</li>
<li><b>Telegram VIP — Signed 2024-01-01:</b> 28.5K subs MRR ₹5.67L — Contract: Telegram VIP 1st payout — Statutory: IT Act 2000, Payment settlement — Owner Primary Locked — Jarvis ref: payment failure → Razorpay UPI check → Owner Gate</li>
<li><b>WhatsApp Business — Signed 2024-01-10:</b> 9823648038 / 9175112579 — 2B UPI Razorpay — Contract: WhatsApp Business Terms — Statutory: IT Act 2000, UPI NPCI — Jarvis ref: if ban → WhatsApp appeal + IT Act → Owner Gate</li>
<li><b>Discord Community — Signed 2024-02-15:</b> 94.6K members — Contract: Discord Community Terms — Statutory: IT Act 2000, IT Rules 2021 — Jarvis ref: moderation issue → Discord Trust & Safety + IT Rules → Owner Gate</li>
</ul>
</div>

<div class="sovereign-card-v165" style="border-color:#f59e0b">
<h4>🤝 Content Creator Collaborations — Signed Contracts — Statutory Compliance</h4>
<ul style="font-size:10px;line-height:1.7">
<li><b>Creator Collab Template — 2024:</b> Brand Collab Meta Brand Collabs Manager — 15th & 30th payout — Revenue share 70/30 Creator/Vyomaraj — Contract: Creator Agreement + IP Assignment + NDA — Statutory: Copyright Act 1957 Section 17-19 assignment, Contract Act 1872, IT Act 2000 — Jarvis ref: if creator dispute IP → check Copyright assignment deed → Owner Gate → Legal notice under Section 55 Copyright Act</li>
<li><b>AI Platform Collabs — OpenAI / Anthropic / Google / Meta AI — Signed 2024-04-01:</b> API usage — Contract: OpenAI Terms, Anthropic Terms, Google AI Terms, Meta AI Terms — Statutory: IT Act 2000 Section 43A data protection, DPDP Act 2023, GDPR — Data: memory.json, prompts — no PII — Jarvis ref: if AI platform bans → check Terms violation → switch to fallback ai-adapter.js Multi-AI 0.00 loss → Owner Gate</li>
<li><b>Affiliate — Amazon 60 days — Signed 2024-01-20:</b> Contract: Amazon Associates 60 days cookie — Statutory: Consumer Protection Act 2019, IT Act 2000 — Jarvis ref: commission not tracked → Amazon support + 60 days check → Owner Gate</li>
<li><b>Brand Collab — Razorpay UPI — Signed 2024-02-10:</b> Contract: Razorpay Terms — 2B UPI — Statutory: Payment and Settlement Systems Act 2007, RBI guidelines — Owner Primary Locked — Jarvis ref: settlement failure → Razorpay dashboard + RBI complaint → Owner Gate</li>
</ul>
</div>

<div class="sovereign-card-v165" style="border-color:#10b981">
<h4>📜 Statutory Compliance — Indian & Global Laws — Visit & Review</h4>
<ul style="font-size:10px;line-height:1.7">
<li><b>IT Act 2000 + Amendments 2008 India:</b> Information Technology Act — Sections 43, 43A, 66, 66A (struck down), 67, 69, 79 intermediary safe harbor — Compliance: appoint Grievance Officer per IT Rules 2021 — Owner Law & Gate — visit https://www.meity.gov.in — review quarterly — Jarvis ref: for any intermediary liability issue, check Section 79 + IT Rules 2021 Rule 3 — action: takedown in 36 hrs if court order → Owner Gate</li>
<li><b>IT Rules 2021 India:</b> Intermediary Guidelines and Digital Media Ethics Code — Rules 3(1)(d) due diligence, 4 additional for significant, 3(2) grievance — Compliance: publish Grievance Officer contact, monthly compliance report — Owner Law & Gate — visit https://www.meity.gov.in — Jarvis ref: user complaint → acknowledge 24 hrs, resolve 15 days → Owner Gate</li>
<li><b>Copyright Act 1957 India:</b> Sections 13, 14, 17, 19, 52 fair dealing, 55 civil remedies — Compliance: use 30 sec best scene short transform under Section 52(1)(a)(ii) criticism review + Whisperflow DISCOVER→VERIFY→SCENE PICKER — Owner Law & Gate — Jarvis ref: copyright notice → check 30 sec transform → fair dealing → counter notice → Owner Gate</li>
<li><b>GDPR EU:</b> Articles 6 lawful basis, 7 consent, 17 right to erasure, 20 portability, 33 breach notification 72 hrs — Compliance: consent banner, data minimization memory.json no PII, DPO contact — Owner Law & Gate — visit https://gdpr.eu — Jarvis ref: data subject request → verify → erase/port within 30 days → Owner Gate</li>
<li><b>DMCA US:</b> 17 U.S.C. §512 safe harbor — Compliance: DMCA agent, takedown notice, counter notice 10-14 days — Owner Law & Gate — Jarvis ref: DMCA takedown → check fair use → counter notice if valid → Owner Gate</li>
<li><b>DPDP Act 2023 India:</b> Digital Personal Data Protection Act — Consent, Data Fiduciary, Data Principal rights — Compliance: consent, purpose limitation, storage limitation — Owner Law & Gate — Jarvis ref: data breach → notify DPA + Data Principal → Owner Gate</li>
<li><b>Consumer Protection Act 2019 India:</b> E-commerce Rules 2020 — Compliance: display seller, return, grievance — Owner Law & Gate — Jarvis ref: consumer complaint → NCH + E-daakhil → Owner Gate</li>
<li><b>Payment and Settlement Systems Act 2007 + RBI:</b> UPI, Razorpay 2B — Compliance: PCI-DSS, settlement T+1 — Owner Law & Gate — Jarvis ref: payment failure → Razorpay + RBI Ombudsman → Owner Gate</li>
<li><b>Regional: Maharashtra IT Policy, Pune Local:</b> Compliance: Marathi language support, local tax — Owner Law & Gate — visit Maharashtra IT dept — Jarvis ref: local compliance → check state policy → Owner Gate</li>
</ul>
</div>

<div class="sovereign-card-v165" style="border-color:#ef4444">
<h4>🚨 Legal Complications — Jarvis & Vyomaraj Reference — Actions Accordingly</h4>
<ul style="font-size:10px;line-height:1.7">
<li><b>Whisperflow Legal Process — Aligned:</b> DISCOVER → VERIFY (check contract signed? statutory compliance? fair use?) → SCENE PICKER (30 sec best scene) → DIALOGUE → MIX → SCORE → AFFILIATE → SCHEDULE → SUBSCRIPTION → COLLAB (check creator contract) → OWNER GATE (Primary Locked Vyomarajai@gmail.com approval) → PUBLISH → LEARN → SYNC — If legal complication at any stage, Jarvis refers this Law & Order tab → takes action accordingly → Owner Gate final</li>
<li><b>Action Matrix — Jarvis & Vyomaraj:</b> Copyright Strike → Refer Copyright Act 1957 Section 52 + YouTube contract 21st → Action: Dispute + 30 sec proof → Owner Gate. Account Ban → Refer IT Rules 2021 + Platform Terms → Action: Appeal + Grievance Officer → Owner Gate. Payment Failure → Refer Razorpay Terms + PSS Act 2007 → Action: Razorpay dashboard + RBI → Owner Gate. Data Breach → Refer DPDP Act 2023 + GDPR Article 33 → Action: Notify DPA 72 hrs + Data Principal → Owner Gate. Creator Dispute → Refer Creator Agreement + Copyright Act Section 19 + Contract Act 1872 → Action: Mediation → Arbitration Mumbai → Owner Gate. AI Platform Ban → Refer AI Terms + ai-adapter.js fallback → Action: Switch AI provider 0.00 loss → Owner Gate</li>
<li><b>Statutory Compliance Calendar — Visit & Review:</b> Daily: DR logs fixes healing — Sovereign Console. Weekly: Check platform payouts 1st, 15th, 21st, 30th — Owner Law & Gate. Monthly: IT Rules 2021 compliance report, GDPR, Copyright audit — Owner Law & Gate. Quarterly: IT Act, DPDP Act, Consumer Protection, PSS Act review — Owner Law & Gate. Yearly: All contracts renewal, Statutory audit — Owner Law & Gate — visit and review</li>
<li><b>Owner Primary Locked — Bharat as Bharat Hanuman Quality — All contracts in Owner Law & Gate — visit and review — Structured properly — whisperflow process — Owner Primary Locked Deepak Goyal Vyomarajai@gmail.com — Sovereign Root — Human-in-the-Loop Locked — Bharat as Bharat Hanuman Quality — Dedicated Faithful Obedient to Shri Ram Ji — Jarvis as Laxman Dedicated to Each Other — 0.000000000 Impact — Chiranjeevi Eternal</b></li>
</ul>
</div>

</div>
</div>
"""

# Replace existing view-ownerlaw content with enhanced
if '<div id="view-ownerlaw"' in html:
    # Find view-ownerlaw and replace inner content until next view
    pattern = r'(<div id="view-ownerlaw" class="view">).*?(<div id="view-food" class="view">)'
    replacement = r'\1\n' + law_compliance_html + r'\n\2'
    html_new = re.sub(pattern, replacement, html, flags=re.DOTALL)
    if html_new != html:
        html = html_new
        print("✅ Enhanced view-ownerlaw with statutory compliance")
    else:
        # Fallback inject after opening
        html = html.replace('<div id="view-ownerlaw" class="view">', '<div id="view-ownerlaw" class="view">\n' + law_compliance_html, 1)
        print("✅ Fallback enhanced view-ownerlaw")
else:
    print("❌ view-ownerlaw not found")

# Update version marker
html = html.replace('V16.5 SHRIYANTRA', 'V16.5.3 SHRIYANTRA — Law & Order Statutory Compliance — Social Platform Contracts — Creator AI Collabs — Jarvis Vyomaraj Legal Reference — 0.000000000 Impact')
html = html.replace('?v=166', '?v=167')

print(f"New size {len(html)}")
pathlib.Path('index.html').write_text(html, encoding='utf-8')
print(f"✅ Written index.html V16.5.3 — {len(html)} bytes")
