import requests
import json
import os
import re
from datetime import datetime, timezone, timedelta
from collections import defaultdict

TOKEN = os.environ.get("SYMPLA_TOKEN")
EVENT_ID = "3315673"
BRT = timezone(timedelta(hours=-3))

CUPONS_MAP = {
    "BemVindoSPIW26": "Marktech Meta",
    "SPIW2026":       "Marktech Google",
    "EBEstadao":      "EBEstadao",
    "EmmRIW":         "EmmRIW",
}
CUPONS  = ["Orgânico", "Marktech Meta", "Marktech Google", "EBEstadao", "EmmRIW"]
COLORS  = ["#00d9ff", "#9b5cf6", "#4d9fff", "#ff8c42", "#ff4dab"]

CORTESIA_CAT = {
    "SMARTCITIES": "Curadores", "INDUSTRIA": "Curadores", "REALESTATE": "Curadores",
    "EGOV": "Curadores", "NOVAMOBILIDADE": "Curadores", "AGROTECH": "Curadores",
    "RETAILTALKS": "Curadores", "RETAIL": "Curadores", "DHO": "Curadores",
    "GREENFUTURE": "Curadores", "TRANSICAO": "Curadores", "TRANSIÇÃO": "Curadores",
    "ESPORTE": "Curadores", "SPORT": "Curadores", "POPTECH": "Curadores",
    "PLENARIA": "Curadores", "PLENÁRIA": "Curadores",
    "AIACTION": "Curadores", "A.I": "Curadores", "AIETHICS": "Curadores", "ETHICS": "Curadores",
    "TECHTRENDS": "Curadores", "GLOBALHEALTH": "Curadores", "HEALTHTECH": "Curadores",
    "LUXO": "Curadores", "SPIWTALKS": "Curadores", "CIENCIA": "Curadores",
    "EDTECH": "Curadores", "FUTUROTRABALHO": "Curadores", "SPIWFUTURE": "Curadores",
    "CREATORS": "Curadores", "LIFESTYLE": "Curadores", "MULHERES": "Curadores",
    "CINEMA": "Curadores", "ENTRETENIMENTO": "Curadores", "SOFTPOWER": "Curadores",
    "PODCAST": "Curadores", "FINTECH": "Curadores", "BLOCKCHAIN": "Curadores",
    "CRYPTO": "Curadores", "GEOPOLITICA": "Curadores", "LEGAL": "Curadores",
    "MASTERCLASS": "Curadores", "BOOKSIGN": "Curadores", "FASHION": "Curadores",
    "CONSUMO": "Curadores", "MUSICSPACE": "Curadores", "SIDEEVENTS": "Curadores",

    "APEXBRASIL": "Patrocinadores Privados", "APEX": "Patrocinadores Privados",
    "FNT": "Patrocinadores Privados", "FIESP": "Patrocinadores Privados",
    "FEBRABAN": "Patrocinadores Privados", "EINSTEIN": "Patrocinadores Privados",
    "GWM": "Patrocinadores Privados", "REDEAMERICAS": "Patrocinadores Privados",
    "CATERPILLAR": "Patrocinadores Privados",

    "PREFEITURA": "Esferas Públicas", "GOVERNO": "Esferas Públicas",

    "MOTOROLA": "Expositores", "CMRSURGICAL": "Expositores", "EMBARCADERO": "Expositores",
    "SOUTECH": "Expositores", "FUTUREMEDIA": "Expositores", "BASF": "Expositores",
    "PD7": "Expositores", "SUZANO": "Expositores", "ORACLE": "Expositores",
    "ASICS": "Expositores", "AUSTRIA": "Expositores", "GEMINI": "Expositores",
    "INGOO": "Expositores", "PHIZ": "Expositores", "WEG": "Expositores",
    "INSIDER": "Expositores",

    "GLOBO": "Parceiros de Mídia", "EXAME": "Parceiros de Mídia",
    "LINKEDIN": "Parceiros de Mídia", "MIT": "Parceiros de Mídia",
    "RECORD": "Parceiros de Mídia", "OXYGEN": "Parceiros de Mídia",
    "ALADAS": "Parceiros de Mídia", "AMPRO": "Parceiros de Mídia",
    "MOOVERS": "Parceiros de Mídia", "COWWORK": "Parceiros de Mídia",
    "OCLB": "Parceiros de Mídia", "KES": "Parceiros de Mídia",
    "WHITERABBIT": "Parceiros de Mídia", "BOOST": "Parceiros de Mídia",
    "BOSSAWOMEN": "Parceiros de Mídia", "FELICIDADE": "Parceiros de Mídia",
    "BROADCAST": "Parceiros de Mídia",

    "ANGAMARCAS": "Parceiro", "ANGA": "Parceiro", "MARINHA": "Parceiro",

    "LEDPULSE": "Experiência", "EXOESQUELETO": "Experiência",

    "FAAP": "FAAP",

    "ESTADAO": "Estadão",

    "INVESTIDOR": "Open Innovation", "HUBS": "Open Innovation", "STARTUP": "Open Innovation",

    "SECMUNICIPAL": "Rouanet", "SECESTAD": "Rouanet",
    "PROJETOSSOCIAIS": "Rouanet", "ROUANET": "Rouanet",

    "ABF": "Universidades / Estratégicos",
    "ABEEOLICA": "Universidades / Estratégicos", "ABRACEEL": "Universidades / Estratégicos",
    "ABSOLAR": "Universidades / Estratégicos", "BRXR": "Universidades / Estratégicos",
    "B2MAMY": "Universidades / Estratégicos", "CEBDS": "Universidades / Estratégicos",
    "CENTROEMPRESARIAL": "Universidades / Estratégicos",
    "CAMARAARABE": "Universidades / Estratégicos", "DCSET": "Universidades / Estratégicos",
    "ECHOS": "Universidades / Estratégicos", "INFINITEFOUNDRY": "Universidades / Estratégicos",
    "ICMC": "Universidades / Estratégicos", "ISGAME": "Universidades / Estratégicos",
    "MASP": "Universidades / Estratégicos", "PACTOGLOBAL": "Universidades / Estratégicos",
    "PROREI": "Universidades / Estratégicos", "SCHOOLOFLIFE": "Universidades / Estratégicos",
    "SERMAIS": "Universidades / Estratégicos", "TANTEMPOS": "Universidades / Estratégicos",
    "ESEG": "Universidades / Estratégicos", "COEFICIENTE": "Universidades / Estratégicos",
    "ADRIANAMORAES": "Universidades / Estratégicos",

    "CAROLDOSTAL": "Embaixadores", "LUCIANOSANTOS": "Embaixadores",
    "MARCELNOBRE": "Embaixadores", "JANDARACI": "Embaixadores",
    "CAMILOBARROS": "Embaixadores", "RENATOGRAU": "Embaixadores",
    "ADRIANOLIMA": "Embaixadores", "CAROLROMANO": "Embaixadores",
    "DILMASOUZA": "Embaixadores", "BRENOPFISTER": "Embaixadores",
    "AMANDAGRACIANO": "Embaixadores", "CAMILAFARANI": "Embaixadores",
    "VANESSAMATHIAS": "Embaixadores",

    "LIRIA": "Área Internacional",
}

