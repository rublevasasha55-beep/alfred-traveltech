"""Visual language shared with the Landing Monitor learning project.
An independent, light fintech-inspired UI, not an official bank product.
"""
from html import escape
import streamlit as st

INK = "#202328"
SUB = "#737D8D"
YELLOW = "#FFDD2D"
BG = "#F7F8FA"
GREEN = "#22A77A"
RED = "#F36C65"

ICON_PATHS = {
    "home": '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
    "layers": '<path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7.07-7.07l-1.7 1.71"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7.07 7.07l1.7-1.71"/>',
    "pulse": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "activity": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M5 12h4l2-4 3 8 2-4h3"/>',
    "alert": '<path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "bolt": '<path d="m13 2-9 12h7l-1 8 10-13h-7l0-7Z"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><path d="M12 7h.01"/>',
    "search": '<circle cx="10.5" cy="10.5" r="7.5"/><path d="m16 16 5 5"/>',
    "bell": '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/>',
    "monitor": '<rect x="2" y="4" width="20" height="15" rx="2"/><path d="M8 22h8M12 19v3"/>',
    "mobile": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>',
    "code": '<path d="m8 5-6 7 6 7M16 5l6 7-6 7"/>',
    "arrow": '<path d="M4 12h15m-6-6 6 6-6 6"/>',
    "external": '<path d="M12 4h8v8M20 4l-9 9"/><path d="M20 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h5"/>',
    "filter": '<path d="M4 7h16M7 12h10M10 17h4"/>',
    "shield": '<path d="M12 2 20 6v6c0 5-3 8-8 10-5-2-8-5-8-10V6z"/><path d="m9 12 2 2 4-4"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 2 4 3 9 3s9-1 9-3V5M3 12c0 2 4 3 9 3s9-1 9-3"/>',
    "file": '<path d="M5 2h9l5 5v15H5z"/><path d="M14 2v5h5M8 12h8M8 16h8"/>',
}

ICON_PATHS.update({
    "plane": '<path d="m22 2-9 20-3-9-8-3L22 2Z"/><path d="M22 2 10 13"/>',
    "route": '<circle cx="6" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><path d="M8 6h8c6 0 6 10 0 10H8"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
    "users": '<circle cx="9" cy="8" r="4"/><path d="M2 21v-2a7 7 0 0 1 14 0v2M16 4a4 4 0 0 1 0 8M18 15a6 6 0 0 1 4 6"/>',
    "wifi-off": '<path d="M2 2l20 20M5 9a15 15 0 0 1 15-1M8 13a10 10 0 0 1 7-1M12 19h.01"/>',
    "refresh": '<path d="M20 7v6h-6M4 17v-6h6"/><path d="M5 10a8 8 0 0 1 14-3M19 14a8 8 0 0 1-14 3"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>',
})


def icon(name, size=20, color="currentColor"):
    path = ICON_PATHS.get(name, ICON_PATHS["info"])
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'


def h(value):
    return escape(str(value), quote=True)

