"""
☪ Salat Lumière — Horaires de prière : Lausanne & Casablanca
Lancer :  streamlit run app.py
Dépendances :  pip install streamlit requests pandas tzdata   (streamlit >= 1.37)
"""
import math
import random
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Salat Lumière", page_icon="🌙", layout="wide")

# ───────────────────────────── Données ─────────────────────────────
CITIES = {
    "Lausanne": {"country": "Switzerland", "flag": "🇨🇭", "method": 3, "tz": "Europe/Zurich",
                 "tag": "Perle du Léman"},
    "Casablanca": {"country": "Morocco", "flag": "🇲🇦", "method": 21, "tz": "Africa/Casablanca",
                   "tag": "La Ville Blanche"},
}
METHODS = {
    "Ligue Islamique Mondiale": 3,
    "Ministère des Habous (Maroc)": 21,
    "UOIF (France/Europe)": 12,
    "Umm al-Qura (La Mecque)": 4,
    "ISNA (Amérique du Nord)": 2,
}
PRAYERS = [
    ("Fajr", "Fajr", "🌅", "Aube", "#a18cd1", "#fbc2eb"),
    ("Sunrise", "Chourouq", "☀️", "Lever du soleil", "#f6d365", "#fda085"),
    ("Dhuhr", "Dhuhr", "🌤️", "Midi", "#84fab0", "#8fd3f4"),
    ("Asr", "Asr", "🌇", "Après-midi", "#fccb90", "#d57eeb"),
    ("Maghrib", "Maghrib", "🌆", "Coucher du soleil", "#ff9a9e", "#fecfef"),
    ("Isha", "Isha", "🌙", "Nuit", "#89f7fe", "#66a6ff"),
]
KAABA = (21.4225, 39.8262)
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
ADHKAR = [
    ("سُبْحَانَ اللَّهِ وَبِحَمْدِهِ", "Gloire et louange à Allah.", "100 fois par jour : les péchés sont effacés."),
    ("لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ", "Il n'y a de force ni de puissance qu'en Allah.", "Un trésor du Paradis."),
    ("أَسْتَغْفِرُ اللَّهَ وَأَتُوبُ إِلَيْهِ", "Je demande pardon à Allah et me repens à Lui.", "Le Prophète ﷺ le disait plus de 70 fois par jour."),
    ("اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ", "Ô Allah, prie sur Muhammad.", "Chaque prière sur lui en vaut dix d'Allah sur vous."),
    ("رَبِّ اشْرَحْ لِي صَدْرِي وَيَسِّرْ لِي أَمْرِي", "Seigneur, ouvre-moi ma poitrine et facilite-moi ma tâche.", "Invocation de Moussa (Moïse) ﷺ."),
    ("حَسْبِيَ اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ", "Allah me suffit, il n'y a de dieu que Lui.", "7 fois matin et soir."),
    ("رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً", "Seigneur, donne-nous belle part ici-bas et dans l'au-delà.", "L'invocation la plus fréquente du Prophète ﷺ."),
]