CORTESIA_TOTAL = {
    "Patrocinadores Privados":      2000,
    "Esferas Públicas":             3000,
    "Expositores":                  1000,
    "Parceiros de Mídia":            500,
    "Parceiro":                      220,
    "Experiência":                    20,
    "Curadores":                    2650,
    "FAAP":                         4000,
    "Estadão":                      2020,
    "Open Innovation":              3000,
    "Rouanet":                      1000,
    "Universidades / Estratégicos": 3500,
    "Embaixadores":                    0,
    "Área Internacional":             50,
    "Outros (Gratuitos)":              0,
}

CORTESIA_ORDER = [
    "Curadores", "FAAP", "Esferas Públicas", "Open Innovation",
    "Estadão", "Patrocinadores Privados", "Expositores",
    "Parceiros de Mídia", "Universidades / Estratégicos",
    "Rouanet", "Parceiro", "Experiência", "Embaixadores",
    "Área Internacional", "Outros (Gratuitos)",
]

CORTESIA_COLORS = [
    "#00d9ff","#9b5cf6","#4d9fff","#ff8c42","#ff4dab",
    "#00ff9d","#ffd700","#ff6b6b","#c084fc","#34d399",
    "#f97316","#60a5fa","#e879f9","#a3e635","#94a3b8",
]


def extract_cupom_pai(discount_str):
    if not discount_str:
        return None
    m = re.search(r'-\s*(.+)$', discount_str)
    return m.group(1).strip() if m else None


def extract_pct(discount_str):
    if not discount_str:
        return 0.0
    m = re.match(r'([\d.]+)%', discount_str.strip())
    return float(m.group(1)) if m else 0.0