STYLE = """<style>

@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --yellow:#ffdd2d;--ink:#202328;--muted:#737d8d;--base:#f7f8fa;--soft:#f0f2f5;}
html,body,.stApp,button,input,textarea,select,[data-testid="stMarkdownContainer"] {font-family:'Manrope',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif!important}
.stApp {background:var(--base);color:var(--ink)}
.block-container {max-width:1580px;padding:1.25rem 2.0rem 2.2rem 2.0rem;}
header[data-testid="stHeader"] {display:none!important} #MainMenu, footer{display:none!important}
[data-testid="stSidebar"] {background:#fff;border:0!important;box-shadow:7px 0 35px rgba(33,36,44,.035);width:252px!important;min-width:252px!important;max-width:252px!important}
[data-testid="stSidebar"] > div {width:252px!important}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {padding:1.5rem 1.05rem}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {display:none}
[data-testid="stSidebar"] hr {border-color:#edf0f3}
[data-testid="stAppViewContainer"] > .main {background:var(--base)}
[data-testid="stDecoration"] {display:none}
h1,h2,h3 {font-weight:800!important;color:var(--ink)!important;letter-spacing:-.035em}
h1 {font-size:32px!important;} h2{font-size:23px!important} h3{font-size:17px!important}
/* Top navigation and header */
.brand {display:flex;align-items:center;gap:12px;padding:5px 8px 5px 8px}
.brandmark {display:flex;align-items:center;justify-content:center;width:43px;height:43px;background:var(--yellow);border-radius:13px;color:#222;font-size:25px;font-weight:900;box-shadow:0 5px 12px rgba(255,221,45,.2)}
.brandcopy b {font-size:16px;letter-spacing:-.045em;color:#1b1d22}
.brandcopy small {display:block;font-size:10px;color:#8991a0;margin-top:4px;letter-spacing:-.01em}
.nav-heading {padding:27px 13px 8px;color:#9aa2af;font-size:10px;font-weight:800;letter-spacing:.13em;text-transform:uppercase}
.nav-link {display:flex;align-items:center;gap:13px;padding:12px 14px;margin:3px 0;border-radius:13px;color:#31343b;text-decoration:none!important;font-size:13px;font-weight:650;transition:background .18s,color .18s}
.nav-link svg{flex:none} .nav-link:hover {background:#f6f7f9;color:#111!important}
.nav-link.active{background:#fff2b3;color:#24262b;font-weight:800}
.nav-link.active svg{color:#1f2125}
.sidemeta {margin-top:31px;padding:17px 15px;border-radius:15px;background:#f6f7f9;font-size:11px;line-height:1.65;color:#727b89}
.sidemeta b{font-size:11px;color:#34383f}.sidemeta .smallnote{margin-top:7px;color:#8d95a1}
.tophead {display:flex;align-items:center;justify-content:space-between;padding:4px 0 13px;gap:14px}
.tophead-left{color:#9299a4;font-size:10px;font-weight:850;letter-spacing:.13em;text-transform:uppercase}
.tophead-right{display:flex;align-items:center;gap:10px}
.top-icon{height:32px;width:32px;border-radius:50%;display:grid;place-items:center;background:white;box-shadow:0 3px 9px rgba(30,35,40,.04)}
.avatar{height:33px;width:33px;border-radius:50%;display:grid;place-items:center;background:#26272b;color:#fff;font-size:11px;font-weight:800}
.hero {position:relative;overflow:hidden;border-radius:22px;padding:20px 28px 23px;margin-bottom:16px;background:#fff;box-shadow:0 6px 25px rgba(25,30,40,.045)}
.hero::before{content:'';position:absolute;right:-35px;top:-88px;height:245px;width:330px;border-radius:49% 51% 52% 48%;transform:rotate(-23deg);background:linear-gradient(135deg,#fff9d5,#ffe277 52%,#fff 94%);opacity:.85}
.hero::after{content:'';position:absolute;right:80px;top:64px;height:160px;width:280px;border-radius:80% 10% 10% 70%;transform:rotate(-12deg);background:linear-gradient(45deg,rgba(255,217,50,.45),rgba(255,249,202,.05));opacity:.9}
.hero h1,.hero p,.hero .eyebrow{position:relative;z-index:1;max-width:80%}
.hero .eyebrow{font-size:10px;font-weight:850;color:#8992a0;letter-spacing:.13em;text-transform:uppercase}
.hero h1{font-size:31px!important;line-height:1.25;margin:8px 0 6px}
.hero p{font-size:12px;color:#727b87;line-height:1.55;margin:0}
/* Streamlit input row styled as light pill controls */
[data-testid="stSelectbox"] label,[data-testid="stTextInput"] label {font-size:11px!important;font-weight:750!important;color:#6e7785!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stTextInput"] input{border-radius:12px!important;border:1px solid #e7ebef!important;background:#fff!important;min-height:40px!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div:hover{border-color:#d3d8de!important}
.stButton button,[data-testid="stFormSubmitButton"] button{border-radius:12px!important;font-weight:800!important;min-height:41px!important;}
.stButton button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"]{background:#ffdd2d!important;color:#22252a!important;border:0!important}
.stButton button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] button[kind="primary"]:hover{background:#ffd21a!important}
.stButton button[kind="secondary"]{background:white;border:1px solid #e6e9ef}
/* Global cards */
.kpi {background:#fff;box-shadow:0 8px 26px rgba(30,35,45,.055);border-radius:18px;padding:17px 17px 15px;min-height:119px}
.kpi-top{display:flex;align-items:center;justify-content:space-between;gap:8px}
.kpi-label{font-size:10px;font-weight:750;color:#79828e;line-height:1.4}
.kpi-icon {display:grid;place-items:center;flex:none;width:35px;height:35px;border-radius:12px;background:#fff8da;color:#2b2d31}
.kpi-value{font-size:29px;line-height:1.25;font-weight:850;letter-spacing:-.055em;margin:7px 0 1px;color:#202328}
.kpi-desc{font-size:10px;color:#8d95a0;line-height:1.35}
.chart-title{font-size:15px;font-weight:850;letter-spacing:-.025em;color:#202328;margin-bottom:2px}
.chart-subtitle{font-size:10px;color:#929aa7;margin-bottom:2px}
/* Panels wrap native plotly and data widgets, avoiding fake drawings */
div[data-testid="column"]:has(.chart-title){background:#fff;border-radius:19px;padding:18px 20px 10px;box-shadow:0 8px 25px rgba(26,30,42,.045);min-width:0}
div[data-testid="column"]:has(.lower-panel-title){background:#fff;border-radius:19px;padding:16px 17px 12px;box-shadow:0 8px 25px rgba(26,30,42,.045);min-width:0}
.lower-panel-title{font-weight:850;font-size:14px;color:#252830;letter-spacing:-.018em;margin-bottom:10px}
.section-title{display:flex;align-items:center;justify-content:space-between;margin:18px 0 10px;font-size:14px;font-weight:850;letter-spacing:-.023em;color:#262a30}
.section-title a{font-size:11px;letter-spacing:normal;color:#6f7783;text-decoration:none;font-weight:700}
.section-title a:hover{color:#222}
.demo-note{display:flex;gap:8px;align-items:center;background:#fff7db;color:#6d6243;border-radius:12px;margin-bottom:15px;padding:9px 14px;font-size:11px}
.status-row{display:flex;gap:2px;overflow:hidden;border-radius:14px;height:20px;margin:18px 0 14px;background:#f4f5f6}
.status-row span{display:block;flex-shrink:0}
.legenditem{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #f1f3f5;color:#59616d;font-size:11px}
.legenditem:last-child{border:0}.legenditem b{margin-left:auto;color:#30353b}
.legenddot{width:9px;height:9px;border-radius:50%;display:inline-block}
.incident-line{display:flex;align-items:center;gap:11px;background:#f9fafb;padding:11px 12px;border-radius:13px;margin:7px 0}
.incicon{width:35px;height:35px;border-radius:11px;display:grid;place-items:center;flex-shrink:0}
.incbody{flex:1;min-width:0}.incbody b{font-size:11px;color:#262930;display:block}.incbody small{color:#89919c;font-size:9px;display:block;margin-top:3px}
.tag{font-size:9px;padding:5px 8px;border-radius:999px;white-space:nowrap;font-weight:750}
.tag-error{background:#ffecea;color:#c14c42}.tag-warning{background:#fff3dc;color:#aa7517}.tag-ok{background:#e4f7ee;color:#168b5a}
.platformgrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.platform{display:flex;gap:7px;align-items:center;background:#f6f7f9;border-radius:12px;padding:9px;color:#343940;font-size:10px;font-weight:700}
.platform .right{margin-left:auto;color:#738191;font-size:9px;font-weight:550}
.risk-feature{background:#fff;box-shadow:0 8px 26px rgba(30,35,45,.055);border-radius:18px;padding:16px 19px;border-left:4px solid #ffdd2d;margin:12px 0}
.risk-feature b{font-size:14px;color:#252830}.risk-feature p{font-size:11px;color:#727b89;line-height:1.5;margin:5px 0 3px}
.risk-number{font-weight:850;font-size:27px;letter-spacing:-.04em;color:#202328}
.risk-mono{font-variant-numeric:tabular-nums}
.mini-checks{width:100%;border-collapse:collapse;font-size:10px}
.mini-checks th{text-align:left;color:#8b93a0;font-weight:700;padding:8px 7px;border-bottom:1px solid #f0f2f4}
.mini-checks td{padding:10px 7px;border-bottom:1px solid #f3f4f6;color:#343942}
.mini-checks tr:last-child td{border-bottom:0}
.quick-hint{color:#8c95a1;font-size:10px;line-height:1.6;margin:6px 0 12px}
.minibadge{font-size:9px;background:#fff6dc;color:#8f6e13;border-radius:7px;padding:3px 7px}
[data-testid="stDataFrame"]{border-radius:14px;overflow:hidden}
[data-testid="stMetric"]{background:#fff;padding:12px 14px;border-radius:14px}
[data-testid="stAlert"]{border-radius:14px}
[data-testid="stExpander"]{border:1px solid #eceef2!important;border-radius:12px!important;background:#fff}
.stCaption,.stMarkdown p{line-height:1.6}
@media(max-width:1100px){.block-container{padding-left:1.3rem;padding-right:1.3rem}.kpi{padding:14px 12px;min-height:110px}.kpi-value{font-size:24px}.kpi-label{font-size:9px}}
@media(max-width:720px){.block-container{padding:1rem}.hero{padding:22px}.hero h1{font-size:24px!important}.hero:before,.hero:after{opacity:.28}}
/* Alfred travel prototype additions */
.kpi {min-height:118px}
.flight-line{display:flex;align-items:center;gap:12px;padding:15px 16px;background:#f9fafb;border-radius:14px;margin:8px 0}
.flight-line .flight-icon{display:grid;place-items:center;border-radius:12px;background:#fff3c3;width:40px;height:40px;flex:none}
.flight-line .flight-text{flex:1;min-width:0}.flight-line .flight-text b{font-size:12px;color:#202328}
.flight-line .flight-text small{display:block;font-size:10px;color:#87909e;margin-top:4px}
.flight-pick{font-size:10px;font-weight:800;background:#eff8f3;color:#17855d;padding:6px 9px;border-radius:999px}
.insight {border-left:4px solid #ffdd2d;background:#fff;border-radius:15px;padding:15px 18px;margin:12px 0;box-shadow:0 8px 28px rgba(25,30,40,.04)}
.insight b{font-size:13px;color:#202328}.insight p{color:#717a88;font-size:11px;margin:8px 0 0;line-height:1.55}
.status-pill{padding:5px 9px;border-radius:999px;background:#fff2d9;color:#976616;font-size:10px;font-weight:800}
.status-pill.critical{background:#fff0ed;color:#bc483c}
.status-pill.ok{background:#e5f7eb;color:#1c8b5c}
[data-testid="stVerticalBlock"]{gap:.7rem}
[data-testid="stDataFrame"] {background:white;border-radius:12px}
div[data-testid="column"]:has(.panel-inside){background:#fff;border-radius:18px;padding:18px 19px 10px;box-shadow:0 7px 24px rgba(26,30,42,.044);min-width:0}
div[data-testid="column"]:has(.plain-column){background:none!important;box-shadow:none!important;padding:0!important}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:#fff!important;border:1px solid #e7ebef!important;border-radius:11px!important}

</style>"""


