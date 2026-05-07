import requests
import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

TOKEN = os.environ.get("SYMPLA_TOKEN")
EVENT_IDS = ["3315673", "3369150"]
BRT = timezone(timedelta(hours=-3))

CUPONS_MAP = {
    "BemVindoSPIW26": "Marktech Meta",
    "SPIW2026":       "Marktech Google",
    "EBEstadao":      "EBEstadao",
    "EmmRIW":         "EmmRIW",
}
CUPONS = ["Orgânico", "Marktech Meta", "Marktech Google", "EBEstadao", "EmmRIW"]
COLORS = ["#00d9ff", "#9b5cf6", "#4d9fff", "#ff8c42", "#ff4dab"]

CORTESIA_CAT = {
    # Palestrantes — prioridade máxima (inclui typo "palestrantre")
    "PALESTRANTE": "Palestrantes", "PALESTR": "Palestrantes", "PALESTRANTRE": "Palestrantes",

    # Curadores
    "SMARTCITIES": "Curadores", "INDUSTRIA": "Curadores", "REALESTATE": "Curadores",
    "EGOV": "Curadores", "NOVAMOBILIDADE": "Curadores", "AGROTECH": "Curadores",
    "RETAILTALKS": "Curadores", "RETAIL": "Curadores", "DHO": "Curadores",
    "GREENFUTURE": "Curadores", "TRANSICAO": "Curadores", "ESPORTE": "Curadores",
    "SPORT": "Curadores", "POPTECH": "Curadores", "PLENARIA": "Curadores",
    "AIACTION": "Curadores", "AIETHICS": "Curadores", "ETHICS": "Curadores",
    "TECHTRENDS": "Curadores", "GLOBALHEALTH": "Curadores", "HEALTHTECH": "Curadores",
    "LUXO": "Curadores", "SPIWTALKS": "Curadores", "CIENCIA": "Curadores",
    "EDTECH": "Curadores", "FUTUROTRABALHO": "Curadores", "FUTURO": "Curadores",
    "SPIWFUTURE": "Curadores", "CREATORS": "Curadores", "LIFESTYLE": "Curadores",
    "MULHERES": "Curadores", "CINEMA": "Curadores", "ENTRETENIMENTO": "Curadores",
    "SOFTPOWER": "Curadores", "PODCAST": "Curadores", "FINTECH": "Curadores",
    "BLOCKCHAIN": "Curadores", "CRYPTO": "Curadores", "GEOPOLITICA": "Curadores",
    "LEGAL": "Curadores", "MASTERCLASS": "Curadores", "BOOKSIGN": "Curadores",
    "FASHION": "Curadores", "CONSUMO": "Curadores", "MUSICSPACE": "Curadores",
    "SIDEEVENTS": "Curadores", "IMMERSIVE": "Curadores",
    "HUMANARE": "Curadores", "AREAINTERNACIONAL": "Curadores", "ÁREA INTERNACIONAL": "Curadores",
    "AIINACTION": "Curadores", "A.I IN ACTION": "Curadores", "AINACTION": "Curadores",
    "CREATOR": "Curadores", "ENERGYHUB": "Curadores", "ENERGY HUB": "Curadores",
    "TILT": "Curadores", "MIT": "Curadores",
    "TRANSICAOENERGETICA": "Curadores", "TRANSIÇÃO ENERGETICA": "Curadores",
    "PALAVRA": "Curadores", "VCSQUARE": "Curadores", "VC SQUARE": "Curadores",

    # Patrocinadores Privados
    "APEXBRASIL": "Patrocinadores Privados", "APEX": "Patrocinadores Privados",
    "FNT": "Patrocinadores Privados", "FIESP": "Patrocinadores Privados",
    "FEBRABAN": "Patrocinadores Privados", "EINSTEIN": "Patrocinadores Privados",
    "GWM": "Patrocinadores Privados", "REDEAMERICAS": "Patrocinadores Privados",
    "CATERPILLAR": "Patrocinadores Privados",
    "GOVSP": "Patrocinadores Privados", "GOV SP": "Patrocinadores Privados",
    "VALE": "Patrocinadores Privados",
    "SPNEGOCIOS": "Patrocinadores Privados", "SP NEGOCIOS": "Patrocinadores Privados", "SPNEG": "Patrocinadores Privados",
    "CONSELHOESTADAO": "Patrocinadores Privados", "CONSELHO ESTADAO": "Patrocinadores Privados",
    "INOVABRA": "Patrocinadores Privados",
    "STELLANTIS": "Patrocinadores Privados",
    "RESECURITY": "Patrocinadores Privados",
    "COCACOLA": "Patrocinadores Privados", "COCA-COLA": "Patrocinadores Privados", "INSTITUTOCOCACOLA": "Patrocinadores Privados",

    # Esferas Públicas
    "PREFEITURA": "Esferas Públicas", "GOVERNO": "Esferas Públicas", "PACAEMBU": "Esferas Públicas",

    # Expositores
    "MOTOROLA": "Expositores", "CMRSURGICAL": "Expositores", "EMBARCADERO": "Expositores",
    "SOUTECH": "Expositores", "FUTUREMEDIA": "Expositores", "BASF": "Expositores",
    "PD7": "Expositores", "SUZANO": "Expositores", "ORACLE": "Expositores",
    "ASICS": "Expositores", "AUSTRIA": "Expositores", "GEMINI": "Expositores",
    "INGOO": "Expositores", "PHIZ": "Expositores", "WEG": "Expositores",
    "INSIDER": "Expositores",

    # Parceiros de Mídia
    "GLOBO": "Parceiros de Mídia", "EXAME": "Parceiros de Mídia",
    "LINKEDIN": "Parceiros de Mídia", "RECORD": "Parceiros de Mídia",
    "OXYGEN": "Parceiros de Mídia", "ALADAS": "Parceiros de Mídia",
    "AMPRO": "Parceiros de Mídia", "MOOVERS": "Parceiros de Mídia",
    "COWWORK": "Parceiros de Mídia", "OCLB": "Parceiros de Mídia",
    "KES": "Parceiros de Mídia", "WHITERABBIT": "Parceiros de Mídia",
    "BOOST": "Parceiros de Mídia", "BOSSAWOMEN": "Parceiros de Mídia",
    "BOSSA": "Parceiros de Mídia", "FELICIDADE": "Parceiros de Mídia",
    "BROADCAST": "Parceiros de Mídia",

    # Parceiro genérico
    "ANGAMARCAS": "Parceiro", "ANGA": "Parceiro", "MARINHA": "Parceiro",

    # Experiência
    "LEDPULSE": "Experiência", "EXOESQUELETO": "Experiência",

    # FAAP — todas as variações
    "FAAP": "FAAP", "CONVIDADOFAAP": "FAAP", "CONVIDADO FAAP": "FAAP",
    "AMIGOSFAAP": "FAAP", "AMIGOS DA FAAP": "FAAP", "AMIGOSDAFAAP": "FAAP",
    "BUSINESSFAAP": "FAAP", "BUSINESS FAAP": "FAAP",
    "BUSINESSAREA": "FAAP", "BUSINESS AREA": "FAAP",
    "CORTESIAFAAP": "FAAP", "PASSAPORTE CORTESIA FAAP": "FAAP",

    # Estadão
    "ESTADAO": "Estadão", "CLUBEESTADAO": "Estadão", "CLUBE ESTADAO": "Estadão",
    "CORTESIAASSINANTE": "Estadão", "CORTESIA ASSINANTE": "Estadão",
    "ASSINANTEESTADAO": "Estadão",

    # Open Innovation
    "INVESTIDOR": "Open Innovation", "HUBS": "Open Innovation",
    "STARTUP": "Open Innovation", "OPENINNOVATION": "Open Innovation",
    "OISPIW": "Open Innovation", "OI ": "Open Innovation",

    # Rouanet
    "SECMUNICIPAL": "Rouanet", "SECESTAD": "Rouanet",
    "PROJETOSSOCIAIS": "Rouanet", "ROUANET": "Rouanet",

    # Universidades / Estratégicos
    "ABF": "Universidades / Estratégicos",
    "ABEEOLICA": "Universidades / Estratégicos", "ABRACEEL": "Universidades / Estratégicos",
    "ABSOLAR": "Universidades / Estratégicos", "BRXR": "Universidades / Estratégicos",
    "B2MAMY": "Universidades / Estratégicos", "CEBDS": "Universidades / Estratégicos",
    "CEBC": "Universidades / Estratégicos", "CENTROEMPRESARIAL": "Universidades / Estratégicos",
    "CAMARAARABE": "Universidades / Estratégicos", "DCSET": "Universidades / Estratégicos",
    "ECHOS": "Universidades / Estratégicos", "INFINITEFOUNDRY": "Universidades / Estratégicos",
    "ICMC": "Universidades / Estratégicos", "ISGAME": "Universidades / Estratégicos",
    "MASP": "Universidades / Estratégicos", "PACTOGLOBAL": "Universidades / Estratégicos",
    "PROREI": "Universidades / Estratégicos", "SCHOOLOFLIFE": "Universidades / Estratégicos",
    "SERMAIS": "Universidades / Estratégicos", "TANTEMPOS": "Universidades / Estratégicos",
    "ESEG": "Universidades / Estratégicos", "COEFICIENTE": "Universidades / Estratégicos",
    "ADRIANAMORAES": "Universidades / Estratégicos", "GLOBALECOSSYSTEM": "Universidades / Estratégicos",

    # Embaixadores
    "CAROLDOSTAL": "Embaixadores", "LUCIANOSANTOS": "Embaixadores",
    "MARCELNOBRE": "Embaixadores", "JANDARACI": "Embaixadores",
    "CAMILOBARROS": "Embaixadores", "RENATOGRAU": "Embaixadores",
    "ADRIANOLIMA": "Embaixadores", "CAROLROMANO": "Embaixadores",
    "DILMASOUZA": "Embaixadores", "BRENOPFISTER": "Embaixadores",
    "AMANDAGRACIANO": "Embaixadores", "CAMILAFARANI": "Embaixadores",
    "VANESSAMATHIAS": "Embaixadores",

    # Área Internacional
    "LIRIA": "Área Internacional", "AREAINTER": "Área Internacional",
    "AREAINTERNACIONAL": "Área Internacional",

    # Campanhas
    "CAMPANHamit": "Campanha MIT", "CAMPANHA MIT": "Campanha MIT",
    "CAMPANHAENERGIA": "Campanha Energia", "CAMPANHA ENERGIA": "Campanha Energia",
    "CAMPANHAESPORTE": "Campanha Esporte", "CAMPANHA ESPORTE": "Campanha Esporte",
}