def classify_cortesia(cupom_pai):
    if not cupom_pai:
        return None
    upper = cupom_pai.upper().replace(" ", "").replace("-", "").replace("_", "")
    for kw, cat in CORTESIA_CAT.items():
        kw_clean = kw.upper().replace(" ", "").replace("-", "").replace("_", "")
        if kw_clean in upper:
            return cat
    return None


def get_all_participants():
    participants = []
    page = 1
    while True:
        url = f"https://api.sympla.com.br/public/v3/events/{EVENT_ID}/participants"
        r = requests.get(url, headers={"s-token": TOKEN}, params={"page_size": 200, "page": page})
        data = r.json()
        items = data.get("data", [])
        if not items:
            break
        participants.extend(items)
        if not data.get("pagination", {}).get("has_next", False):
            break
        page += 1
    return participants


def get_all_orders():
    orders = []
    page = 1
    while True:
        url = f"https://api.sympla.com.br/public/v3/events/{EVENT_ID}/orders"
        r = requests.get(url, headers={"s-token": TOKEN}, params={"page_size": 200, "page": page})
        data = r.json()
        items = data.get("data", [])
        if not items:
            break
        orders.extend(items)
        if not data.get("pagination", {}).get("has_next", False):
            break
        page += 1
    return orders


def classify_cupom_vendas(discount_str):
    disc = discount_str or ""
    for code, name in CUPONS_MAP.items():
        if code in disc:
            return name
    return "Orgânico"