# ───────────────────────────── Style ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Amiri:wght@400;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Poppins', sans-serif; }
.stApp {
  background: linear-gradient(135deg, #ffe3ec 0%, #fff1e0 22%, #e4f7ee 48%, #dcecff 74%, #ece0ff 100%);
  background-attachment: fixed;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; max-width: 1200px; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,.85), rgba(240,230,255,.85));
  backdrop-filter: blur(14px);
}
h1,h2,h3,h4,p,span,label,div { color: #3b3556; }

.hero {
  position: relative; overflow: hidden; border-radius: 32px; padding: 34px 40px; margin-bottom: 22px;
  background: linear-gradient(120deg, #ff9a9e 0%, #fad0c4 25%, #fbc2eb 50%, #a6c1ee 78%, #84fab0 100%);
  box-shadow: 0 20px 50px rgba(166,120,200,.30);
}
.hero::before, .hero::after { content:""; position:absolute; border-radius:50%; background:rgba(255,255,255,.35); }
.hero::before { width:280px; height:280px; right:-60px; top:-90px; }
.hero::after  { width:180px; height:180px; right:180px; bottom:-90px; background:rgba(255,255,255,.25); }
.hero h1 { font-weight:800; font-size:2.5rem; margin:0; color:#fff; text-shadow:0 3px 14px rgba(120,60,150,.35); }
.hero .sub { color:#fff; font-size:1.05rem; opacity:.95; margin-top:6px; }
.hero .chips span {
  display:inline-block; margin:14px 8px 0 0; padding:6px 16px; border-radius:99px; font-size:.85rem; font-weight:500;
  background:rgba(255,255,255,.55); backdrop-filter:blur(8px); color:#5a3a78;
}
.glass {
  background: rgba(255,255,255,.62); backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,.85); border-radius: 26px; padding: 22px 26px;
  box-shadow: 0 10px 34px rgba(150,120,200,.16); margin-bottom: 18px;
}
.next {
  border-radius: 30px; padding: 30px 36px; margin-bottom: 20px; text-align:center;
  background: linear-gradient(135deg, #ffffffcc, #ffffff88);
  border: 1px solid #fff; box-shadow: 0 14px 40px rgba(120,150,230,.22);
}
.next .lbl { letter-spacing:.2em; font-size:.75rem; font-weight:600; color:#9a7fbf; text-transform:uppercase; }
.next .nm { font-size:1.9rem; font-weight:700; background:linear-gradient(90deg,#ff758c,#a18cd1,#4facfe);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.next .cd { font-size:4rem; font-weight:800; font-variant-numeric:tabular-nums; line-height:1.1;
  background:linear-gradient(90deg,#ff9a9e,#a18cd1,#5ee7df); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.pgrid { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:16px; margin-bottom:18px; }
.pcard {
  border-radius:26px; padding:20px 16px; text-align:center; color:#fff; position:relative;
  transition:transform .25s ease, box-shadow .25s ease; box-shadow:0 10px 26px rgba(0,0,0,.10);
}
.pcard:hover { transform:translateY(-6px) scale(1.02); box-shadow:0 18px 38px rgba(0,0,0,.16); }
.pcard .ic { font-size:2rem; }
.pcard .nm { font-weight:700; font-size:1.05rem; color:#fff; }
.pcard .ds { font-size:.72rem; opacity:.9; color:#fff; }
.pcard .tm { font-size:2rem; font-weight:800; margin-top:6px; color:#fff; text-shadow:0 2px 8px rgba(0,0,0,.15); }
.pcard.now { outline:4px solid #fff; box-shadow:0 0 0 7px rgba(255,255,255,.45), 0 18px 40px rgba(120,80,200,.35); }
.pcard .badge { position:absolute; top:10px; right:12px; background:#fff; color:#7b52c9; font-size:.62rem;
  font-weight:700; padding:2px 9px; border-radius:99px; }
.night { border-radius:28px; padding:26px; text-align:center; color:#fff;
  background:linear-gradient(135deg,#8ec5fc 0%,#e0c3fc 100%); box-shadow:0 14px 36px rgba(140,130,230,.35); }
.night .big { font-size:3rem; font-weight:800; color:#fff; }
.night div,.night span { color:#fff; }
.bar { display:flex; height:46px; border-radius:23px; overflow:hidden; box-shadow:inset 0 2px 8px rgba(0,0,0,.08); margin:14px 0 8px; }
.bar div { display:flex; align-items:center; justify-content:center; color:#fff; font-weight:600; font-size:.85rem; }
.arabic { font-family:'Amiri',serif; font-size:2rem; direction:rtl; color:#6a4c9c; line-height:1.9; }
.pill { display:inline-block; padding:5px 14px; border-radius:99px; margin:3px 4px 3px 0; font-size:.82rem; font-weight:600;
  background:linear-gradient(90deg,#fbc2eb,#a6c1ee); color:#4b3a78; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { background:rgba(255,255,255,.6); border-radius:99px; padding:8px 20px; font-weight:600; }
.stTabs [aria-selected="true"] { background:linear-gradient(90deg,#ff9a9e,#a18cd1) !important; }
.stTabs [aria-selected="true"] p { color:#fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }
.stButton>button, .stDownloadButton>button {
  border:none; border-radius:99px; font-weight:600; color:#fff; padding:.5rem 1.4rem;
  background:linear-gradient(90deg,#ff9a9e,#a18cd1,#5ee7df); transition:transform .2s;
}
.stButton>button:hover, .stDownloadButton>button:hover { transform:scale(1.05); color:#fff; }
.stButton>button p, .stDownloadButton>button p { color:#fff; }
.ring { width:190px; height:190px; border-radius:50%; margin:auto; display:flex; align-items:center; justify-content:center; }
.ring div { width:150px; height:150px; border-radius:50%; background:#fff; display:flex; align-items:center;
  justify-content:center; font-size:2.6rem; font-weight:800; color:#7b52c9; }
</style>
""", unsafe_allow_html=True)


# ───────────────────────────── Fonctions ─────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_day(city: str, country: str, d: str, method: int, school: int):
    r = requests.get(f"https://api.aladhan.com/v1/timingsByCity/{d}",
                     params={"city": city, "country": country, "method": method, "school": school}, timeout=15)
    r.raise_for_status()
    return r.json()["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_month(city: str, country: str, year: int, month: int, method: int, school: int):
    r = requests.get(f"https://api.aladhan.com/v1/calendarByCity/{year}/{month}",
                     params={"city": city, "country": country, "method": method, "school": school}, timeout=20)
    r.raise_for_status()
    return r.json()["data"]


def to_dt(day: date, hhmm: str, tz: ZoneInfo) -> datetime:
    h, m = hhmm.strip()[:5].split(":")
    return datetime(day.year, day.month, day.day, int(h), int(m), tzinfo=tz)


def fmt_td(td: timedelta) -> str:
    s = max(int(td.total_seconds()), 0)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def fmt_dur(td: timedelta) -> str:
    m = int(td.total_seconds() // 60)
    return f"{m // 60} h {m % 60:02d} min"


def qibla_bearing(lat, lon):
    p1, p2 = math.radians(lat), math.radians(KAABA[0])
    dl = math.radians(KAABA[1] - lon)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def distance_kaaba(lat, lon):
    p1, p2 = math.radians(lat), math.radians(KAABA[0])
    dp, dl = p2 - p1, math.radians(KAABA[1] - lon)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def build_ics(city, day, times, tz_name):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Salat Lumiere//FR"]
    for key, label, *_ in PRAYERS:
        h, m = times[key].split(":")
        stamp = f"{day:%Y%m%d}T{int(h):02d}{int(m):02d}00"
        end_m = int(h) * 60 + int(m) + 15
        end = f"{day:%Y%m%d}T{end_m // 60 % 24:02d}{end_m % 60:02d}00"
        lines += ["BEGIN:VEVENT", f"UID:{key}-{city}-{stamp}@salat-lumiere", f"DTSTAMP:{stamp}",
                  f"DTSTART;TZID={tz_name}:{stamp}", f"DTEND;TZID={tz_name}:{end}",
                  f"SUMMARY:🕌 {label} – {city}", "BEGIN:VALARM", "TRIGGER:-PT10M", "ACTION:DISPLAY",
                  f"DESCRIPTION:{label} dans 10 minutes", "END:VALARM", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def load_city(name, day, method, school):
    """Retourne toutes les infos calculées pour une ville."""
    c = CITIES[name]
    d0 = fetch_day(name, c["country"], day.strftime("%d-%m-%Y"), method, school)
    d1 = fetch_day(name, c["country"], (day + timedelta(days=1)).strftime("%d-%m-%Y"), method, school)
    tz = ZoneInfo(d0["meta"]["timezone"])
    t0 = {k: v[:5] for k, v in d0["timings"].items()}
    t1 = {k: v[:5] for k, v in d1["timings"].items()}
    maghrib = to_dt(day, t0["Maghrib"], tz)
    fajr_next = to_dt(day + timedelta(days=1), t1["Fajr"], tz)
    night = fajr_next - maghrib
    return {
        "name": name, "tz": tz, "tz_name": d0["meta"]["timezone"], "t": t0, "t_next": t1,
        "hijri": d0["date"]["hijri"], "lat": d0["meta"]["latitude"], "lon": d0["meta"]["longitude"],
        "maghrib": maghrib, "fajr_next": fajr_next, "night": night,
        "mid": maghrib + night / 2, "last3": maghrib + night * 2 / 3, "first3": maghrib + night / 3,
    }


def next_prayer(info, day, now):
    for key, label, *_ in PRAYERS:
        dt = to_dt(day, info["t"][key], info["tz"])
        if dt > now:
            return key, label, dt
    return "Fajr", "Fajr", to_dt(day + timedelta(days=1), info["t_next"]["Fajr"], info["tz"])


# ───────────────────────────── Sidebar ─────────────────────────────
with st.sidebar:
    st.markdown("## 🌙 Salat Lumière")
    city = st.radio("Ville", list(CITIES), format_func=lambda n: f"{CITIES[n]['flag']} {n}")
    method_label = st.selectbox("Méthode de calcul", list(METHODS), key=f"m_{city}",
                                index=list(METHODS.values()).index(CITIES[city]["method"]))
    school = st.radio("Asr (école juridique)", [0, 1], horizontal=True,
                      format_func=lambda x: "Chafi'i / Maliki" if x == 0 else "Hanafi")
    tz_city = ZoneInfo(CITIES[city]["tz"])
    day = st.date_input("Date", value=datetime.now(tz_city).date())
    st.caption("Horaires fournis par l'API Aladhan.")

method = METHODS[method_label]
try:
    info = load_city(city, day, method, school)
except Exception as e:
    st.error(f"Impossible de récupérer les horaires ({e}). Vérifie ta connexion internet.")
    st.stop()

c = CITIES[city]
hj = info["hijri"]
hero_date = f"{JOURS[day.weekday()]} {day.day} {MOIS[day.month - 1]} {day.year}"

# ───────────────────────────── Hero ─────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>{c['flag']} {city} — Horaires de prière</h1>
  <div class="sub">{c['tag']} · {hero_date}</div>
  <div class="chips">
    <span>🗓️ {hj['day']} {hj['month']['en']} {hj['year']} H</span>
    <span>🌐 {info['tz_name']}</span>
    <span>📐 {method_label}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ───────────────────────────── Compte à rebours en direct ─────────────────────────────
@st.fragment(run_every=1)
def live_countdown(info, day):
    now = datetime.now(info["tz"])
    key, label, dt = next_prayer(info, day, now)
    st.markdown(f"""
    <div class="next">
      <div class="lbl">Prochaine prière</div>
      <div class="nm">{label} · {dt:%H:%M}</div>
      <div class="cd">{fmt_td(dt - now)}</div>
      <div style="color:#9a7fbf;font-size:.9rem">Heure locale à {info['name']} : {now:%H:%M:%S}</div>
    </div>""", unsafe_allow_html=True)


is_today = day == datetime.now(info["tz"]).date()
if is_today:
    live_countdown(info, day)

# ───────────────────────────── Cartes des prières ─────────────────────────────
now_key = next_prayer(info, day, datetime.now(info["tz"]))[0] if is_today else None
cards = ""
for key, label, icon, desc, c1, c2 in PRAYERS:
    cls = "pcard now" if key == now_key else "pcard"
    badge = '<div class="badge">PROCHAINE</div>' if key == now_key else ""
    cards += (f'<div class="{cls}" style="background:linear-gradient(145deg,{c1},{c2})">{badge}'
              f'<div class="ic">{icon}</div><div class="nm">{label}</div><div class="ds">{desc}</div>'
              f'<div class="tm">{info["t"][key]}</div></div>')
st.markdown(f'<div class="pgrid">{cards}</div>', unsafe_allow_html=True)

# Jeûne conseillé
tips = []
if day.weekday() in (0, 3):
    tips.append("🌿 Lundi/Jeudi : jeûne surérogatoire recommandé")
if int(hj["day"]) in (13, 14, 15):
    tips.append("🌕 Jours Blancs (Ayyam al-Bid) : jeûne recommandé")
if day.weekday() == 4:
    tips.append("🕌 Vendredi : Sourate Al-Kahf & ghusl du Jumu'a")
if hj["month"]["number"] == 10 and int(hj["day"]) == 1:
    tips.append("🎉 Aïd al-Fitr")
if hj["month"]["number"] == 12 and int(hj["day"]) == 10:
    tips.append("🐑 Aïd al-Adha")
if hj["month"]["number"] == 9:
    tips.append("🌙 Ramadan Moubarak !")
if tips:
    st.markdown("".join(f'<span class="pill">{t}</span>' for t in tips), unsafe_allow_html=True)
    st.write("")

# ───────────────────────────── Onglets ─────────────────────────────
tab_night, tab_qibla, tab_month, tab_cmp, tab_track, tab_export = st.tabs(
    ["🌌 Tiers de la nuit", "🧭 Qibla", "📅 Mois", "⚖️ Lausanne vs Casablanca", "✅ Suivi & Tasbih", "📲 Export"])

# ---- Tiers de la nuit
with tab_night:
    n = info["night"]
    st.markdown(f"""
    <div class="night">
      <div style="letter-spacing:.2em;font-size:.8rem">✨ DERNIER TIERS DE LA NUIT ✨</div>
      <div class="big">{info['last3']:%H:%M} → {info['fajr_next']:%H:%M}</div>
      <div>Le moment de la descente divine : invocations, Tahajjud, istighfar.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")
    third = n / 3
    st.markdown(f"""
    <div class="glass">
      <b>Nuit complète : {info['maghrib']:%H:%M} → {info['fajr_next']:%H:%M}</b> (durée {fmt_dur(n)})
      <div class="bar">
        <div style="flex:1;background:linear-gradient(90deg,#f6d365,#fda085)">1er tiers</div>
        <div style="flex:1;background:linear-gradient(90deg,#a18cd1,#fbc2eb)">2e tiers</div>
        <div style="flex:1;background:linear-gradient(90deg,#4facfe,#00f2fe)">Dernier tiers</div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:.85rem;font-weight:600">
        <span>{info['maghrib']:%H:%M}</span><span>{info['first3']:%H:%M}</span>
        <span>{info['last3']:%H:%M}</span><span>{info['fajr_next']:%H:%M}</span>
      </div>
    </div>""", unsafe_allow_html=True)
    a, b, cc = st.columns(3)
    a.metric("🌗 Milieu de la nuit", f"{info['mid']:%H:%M}")
    b.metric("⏳ Durée d'un tiers", fmt_dur(third))
    cc.metric("🕊️ Réveil conseillé (Tahajjud)", f"{info['last3'] + timedelta(minutes=10):%H:%M}")
    if is_today:
        now = datetime.now(info["tz"])
        if info["last3"] <= now <= info["fajr_next"]:
            st.success("🌠 Nous sommes actuellement dans le dernier tiers de la nuit. Profite de ce moment !")
        elif now < info["last3"]:
            st.info(f"Le dernier tiers commence dans {fmt_dur(info['last3'] - now)}.")

# ---- Qibla
with tab_qibla:
    br = qibla_bearing(info["lat"], info["lon"])
    dist = distance_kaaba(info["lat"], info["lon"])
    q1, q2 = st.columns([1, 1])
    with q1:
        st.markdown(f"""
        <div class="glass" style="text-align:center">
          <svg viewBox="-110 -110 220 220" width="280">
            <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#ff9a9e"/><stop offset=".5" stop-color="#a18cd1"/><stop offset="1" stop-color="#5ee7df"/>
            </linearGradient></defs>
            <circle r="100" fill="#fff" stroke="url(#g)" stroke-width="6"/>
            <text y="-82" text-anchor="middle" font-size="13" fill="#7b52c9" font-weight="700">N</text>
            <text y="92" text-anchor="middle" font-size="13" fill="#aaa">S</text>
            <text x="88" y="5" text-anchor="middle" font-size="13" fill="#aaa">E</text>
            <text x="-88" y="5" text-anchor="middle" font-size="13" fill="#aaa">O</text>
            <g transform="rotate({br:.1f})">
              <polygon points="0,-72 10,0 -10,0" fill="url(#g)"/>
              <polygon points="0,50 8,0 -8,0" fill="#e6dcf5"/>
              <text y="-76" text-anchor="middle" font-size="18">🕋</text>
            </g>
            <circle r="7" fill="#fff" stroke="#a18cd1" stroke-width="3"/>
          </svg>
        </div>""", unsafe_allow_html=True)
    with q2:
        st.markdown(f"""
        <div class="glass">
          <h3>Direction de la Qibla à {city}</h3>
          <div style="font-size:3rem;font-weight:800;color:#7b52c9">{br:.1f}°</div>
          <div>depuis le Nord, dans le sens des aiguilles d'une montre.</div>
          <p>📏 Distance jusqu'à la Kaaba : <b>{dist:,.0f} km</b></p>
          <p style="font-size:.85rem">💡 Astuce : pose ton téléphone à plat, oriente le Nord avec une boussole,
          puis tourne de {br:.0f}° vers l'est.</p>
        </div>""".replace(",", " "), unsafe_allow_html=True)

# ---- Mois
with tab_month:
    try:
        rows = fetch_month(city, c["country"], day.year, day.month, method, school)
        df = pd.DataFrame([{
            "Jour": f"{JOURS[datetime.strptime(r['date']['gregorian']['date'], '%d-%m-%Y').weekday()][:3]} "
                    f"{r['date']['gregorian']['day']}",
            "Hijri": f"{r['date']['hijri']['day']} {r['date']['hijri']['month']['en']}",
            **{lbl: r["timings"][k][:5] for k, lbl, *_ in PRAYERS},
        } for r in rows])
        st.markdown(f"#### {MOIS[day.month - 1].capitalize()} {day.year} — {city}")
        st.dataframe(df, hide_index=True, use_container_width=True, height=480)
        st.download_button("⬇️ Télécharger en CSV", df.to_csv(index=False).encode("utf-8"),
                           f"horaires_{city}_{day.year}_{day.month:02d}.csv", "text/csv")
    except Exception as e:
        st.warning(f"Calendrier indisponible : {e}")

# ---- Comparaison
with tab_cmp:
    try:
        a_info = load_city("Lausanne", day, METHODS["Ligue Islamique Mondiale"], school)
        b_info = load_city("Casablanca", day, METHODS["Ministère des Habous (Maroc)"], school)
        rows = []
        for key, label, icon, *_ in PRAYERS:
            ta, tb = a_info["t"][key], b_info["t"][key]
            rows.append({"Prière": f"{icon} {label}", "🇨🇭 Lausanne": ta, "🇲🇦 Casablanca": tb})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        off = (datetime.now(a_info["tz"]).utcoffset() - datetime.now(b_info["tz"]).utcoffset())
        st.markdown(f'<div class="glass">🕰️ Décalage horaire actuel : <b>{int(off.total_seconds() // 3600)} h</b> '
                    f'entre Lausanne et Casablanca.<br>🌌 Dernier tiers — Lausanne : <b>{a_info["last3"]:%H:%M}</b> · '
                    f'Casablanca : <b>{b_info["last3"]:%H:%M}</b></div>', unsafe_allow_html=True)
        st.caption("Chaque ville utilise sa méthode de référence (LIM pour Lausanne, Habous pour Casablanca).")
    except Exception as e:
        st.warning(f"Comparaison indisponible : {e}")

# ---- Suivi & Tasbih
with tab_track:
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("#### ✅ Mes prières du jour")
        done = 0
        for key, label, icon, *_ in PRAYERS:
            if key == "Sunrise":
                continue
            if st.checkbox(f"{icon} {label} — {info['t'][key]}", key=f"trk_{city}_{day}_{key}"):
                done += 1
        pct = int(done / 5 * 100)
        st.markdown(f'<div class="ring" style="background:conic-gradient(#ff9a9e 0 {pct}%,#a18cd1 {pct}%,#e9e2f7 {pct}% 100%)">'
                    f'<div>{done}/5</div></div>', unsafe_allow_html=True)
        if done == 5:
            st.balloons()
            st.success("Machallah, journée complète ! 🌟")
    with t2:
        st.markdown("#### 📿 Tasbih digital")
        st.session_state.setdefault("tasbih", 0)
        target = st.select_slider("Objectif", [33, 99, 100, 300], value=33)
        b1, b2 = st.columns(2)
        if b1.button("➕ Sub'hanAllah", use_container_width=True):
            st.session_state.tasbih += 1
        if b2.button("↺ Remise à zéro", use_container_width=True):
            st.session_state.tasbih = 0
        cnt = st.session_state.tasbih
        st.progress(min(cnt / target, 1.0))
        st.markdown(f'<div style="text-align:center;font-size:3.4rem;font-weight:800;color:#7b52c9">{cnt}'
                    f'<span style="font-size:1.2rem;color:#aaa"> / {target}</span></div>', unsafe_allow_html=True)
        if cnt >= target:
            st.success("Objectif atteint, Baraka Allahu fik ! 🤲")

    idx = (day.toordinal() + (random.Random(day.toordinal()).randint(0, 3))) % len(ADHKAR)
    ar, fr, note = ADHKAR[idx]
    st.markdown(f"""
    <div class="glass" style="text-align:center">
      <div class="lbl" style="letter-spacing:.2em;font-size:.75rem;color:#9a7fbf">✨ DHIKR DU JOUR</div>
      <div class="arabic">{ar}</div><div><b>{fr}</b></div>
      <div style="font-size:.85rem;opacity:.8">{note}</div>
    </div>""", unsafe_allow_html=True)

# ---- Export
with tab_export:
    st.markdown("#### 📲 Ajoute les prières à ton agenda")
    st.write("Fichier .ics avec rappel **10 min avant** chaque prière (Google Agenda, Apple, Outlook…).")
    st.download_button("📅 Télécharger l'agenda du jour",
                       build_ics(city, day, info["t"], info["tz_name"]).encode("utf-8"),
                       f"priere_{city}_{day}.ics", "text/calendar")
    st.markdown("#### 💬 Message à partager")
    txt = f"🕌 Prières à {city} — {hero_date}\n" + "\n".join(
        f"{icon} {label} : {info['t'][k]}" for k, label, icon, *_ in PRAYERS
    ) + f"\n🌌 Dernier tiers de la nuit : {info['last3']:%H:%M}"
    st.code(txt, language=None)

st.markdown("<div style='text-align:center;opacity:.6;padding:24px;font-size:.8rem'>"
            "Fait avec 💜 · Salat Lumière · Vérifie toujours avec ta mosquée locale</div>", unsafe_allow_html=True)