CORTESIA_TOTAL = {
    "Palestrantes":                  540,
    "Curadores":                    2650,
    "FAAP":                         4000,
    "Esferas Públicas":             3000,
    "Open Innovation":              3000,
    "Estadão":                      2020,
    "Patrocinadores Privados":      2000,
    "Expositores":                  1000,
    "Parceiros de Mídia":            500,
    "Universidades / Estratégicos": 3500,
    "Rouanet":                      1000,
    "Parceiro":                      220,
    "Experiência":                    20,
    "Embaixadores":                    0,
    "Área Internacional":             50,
    "Campanhas":                        0,
    "Outros (Gratuitos)":              0,
}

CORTESIA_ORDER = [
    "Palestrantes", "Curadores", "FAAP", "Esferas Públicas", "Open Innovation",
    "Estadão", "Patrocinadores Privados", "Expositores",
    "Parceiros de Mídia", "Universidades / Estratégicos",
    "Rouanet", "Parceiro", "Experiência",
    "Embaixadores", "Área Internacional", "Campanhas",
    "Outros (Gratuitos)",
]

CORTESIA_COLORS = [
    "#00d9ff","#9b5cf6","#4d9fff","#ff8c42","#ff4dab",
    "#00ff9d","#ffd700","#ff6b6b","#c084fc","#34d399",
    "#f97316","#60a5fa","#e879f9","#a3e635","#64748b","#94a3b8",
    "#06b6d4","#8b5cf6","#10b981",
]