def apply_style():
    st.markdown(STYLE, unsafe_allow_html=True)
    if st.query_params.get("capture", "0") == "1":
        st.markdown("<style>[data-testid='stToolbar']{display:none!important}</style>", unsafe_allow_html=True)


def sidebar(current_page, pages):
    with st.sidebar:
        st.markdown('<div class="brand"><div class="brandmark">A</div><div class="brandcopy"><b>Альфред</b><small>Помощник в путешествиях</small></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-heading">Путешествие и сценарии</div>', unsafe_allow_html=True)
        links = []
        for page_id, title, symbol in pages:
            cls=' active' if current_page == page_id else ''
            links.append(f'<a class="nav-link{cls}" href="?view={page_id}">{icon(symbol,18)}<span>{h(title)}</span></a>')
        st.markdown(''.join(links), unsafe_allow_html=True)
        st.markdown('<div class="sidemeta">'+icon('shield',17,'#958029')+' <b>Учебный сценарий</b><br>Статусы, тарифы, маршруты и поставщики вымышлены.<div class="smallnote">Паспортные данные не используются. Бронирования и платежи не выполняются.</div></div>', unsafe_allow_html=True)


def shell(section, title, subtitle):
    st.markdown('<div class="tophead"><div class="tophead-left">Альфред / TravelTech / Демо API</div><div class="tophead-right"><span class="top-icon">'+icon('bell',17)+'</span><span class="avatar">AF</span></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero"><div class="eyebrow">{h(section)}</div><h1>{h(title)}</h1><p>{h(subtitle)}</p></div>', unsafe_allow_html=True)


def kpi(label, value, foot, symbol):
    st.markdown('<div class="kpi"><div class="kpi-top"><span class="kpi-label">'+h(label)+'</span><span class="kpi-icon">'+icon(symbol,19,INK)+'</span></div><div class="kpi-value">'+h(value)+'</div><div class="kpi-desc">'+h(foot)+'</div></div>',unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="chart-title">{h(title)}</div><div class="chart-subtitle">{h(sub)}</div>',unsafe_allow_html=True)


def note(text):
    st.markdown('<div class="demo-note">'+icon('info',15)+' '+h(text)+'</div>',unsafe_allow_html=True)


def insight(title, message):
    st.markdown(f'<div class="insight"><b>{h(title)}</b><p>{h(message)}</p></div>',unsafe_allow_html=True)