def process(participants, orders):
    by_day = {}
    by_origin = {c: {"t": 0, "c": 0, "p": 0, "r": 0} for c in CUPONS}
    total = {"t": 0, "c": 0, "p": 0}
    cortesias = defaultdict(lambda: defaultdict(int))
    parceiros = defaultdict(lambda: {"pct": 0.0, "count": 0})

    approved_orders = set()
    for p in participants:
        created = p.get("order_date", "") or ""
        try:
            dt = datetime.strptime(created[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=BRT)
            dia = dt.strftime("%d/%m")
        except:
            dia = "??"

        discount_str = p.get("order_discount", "") or ""
        valor = float(p.get("ticket_sale_price", 0) or 0)
        order_id = p.get("order_id", "")
        approved_orders.add(order_id)
        cupom_pai = extract_cupom_pai(discount_str)
        pct = extract_pct(discount_str)

        if valor == 0 or pct == 100.0:
            if cupom_pai:
                cat = classify_cortesia(cupom_pai) or "Outros (Gratuitos)"
                cortesias[cat][cupom_pai] += 1
            continue

        cupom_vendas = classify_cupom_vendas(discount_str)
        if cupom_vendas == "Orgânico" and pct > 0 and cupom_pai:
            parceiros[cupom_pai]["pct"] = pct
            parceiros[cupom_pai]["count"] += 1
            continue

        cupom = cupom_vendas
        if dia not in by_day:
            by_day[dia] = {"total": 0, "confirmados": 0, "pendentes": 0, "orig": {}}
        if cupom not in by_day[dia]["orig"]:
            by_day[dia]["orig"][cupom] = {"t": 0, "c": 0, "p": 0}

        by_day[dia]["total"] += 1
        by_day[dia]["confirmados"] += 1
        by_day[dia]["orig"][cupom]["t"] += 1
        by_day[dia]["orig"][cupom]["c"] += 1
        by_origin[cupom]["t"] += 1
        by_origin[cupom]["c"] += 1
        by_origin[cupom]["r"] += valor
        total["t"] += 1
        total["c"] += 1

    for o in orders:
        status = o.get("status", "") or o.get("order_status", "")
        order_id = o.get("id", "") or o.get("order_id", "")
        if status == "A" or str(order_id) in approved_orders or order_id in approved_orders:
            continue
        created = o.get("created_date", "") or o.get("order_date", "") or ""
        try:
            dt = datetime.strptime(created[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=BRT)
            dia = dt.strftime("%d/%m")
        except:
            dia = "??"
        cupom = classify_cupom_vendas(o.get("discount_code", "") or o.get("order_discount", ""))
        qty = int(o.get("quantity", 1) or 1)
        if dia not in by_day:
            by_day[dia] = {"total": 0, "confirmados": 0, "pendentes": 0, "orig": {}}
        if cupom not in by_day[dia]["orig"]:
            by_day[dia]["orig"][cupom] = {"t": 0, "c": 0, "p": 0}
        by_day[dia]["total"] += qty
        by_day[dia]["pendentes"] += qty
        by_day[dia]["orig"][cupom]["t"] += qty
        by_day[dia]["orig"][cupom]["p"] += qty
        by_origin[cupom]["t"] += qty
        by_origin[cupom]["p"] += qty
        total["t"] += qty
        total["p"] += qty

    return by_day, by_origin, total, dict(cortesias), dict(parceiros)


def fmt_brl(v):
    s = f"{v:,.0f}".replace(",", ".")
    return f"R$ {s}"


def generate_html(by_day, by_origin, total, cortesias, parceiros):
    now = datetime.now(BRT)
    ts = now.strftime("%d/%m/%Y · %Hh%M")
    dias = sorted(by_day.keys(), key=lambda d: datetime.strptime(d, "%d/%m"))
    ndias = len(dias)
    rec_conf = sum(by_origin[c]["r"] for c in CUPONS)
    taxa = round(total["c"] / total["t"] * 100) if total["t"] else 0

    orig_data = {}
    for c in CUPONS:
        o = by_origin[c]
        if o["t"] > 0:
            orig_data[c] = {"t": o["t"], "c": o["c"], "p": o["p"], "r": fmt_brl(o["r"])}

    cortesias_data = []
    for cat in CORTESIA_ORDER:
        cupons_cat = cortesias.get(cat, {})
        utilizados = sum(cupons_cat.values())
        disponivel = CORTESIA_TOTAL.get(cat, 0)
        pct = round(utilizados / disponivel * 100, 1) if disponivel > 0 else 0
        cupons_list = [{"nome": k, "utilizados": v} for k, v in sorted(cupons_cat.items(), key=lambda x: -x[1])]
        if utilizados > 0 or disponivel > 0:
            cortesias_data.append({
                "cat": cat, "disponivel": disponivel,
                "utilizados": utilizados, "pct": pct, "cupons": cupons_list,
            })

    parceiros_data = [
        {"cupom": k, "pct": v["pct"], "count": v["count"]}
        for k, v in sorted(parceiros.items(), key=lambda x: -x[1]["count"])
    ]

    html = open("template.html").read()
    html = html.replace("__TIMESTAMP__",      ts)
    html = html.replace("__TOTAL__",          str(total["t"]))
    html = html.replace("__CONF__",           str(total["c"]))
    html = html.replace("__PEND__",           str(total["p"]))
    html = html.replace("__TAXA__",           str(taxa))
    receita_num = f"{int(rec_conf):,}".replace(",", ".")
    ticket = str(round(rec_conf / total["c"])) if total["c"] else "0"
    html = html.replace("__RECEITA__",        fmt_brl(rec_conf))
    html = html.replace("__RECEITA_NUM__",    receita_num)
    html = html.replace("__TICKET__",         ticket)
    html = html.replace("__NDIAS__",          str(ndias))
    html = html.replace("__DIAS_JSON__",      json.dumps(dias, ensure_ascii=False))
    html = html.replace("__BY_DAY_JSON__",    json.dumps(by_day, ensure_ascii=False))
    html = html.replace("__ORIG_JSON__",      json.dumps(orig_data, ensure_ascii=False))
    html = html.replace("__CUPONS_JSON__",    json.dumps(CUPONS, ensure_ascii=False))
    html = html.replace("__COLORS_JSON__",    json.dumps(COLORS))
    html = html.replace("__CORTESIAS_JSON__", json.dumps(cortesias_data, ensure_ascii=False))
    html = html.replace("__PARCEIROS_JSON__", json.dumps(parceiros_data, ensure_ascii=False))
    html = html.replace("__CAT_COLORS_JSON__",json.dumps(CORTESIA_COLORS))
    return html


if __name__ == "__main__":
    print("Buscando participantes aprovados...")
    participants = get_all_participants()
    print(f"Aprovados: {len(participants)}")

    print("Buscando pedidos...")
    orders = get_all_orders()
    print(f"Total pedidos: {len(orders)}")

    by_day, by_origin, total, cortesias, parceiros = process(participants, orders)
    total_cort = sum(sum(c.values()) for c in cortesias.values())
    total_parc = sum(v["count"] for v in parceiros.values())
    print(f"Vendas: {total['t']} | Cortesias: {total_cort} | Parceiros desconto: {total_parc}")

    print("=== CORTESIAS POR CATEGORIA ===")
    for cat, cupons in cortesias.items():
        print(f"  {cat}: {sum(cupons.values())} → {list(cupons.items())}")

    print("=== PARCEIROS COM DESCONTO ===")
    for cupom, v in sorted(parceiros.items(), key=lambda x: -x[1]["count"]):
        print(f"  {cupom}: {v['count']}x @ {v['pct']}% off")

    html = generate_html(by_day, by_origin, total, cortesias, parceiros)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html gerado com sucesso!")