CLEVEL_KW = [
    "CEO","CFO","COO","CTO","CMO","CISO","CRO","CDO","CSO","CPO","CHRO",
    "DIRETOR","DIRETORA","PRESIDENT","VP ","VICE-PRESI","VICE PRESI",
    "SÓCIO","SOCIO","PARTNER","FOUNDER","CO-FOUNDER","COFOUND",
    "MANAGING DIRECTOR","MD ","BOARD","CONSELHEIRO","CONSELHEIRA",
]


# Mapeamento de cupom → nome da subcampanha
CAMPANHA_MAP = {
    "CONVITE":         "Campanha MIT 1",
    "CAMPANHAMT":      "Campanha MIT Redes",
    "CONVIDADOSMIT":   "Campanha MIT Emmkt",
    "CONVIDADOS MIT":  "Campanha MIT Emmkt",
    "CAMPANHAENERGIA": "Campanha Energia",
    "CAMPANHAESPORTE": "Campanha Esporte",
}

def get_campanha_sub(cupom_pai):
    """Retorna subcategoria de campanha para um cupom, ou None."""
    if not cupom_pai:
        return None
    upper = re.sub(r"[\s\-_]", "", cupom_pai.upper())
    for k, v in CAMPANHA_MAP.items():
        kc = re.sub(r"[\s\-_]", "", k.upper())
        if kc in upper or upper == kc:
            return v
    return None


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


def classify_cortesia(cupom_pai, ticket_name=""):
    """Classifica cortesia — palestrante tem prioridade máxima."""
    combined = f"{cupom_pai or ''} {ticket_name or ''}".upper()
    combined_clean = re.sub(r'[\s\-_]', '', combined)

    # Palestrante: prioridade máxima
    if "PALESTR" in combined_clean:
        return "Palestrantes"

    # ticket_name direto para FAAP
    tn = re.sub(r'[\s\-_]', '', (ticket_name or "").upper())
    if "CORTESIAFAAP" in tn or "PASSAPORTECORTESIAFAAP" in tn:
        return "FAAP"
    # ticket_name direto para Estadão
    if "CORTESIAASSINANTE" in tn or "CORTESIAESTADAO" in tn or "PASSAPORTECORTESIAASSINANTE" in tn:
        return "Estadão"

    if not cupom_pai:
        return None
    upper = re.sub(r'[\s\-_]', '', cupom_pai.upper())
    # Campanhas têm prioridade antes de Curadores
    campanha_keys = ["CONVITE","CAMPANHAMT","CONVIDADOSMIT","CAMPANHAENERGIA","CAMPANHAESPORTE"]
    for ck in campanha_keys:
        if ck in upper:
            return "Campanhas"
    for kw, cat in CORTESIA_CAT.items():
        kw_clean = re.sub(r'[\s\-_]', '', kw.upper())
        if kw_clean in upper:
            return cat
    return None


def get_form_field(participant, field_name):
    for f in participant.get("custom_form", []):
        if f.get("name", "").strip().lower() == field_name.lower():
            return (f.get("value") or "").strip()
    return ""


def is_clevel(cargo):
    if not cargo:
        return False
    upper = cargo.upper()
    return any(kw in upper for kw in CLEVEL_KW)


def get_participants(event_id):
    participants = []
    page = 1
    while True:
        url = f"https://api.sympla.com.br/public/v3/events/{event_id}/participants"
        r = requests.get(url, headers={"s-token": TOKEN}, params={"page_size": 200, "page": page})
        data = r.json()
        items = data.get("data", [])
        if not items:
            break
        participants.extend(items)
        if not data.get("pagination", {}).get("has_next", False):
            break
        page += 1
        time.sleep(0.5)
    return participants


def get_orders(event_id):
    orders = []
    page = 1
    while True:
        url = f"https://api.sympla.com.br/public/v3/events/{event_id}/orders"
        r = requests.get(url, headers={"s-token": TOKEN}, params={"page_size": 200, "page": page})
        data = r.json()
        items = data.get("data", [])
        if not items:
            break
        orders.extend(items)
        if not data.get("pagination", {}).get("has_next", False):
            break
        page += 1
        time.sleep(0.5)
    return orders


def classify_cupom_vendas(discount_str):
    disc = discount_str or ""
    for code, name in CUPONS_MAP.items():
        if code in disc:
            return name
    return "Orgânico"


def process(all_participants, all_orders):
    by_day = {}
    by_origin = {c: {"t": 0, "c": 0, "p": 0, "r": 0} for c in CUPONS}
    total = {"t": 0, "c": 0, "p": 0}
    cortesias = defaultdict(lambda: defaultdict(int))
    parceiros = defaultdict(lambda: {"pct": 0.0, "count": 0})
    total_cort = 0

    approved_orders = set()
    for p in all_participants:
        created = p.get("order_date", "") or ""
        try:
            dt = datetime.strptime(created[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=BRT)
            dia = dt.strftime("%d/%m")
        except:
            dia = "??"

        discount_str = p.get("order_discount", "") or ""
        valor = float(p.get("ticket_sale_price", 0) or 0)
        ticket_name = p.get("ticket_name", "") or ""
        order_id = p.get("order_id", "")
        approved_orders.add(order_id)
        cupom_pai = extract_cupom_pai(discount_str)
        pct = extract_pct(discount_str)

        # Gratuito = valor 0 ou 100% desconto ou ticket_name com Cortesia
        is_free = (valor == 0 or pct == 100.0 or
                   "cortesia" in ticket_name.lower() or
                   "convite" in ticket_name.lower())

        if is_free:
            total_cort += 1
            cat = classify_cortesia(cupom_pai, ticket_name) or "Outros (Gratuitos)"
            key = cupom_pai or ticket_name or "Sem código"
            # Para campanhas, usar subcategoria como key
            if cat == "Campanhas":
                sub = get_campanha_sub(cupom_pai) or key
                cortesias[cat][sub] += 1
            else:
                cortesias[cat][key] += 1
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

    for o in all_orders:
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

    return by_day, by_origin, total, dict(cortesias), dict(parceiros), total_cort


def process_convite(all_participants):
    """Participantes com cupom 'Convite' em qualquer dos dois eventos."""
    convite = [p for p in all_participants
               if "convite" in (p.get("order_discount") or "").lower()
               or "convite" in (p.get("ticket_name") or "").lower()]

    total = len(convite)
    empresas = Counter()
    cargos = Counter()
    cidades = Counter()
    faixas = Counter()
    generos = Counter()
    clevel_count = 0

    for p in convite:
        empresa = get_form_field(p, "Empresa/Instituição") or "Não informado"
        cargo   = get_form_field(p, "Ocupação") or "Não informado"
        cidade  = get_form_field(p, "Cidade/Estado") or "Não informado"
        faixa   = get_form_field(p, "Faixa Etária") or "Não informado"
        genero  = get_form_field(p, "Gênero") or "Não informado"

        empresas[empresa] += 1
        cargos[cargo] += 1
        cidades[cidade] += 1
        faixas[faixa] += 1
        generos[genero] += 1
        if is_clevel(cargo):
            clevel_count += 1

    return {
        "total": total,
        "clevel": clevel_count,
        "clevel_pct": round(clevel_count / total * 100, 1) if total else 0,
        "top_empresas": [{"nome": k, "n": v} for k, v in empresas.most_common(10)],
        "top_cargos":   [{"nome": k, "n": v} for k, v in cargos.most_common(10)],
        "top_cidades":  [{"nome": k, "n": v} for k, v in cidades.most_common(10)],
        "faixas":       [{"nome": k, "n": v} for k, v in sorted(faixas.items())],
        "generos":      [{"nome": k, "n": v} for k, v in generos.most_common()],
    }


def fmt_brl(v):
    s = f"{v:,.0f}".replace(",", ".")
    return f"R$ {s}"


def generate_html(by_day, by_origin, total, cortesias, parceiros, total_cort, convite_data):
    now = datetime.now(BRT)
    ts = now.strftime("%d/%m/%Y · %Hh%M")
    dias = sorted(by_day.keys(), key=lambda d: datetime.strptime(d, "%d/%m"))
    ndias = len(dias)
    rec_conf = sum(by_origin[c]["r"] for c in CUPONS)
    taxa = round(total["c"] / total["t"] * 100) if total["t"] else 0
    total_geral = total["t"] + total_cort

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
    html = html.replace("__TIMESTAMP__",       ts)
    html = html.replace("__TOTAL__",           str(total["t"]))
    html = html.replace("__TOTAL_GERAL__",     str(total_geral))
    html = html.replace("__TOTAL_CORT__",      str(total_cort))
    html = html.replace("__CONF__",            str(total["c"]))
    html = html.replace("__PEND__",            str(total["p"]))
    html = html.replace("__TAXA__",            str(taxa))
    receita_num = f"{int(rec_conf):,}".replace(",", ".")
    ticket = str(round(rec_conf / total["c"])) if total["c"] else "0"
    html = html.replace("__RECEITA__",         fmt_brl(rec_conf))
    html = html.replace("__RECEITA_NUM__",     receita_num)
    html = html.replace("__TICKET__",          ticket)
    html = html.replace("__NDIAS__",           str(ndias))
    html = html.replace("__DIAS_JSON__",       json.dumps(dias, ensure_ascii=False))
    html = html.replace("__BY_DAY_JSON__",     json.dumps(by_day, ensure_ascii=False))
    html = html.replace("__ORIG_JSON__",       json.dumps(orig_data, ensure_ascii=False))
    html = html.replace("__CUPONS_JSON__",     json.dumps(CUPONS, ensure_ascii=False))
    html = html.replace("__COLORS_JSON__",     json.dumps(COLORS))
    html = html.replace("__CORTESIAS_JSON__",  json.dumps(cortesias_data, ensure_ascii=False))
    html = html.replace("__PARCEIROS_JSON__",  json.dumps(parceiros_data, ensure_ascii=False))
    html = html.replace("__CAT_COLORS_JSON__", json.dumps(CORTESIA_COLORS))
    html = html.replace("__CONVITE_JSON__",    json.dumps(convite_data, ensure_ascii=False))
    return html


if __name__ == "__main__":
    all_participants = []
    all_orders = []

    for eid in EVENT_IDS:
        print(f"Buscando participantes evento {eid}...")
        p = get_participants(eid)
        print(f"  → {len(p)} participantes")
        all_participants.extend(p)

        print(f"Buscando pedidos evento {eid}...")
        o = get_orders(eid)
        print(f"  → {len(o)} pedidos")
        all_orders.extend(o)

    print(f"\nTotal combinado: {len(all_participants)} participantes, {len(all_orders)} pedidos")

    by_day, by_origin, total, cortesias, parceiros, total_cort = process(all_participants, all_orders)
    convite_data = process_convite(all_participants)

    total_cort_n = sum(sum(c.values()) for c in cortesias.values())
    total_parc   = sum(v["count"] for v in parceiros.values())
    print(f"Vendas: {total['t']} | Cortesias: {total_cort_n} | Parceiros: {total_parc}")
    print(f"Convite: {convite_data['total']} | C-level: {convite_data['clevel_pct']}%")

    print("\n=== CORTESIAS POR CATEGORIA ===")
    for cat, cupons in cortesias.items():
        print(f"  {cat}: {sum(cupons.values())} → {sorted(cupons.items(), key=lambda x: -x[1])[:5]}")

    print("\n=== PARCEIROS COM DESCONTO ===")
    for cupom, v in sorted(parceiros.items(), key=lambda x: -x[1]["count"]):
        print(f"  {cupom}: {v['count']}x @ {v['pct']}% off")

    html = generate_html(by_day, by_origin, total, cortesias, parceiros, total_cort, convite_data)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\nindex.html gerado com sucesso!")
