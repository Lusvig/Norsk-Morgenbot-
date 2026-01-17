import os
import requests
import feedparser
import json
import random
import re
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from functools import wraps
from groq import Groq

# Fjern proxy-innstillinger
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

from dotenv import load_dotenv
load_dotenv()

# Konfigurer logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Miljøvariabler
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BY = os.environ.get("BY", "Moss")

# ============================================================================
# CACHE OPPSETT
# ============================================================================
_cache = {}

def cache_result(ttl_seconds=300):
    """Cache decorator for API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if key in _cache:
                result, timestamp = _cache[key]
                if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            result = func(*args, **kwargs)
            _cache[key] = (result, datetime.now())
            return result
        return wrapper
    return decorator

# ============================================================================
# RETRY LOGIKK
# ============================================================================
def retry_on_failure(max_attempts=3, backoff_factor=1):
    """Retry decorator for API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    wait_time = backoff_factor * (2  ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        return wrapper
    return decorator

# ============================================================================
#  ** OG FERIE- FUNKSJONER (DYNAMISK) **
# ============================================================================
def beregn_paske(year: int) -> Tuple[datetime, datetime]:
    """Beregn påskedager for et gitt år"""
    # Algoritme for påskeberegning (Gregoriansk kalender)
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    
    paske_dag = datetime(year, month, day)
    palmesondag = paske_dag - timedelta(days=7)
    skjaertorsdag = paske_dag - timedelta(days=3)
    langfredag = paske_dag - timedelta(days=2)
    andre_paske_dag = paske_dag + timedelta(days=1)
    
    return paske_dag, palmesondag, skjaertorsdag, langfredag, andre_paske_dag

def beregn_bevegelige_helligdager(year: int) -> Dict[str, str]:
    """Beregn alle bevegelige helligdager for et gitt år"""
    paske_dag, palmesondag, skjaertorsdag, langfredag, andre_paske_dag = beregn_paske(year)
    
    # Kristi himmelfartsdag (39 dager etter påske)
    kristi_himmelfart = paske_dag + timedelta(days=39)
    
    # Første pinsedag (49 dager etter påske)
    forste_pinsedag = paske_dag + timedelta(days=49)
    andre_pinsedag = paske_dag + timedelta(days=50)
    
    return {
        palmesondag.strftime("%Y-%m-%d"): "Palmesøndag",
        skjaertorsdag.strftime("%Y-%m-%d"): "Skjærtorsdag",
        langfredag.strftime("%Y-%m-%d"): "Langfredag",
        paske_dag.strftime("%Y-%m-%d"): "Første påskedag",
        andre_paske_dag.strftime("%Y-%m-%d"): "Andre påskedag",
        kristi_himmelfart.strftime("%Y-%m-%d"): "Kristi himmelfartsdag",
        forste_pinsedag.strftime("%Y-%m-%d"): "Første pinsedag",
        andre_pinsedag.strftime("%Y-%m-%d"): "Andre pinsedag"
    }

def hent_helligdager(year: int) -> Dict[str, str]:
    """Hent alle helligdager for et gitt år"""
    # Faste helligdager
    faste_helligdager = {
        f"{year}-01-01": "Første nyttårsdag",
        f"{year}-05-01": "Arbeidernes dag",
        f"{year}-05-17": "Grunnlovsdagen",
        f"{year}-12-25": "Første juledag",
        f"{year}-12-26": "Andre juledag"
    }
    
    # Bevegelige helligdager
    bevegelige_helligdager = beregn_bevegelige_helligdager(year)
    
    return { **faste_helligdager, **bevegelige_helligdager}

def hent_ferier(year: int) -> Dict[str, Tuple[str, str]]:
    """Hent alle ferier for et gitt år"""
    # Vinterferie (andre uke i februar)
    vinter_ferie_start = datetime(year, 2, 8) + timedelta(days=6)  # Finnes andre mandag i februar
    vinter_ferie_slutt = vinter_ferie_start + timedelta(days=4)
    
    # Påskeferie (komplett uke før påske + uken etter)
    paske_dag, _, _, _, _ = beregn_paske(year)
    paske_ferie_start = paske_dag - timedelta(days=7)  # Mandag før påske
    paske_ferie_slutt = paske_dag + timedelta(days=7)   # Onsdag etter andre påskedag
    
    # Sommerferie (siste uken i juni til midten av august - justert for norske skoler)
    sommer_ferie_start = datetime(year, 6, 20)
    sommer_ferie_slutt = datetime(year, 8, 15)
    
    # Høstferie (første helgen i oktober)
    host_ferie_start = datetime(year, 10, 1)
    while host_ferie_start.weekday() != 0:  # Finn første mandag
        host_ferie_start += timedelta(days=1)
    host_ferie_start += timedelta(days=5)  # Andre uken i oktober
    host_ferie_slutt = host_ferie_start + timedelta(days=4)
    
    # Juleferie (siste uken i desember til første uken i januar)
    jule_ferie_start = datetime(year, 12, 22)
    jule_ferie_slutt = datetime(year + 1, 1, 2) if year < 12 else datetime(year, 1, 2)
    
    return {
        vinter_ferie_start.strftime("%Y-%m-%d"): ("Vinterferie starter", vinter_ferie_slutt.strftime("%Y-%m-%d")),
        paske_ferie_start.strftime("%Y-%m-%d"): ("Påskeferie starter", paske_ferie_slutt.strftime("%Y-%m-%d")),
        sommer_ferie_start.strftime("%Y-%m-%d"): ("Sommerferie starter", sommer_ferie_slutt.strftime("%Y-%m-%d")),
        host_ferie_start.strftime("%Y-%m-%d"): ("Høstferie starter", host_ferie_slutt.strftime("%Y-%m-%d")),
        jule_ferie_start.strftime("%Y-%m-%d"): ("Juleferie starter", jule_ferie_slutt.strftime("%Y-%m-%d"))
    }

def hent_store_hendelser(year: int) -> Dict[str, Tuple[str, str]]:
    """Hent store hendelser for et gitt år"""
    return {
        f"{year}-06-21": ("☀️ Sommeren starter!", "Sommersolverv"),
        f"{year}-12-24": (" ", "Jul"),
        f"{year}-12-31": (" ", "Nyttår"),
        f"{year}-05-10": (" Eurovision 2025", "Super Bowl"),
        f"{year}-07-04": (" Tour de France starter", "Sykkel")
    }

# ============================================================================
# BYER MED KOORDINATER OG KONFIGURERBARE LISTER
# ============================================================================
BY_KOORDINATER = {
    "Moss": {"lat": 59.43, "lon": 10.66, "strompris_sone": "NO1"},
    "Oslo": {"lat": 59.91, "lon": 10.75, "strompris_sone": "NO1"},
    "Bergen": {"lat": 60.39, "lon": 5.32, "strompris_sone": "NO5"},
    "Trondheim": {"lat": 63.43, "lon": 10.39, "strompris_sone": "NO1"},
    "Stavanger": {"lat": 58.97, "lon": 5.73, "strompris_sone": "NO5"},
    "Tromsø": {"lat": 69.65, "lon": 18.96, "strompris_sone": "NO4"},
    "Kristiansand": {"lat": 58.15, "lon": 8.0, "strompris_sone": "NO1"},
    "Drammen": {"lat": 59.74, "lon": 10.22, "strompris_sone": "NO1"},
    "Fredrikstad": {"lat": 59.21, "lon": 10.95, "strompris_sone": "NO1"},
}

# La brukeren legge til egne byer via environment variabler
def utvidede_by_koordinater():
    """Utvid bylisten med brukerdefinerte byer fra environment"""
    custom_cities = os.environ.get("CUSTOM_CITIES")
    if custom_cities:
        try:
            custom_data = json.loads(custom_cities)
            BY_KOORDINATER.update(custom_data)
            logger.info(f"La til {len(custom_data)} egendefinerte byer")
        except json.JSONDecodeError as e:
            logger.error(f"Kunne ikke parse CUSTOM_CITIES: {e}")
    return BY_KOORDINATER

# ============================================================================
# VÆR-FUNKSJONER
# ============================================================================
@retry_on_failure(max_attempts=3)
@cache_result(ttl_seconds=600)  # Cache i 10 minutter
def hent_vaer(by: str) -> Optional[Dict[str, Any]]:
    """Henter værdata fra Yr.no med caching og retry"""
    try:
        by_data = utvidede_by_koordinater().get(by, BY_KOORDINATER["Moss"])
        
        url = f"https://api.met.no/locationforecast/2.0/compact?lat={by_data['lat']}&lon={by_data['lon']}"
        headers = {
            "User-Agent": "Morgenbot/1.0 github.com/username/morgenbot"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        timeseries = data["properties"]["timeseries"]
        
        if not timeseries:
            logger.warning("Ingen værdata tilgjengelig")
            return None
            
        weather_data = timeseries[0]["data"]
        instant = weather_data["instant"]["details"]
        next_1h = weather_data.get("next_1_hours", {})
        next_1h_details = next_1h.get("details", {})
        symbol_code = next_1h.get("summary", {}).get("symbol_code", "fair_day")
        
        temp = instant.get("air_temperature", 0)
        wind_speed = instant.get("wind_speed", 0)
        precipitation = next_1h_details.get("precipitation_amount", 0)
        
        vær_symboler = {
            "clearsky_day": "☀️", "clearsky_night": " ", "clearsky_polartwilight": " ",
            "cloudy": "☁️", "fair_day": " ", "fair_night": " ", "fair_polartwilight": " ",
            "fog": " ", "heavyrain": " ", "heavyrainandthunder": "⛈️", "heavyrainshowers": " ",
            "heavyrainshowersandthunder": "⛈️", "heavysleet": " ", "heavysleetandthunder": "⛈️",
            "heavysleetshowers": " ", "heavysleetshowersandthunder": "⛈️", "heavysnow": "❄️",
            "heavysnowandthunder": "⛈️", "heavysnowshowers": "❄️", "heavysnowshowersandthunder": "⛈️",
            "lightrain": " ", "lightrainandthunder": "⛈️", "lightrainshowers": " ",
            "lightrainshowersandthunder": "⛈️", "lightsleet": " ", "lightsleetandthunder": "⛈️",
            "lightsleetshowers": " ", "lightsnow": "❄️", "lightsnowandthunder": "⛈️",
            "lightsnowshowers": "❄️", "lightssleetshowersandthunder": "⛈️", "lightssnowshowersandthunder": "⛈️",
            "partlycloudy_day": "⛅", "partlycloudy_night": " ", "partlycloudy_polartwilight": " ",
            "rain": " ", "rainandthunder": "⛈️", "rainshowers": " ", "rainshowersandthunder": "⛈️",
            "sleet": " ", "sleetandthunder": "⛈️", "sleetshowers": " ", "sleetshowersandthunder": "⛈️",
            "snow": "❄️", "snowandthunder": "⛈️", "snowshowers": "❄️", "snowshowersandthunder": "⛈️"
        }
        
        temperatur_tekst = (
            f"{temp}°C" if temp > 0 else f"{temp}°C"
        ) if temp <= 5 else f"{temp}°C"
        
        klesanbefaling = "🧥 "
        if temp < -5:
            klesanbefaling += "Varmt undertøy, ullgenser, vinterjakke, lue, votter og varme sko"
        elif temp < 0:
            klesanbefaling += "Ullgenser, varm jakke, lue og votter"
        elif temp < 5:
            klesanbefaling += "Ullgenser eller fleece, vindtett jakke"
        elif temp < 15:
            klesanbefaling += "Langermet skjorte eller lett genser, vindjakke"
        elif temp < 20:
            klesanbefaling += "T-skjorte eller lett langarmet"
        else:
            klesanbefaling += "Lett sommerklær, solbriller"
        
        if precipitation > 0:
            klesanbefaling += ", regntøy og paraply"
        if wind_speed > 15:
            klesanbefaling += ", vindtett bekledning"
        
        strompris = "Ikke tilgjengelig"
        try:
            sone = by_data.get("strompris_sone", "NO1")
            na = datetime.now()
            start = na.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            
            pris_url = f"https://www.hvakosterstrommen.no/api/v1/prices/{sone}_{na.strftime('%Y/%m-%d')}.json"
            pris_response = requests.get(pris_url, headers=headers, timeout=10)
            
            if pris_response.status_code == 200:
                pris_data = pris_response.json()
                if pris_data:
                    snitt_pris = sum(time["NOK_per_kWh"] for time in pris_data) / len(pris_data)
                    naverende_time = na.hour
                    naverende_pris = next(
                        (time["NOK_per_kWh"] for time in pris_data if time["time_start"][:13] == start.strftime("%Y-%m-%dT%H")), 
                        snitt_pris
                    )
                    strompris = f"{naverende_pris:.2f} NOK/kWh (snitt: {snitt_pris:.2f})"
        except Exception as e:
            logger.warning(f"Kunne ikke hente strømpris: {e}")
        
        return {
            "temperatur": temperatur_tekst,
            "symbol": vær_symboler.get(symbol_code, " "),
            "beskrivelse": symbol_code.replace("_", " ").title(),
            "vind": f"{wind_speed:.1f} m/s",
            "nedbør": f"{precipitation:.1f} mm",
            "klesanbefaling": klesanbefaling,
            "strompris": strompris
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Nettverksfeil ved henting av vær: {e}")
        return None
    except Exception as e:
        logger.error(f"Uventet feil ved henting av vær: {e}")
        return None

# ============================================================================
# NYHETS -FUNKSJONER
# ============================================================================
@retry_on_failure(max_attempts=2)
@cache_result(ttl_seconds=900)  # Cache i 15 minutter
def hent_nyheter() -> List[Dict[str, str]]:
    """Henter nyheter fra NRK med caching og retry"""
    try:
        feeds = [
            ("https://www.nrk.no/nyheter/siste.rss", "NRK: Toppsaker"),
            ("https://www.nrk.no/urix/siste.rss", "NRK: Verden"),
            ("https://www.nrk.no/norge/siste.rss", "NRK: Norge")
        ]
        
        alle_nyheter = []
        for url, kategori in feeds:
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    for entry in feed.entries[:3]:
                        alle_nyheter.append({
                            "tittel": entry.title,
                            "link": entry.link,
                            "kategori": kategori
                        })
            except Exception as e:
                logger.warning(f"Feil ved parsing av {kategori}: {e}")
                continue
        
        return alle_nyheter[:6]
        
    except Exception as e:
        logger.error(f"Feil ved henting av nyheter: {e}")
        return [{"tittel": "Kunne ikke laste nyheter", "link": "", "kategori": "Error"}]

# ============================================================================
# ØKONOMI -FUNKSJONER
# ============================================================================
@retry_on_failure(max_attempts=3)
@cache_result(ttl_seconds=900)  # Cache i 15 minutter
def hent_okonomi() -> Dict[str, List]:
    """Henter økonomidata med caching og retry"""
    try:
        # La brukeren konfigurere aksjer via environment variable
        aksjer_config = os.environ.get("KONFIGURER_AKSJER", 
            "^OSEAX,Oslo Børs;EQNR.OL,Equinor;DNB.OL,DNB;TEL.OL,Telenor;MOWI.OL,Mowi;NHY.OL,Norsk Hydro;YAR.OL,Yara")
        
        aksjer = []
        for item in aksjer_config.split(";"):
            if item.strip():
                symbol, navn = item.split(",", 1)
                aksjer.append((symbol.strip(), navn.strip()))
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        aksjer_info = []
        
        for symbol, navn in aksjer:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                result = data["chart"]["result"]
                
                if not result:
                    continue
                
                meta = result[0]["meta"]
                current = meta.get("regularMarketPrice", 0)
                previous = meta.get("previousClose", 0)
                
                if previous > 0:
                    endring = ((current - previous) / previous) * 100
                else:
                    endring = 0
                
                emoji = "📈" if endring >= 0 else "📉"
                endring_str = f"+{endring:.2f}%" if endring >= 0 else f"{endring:.2f}%"
                
                aksjer_info.append({
                    "navn": navn,
                    "pris": current,
                    "endring": endring,
                    "endring_str": endring_str,
                    "emoji": emoji
                })
            
            except Exception as e:
                logger.warning(f"Feil ved henting av {symbol}: {e}")
                continue
        
        # Valutakurser
        valuta = []
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/NOK", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            usd_rate = 1 / data["rates"]["USD"]
            eur_rate = 1 / data["rates"]["EUR"]
            sek_rate = 1 / data["rates"]["SEK"]
            gbp_rate = 1 / data["rates"]["GBP"]
            
            valuta = [
                {"par": "USD/NOK", "kurs": round(usd_rate, 2), "emoji": "💵"},
                {"par": "EUR/NOK", "kurs": round(eur_rate, 2), "emoji": "💶"},
                {"par": "SEK/NOK", "kurs": round(sek_rate, 4), "emoji": "🇸🇪"},
                {"par": "GBP/NOK", "kurs": round(gbp_rate, 2), "emoji": "💷"},
            ]
            
        except Exception as e:
            logger.warning(f"Feil ved henting av valutakurser: {e}")
        
        return {"aksjer": aksjer_info, "valuta": valuta}
    
    except Exception as e:
        logger.error(f"Feil ved henting av økonomidata: {e}")
        return {"aksjer": [], "valuta": []}

@retry_on_failure(max_attempts=2)
@cache_result(ttl_seconds=900)
def hent_krypto() -> List[Dict[str, Any]]:
    """Henter kryptovaluta priser"""
    try:
        coins = ["bitcoin", "ethereum", "solana", "dogecoin", "cardano"]
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins)}&vs_currencies=nok,usd&include_24hr_change=true"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        emoji_map = {
            "bitcoin": "₿", "ethereum": "Ξ", "solana": "◎",
            "dogecoin": "🐕", "cardano": " ",
            "bitcoin-cash": " ", "litecoin": " ", "polkadot": " ",
            "chainlink": " ", "stellar": " ", "vechain": " ", "filecoin": " ",
            "aave": " ", "the-graph": " ", "uniswap": " ", "ftx-token": " ",
            "eos": " ", "tezos": " ", "compound": " ", "sushi": " ", "yearn-finance": " ",
            "maker": " ", "dai": " ", "wrapped-bitcoin": "₿", "paxos-standard": " ",
            "usd-coin": " ", "tether": " ", "tron": " ", "iota": " ", "neo": " "
        }
        
        krypto_info = []
        for coin, info in data.items():
            nok_verdi = info.get("nok", 0)
            usd_verdi = info.get("usd", 0)
            endring_24h = info.get("nok_24h_change", 0)
            
            emoji = emoji_map.get(coin, " ")
            endring_symbol = "📈" if endring_24h >= 0 else "📉"
            endring_str = f"{endring_24h:.1f}%" if endring_24h else "N/A"
            
            krypto_info.append({
                "navn": coin.replace("-", " ").title(),
                "symbol": coin.upper(),
                "pris_nok": nok_verdi,
                "pris_usd": usd_verdi,
                "endring_24h": endring_24h,
                "endring_str": endring_str,
                "emoji": emoji
            })
        
        return krypto_info
    
    except Exception as e:
        logger.error(f"Feil ved henting av kryptodata: {e}")
        return []

# ============================================================================
# DATA OG HENDELSE -FUNKSJONER
# ============================================================================
def hent_naverende_dato() -> datetime:
    """Henter nåværende dato med norsk tidssone"""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/Oslo"))
    except ImportError:
        logger.warning("zoneinfo ikke tilgjengelig, bruker systemtidssone")
        return datetime.now()

def hent_dagens_navn(dato: datetime) -> str:
    """Henter dagens navn på norsk"""
    DAGER = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
    return DAGER[dato.weekday()]

def hent_navnedag(dato: datetime) -> List[str]:
    """Henter navnedager"""
    # Simplifisert versjon - kan utvides med full kalender
    month_day = dato.strftime("%m-%d")
    navn = {
        "01-01": ["Nyttårsdag"],
        "02-14": ["Valentine"],
        "05-01": ["Arbeidernes dag"],
        "05-17": ["Grunnlovsdagen"],
        "12-24": ["Julaften"],
        "12-25": ["Første juledag"],
        "12-26": ["Andre juledag"],
        "12-31": ["Nyttårsaften"]
    }
    return navn.get(month_day, [])

def tell_ned_til_dato(mål_dato: datetime) -> Optional[str]:
    """Tell ned til en spesifikk dato"""
    try:
        idag = hent_naverende_dato()
        if mål_dato.date() <= idag.date():
            return None
        
        dager_igjen = (mål_dato.date() - idag.date()).days
        
        if dager_igjen == 0:
            return "I dag!"
        elif dager_igjen == 1:
            return "I morgen!"
        elif dager_igjen < 7:
            return f"Om {dager_igjen} dager"
        elif dager_igjen < 30:
            uker = dager_igjen // 7
            dager = dager_igjen % 7
            if dager == 0:
                return f"Om {uker} uker"
            else:
                return f"Om {uker} uker og {dager} dager"
        else:
            måneder = dager_igjen // 30
            dager = dager_igjen % 30
            if dager == 0:
                return f"Om {måneder} måneder"
            else:
                return f"Om {måneder} måneder og {dager} dager"
    
    except Exception as e:
        logger.error(f"Feil i nedtelling: {e}")
        return None

def hent_fridager() -> Dict[str, Any]:
    """Henter alle fridager for inneværende år"""
    try:
        idag = hent_naverende_dato()
        år = idag.year
        
        helligdager = hent_helligdager(år)
        ferier = hent_ferier(år)
        hendelser = hent_store_hendelser(år)
        
        alle_fridager = {}
        
        # Legg til helligdager
        for dato_str, navn in helligdager.items():
            alle_fridager[dato_str] = {"type": "helligdag", "navn": navn}
        
        # Legg til ferier
        for start_dato, (navn, slutt_dato) in ferier.items():
            alle_fridager[start_dato] = {"type": "ferie", "navn": navn, "slutt": slutt_dato}
        
        # Legg til hendelser
        for dato_str, (navn, type_navn) in hendelser.items():
            alle_fridager[dato_str] = {"type": "hendelse", "navn": navn, "kategori": type_navn}
        
        return alle_fridager
    
    except Exception as e:
        logger.error(f"Feil ved henting av fridager: {e}")
        return {}

# ============================================================================
# MOTIVASJON OG INNHOLD
# ============================================================================
def hent_sitater() -> List[str]:
    """Henter motiverende sitater med mulighet for brukertilpasning"""
    # Standard sitater
    sitater = [
        "Hver dag er en ny mulighet til å bli bedre enn i går.",
        "Suksess er summen av små innsatser, gjentatt dag etter dag.",
        "Det eneste som står mellom deg og drømmen din er viljen til å prøve.",
        "Vær modig. Ta sjanser. Ingenting kan erstatte erfaring.",
        "Livet er 10% hva som skjer med deg og 90% hvordan du reagerer.",
        "Start der du er. Bruk det du har. Gjør det du kan.",
        "Den beste tiden å plante et tre var for 20 år siden. Den nest beste er nå.",
        "Tro på deg selv. Du er sterkere enn du tror.",
        "Ikke vent på muligheter. Skap dem.",
        "Små steg hver dag fører til store forandringer over tid.",
        "Hver ekspert var en gang en nybegynner.",
        "Din eneste grense er deg selv.",
        "Gjør det som er riktig, ikke det som er lett.",
        "Dagen i dag er en gave, derfor kaller vi den presang.",
        "Du trenger ikke være perfekt for å starte, men du må starte for å bli bedre.",
        "Fremtiden tilhører de som tror på skjønnheten i drømmene sine.",
        "Det er aldri for sent å bli den du kunne ha vært.",
        "Mot er ikke fraværet av frykt, men beslutningen om at noe annet er viktigere.",
        "Livet begynner der komfortsonen slutter.",
        "En reise på tusen mil begynner med et enkelt steg.",
        "Vær endringen du ønsker å se i verden.",
        "Hvis du kan drømme det, kan du oppnå det.",
        "Feil er bare bevis på at du prøver.",
        "Holdningen din bestemmer retningen din.",
        "Hver dag bringer nye valg.",
    ]
    
    # Legg til brukerdefinerte sitater hvis CUSTOM_QUOTES er satt
    custom_quotes = os.environ.get("CUSTOM_QUOTES")
    if custom_quotes:
        try:
            custom_list = json.loads(custom_quotes)
            if isinstance(custom_list, list):
                sitater.extend(custom_list)
                logger.info(f"La til {len(custom_list)} brukerdefinerte sitater")
        except json.JSONDecodeError as e:
            logger.error(f"Kunne ikke parse CUSTOM_QUOTES: {e}")
    
    return sitater

def hent_vitser() -> List[str]:
    """Henter norske vitser"""
    return [
        "Hvorfor går nordmenn alltid i fjellet? Fordi det er så oppoverbakke å bo der! 🏔️",
        "Hva sa snømåkeren til naboen? 'Jeg skyfler bare innom!' ❄️",
        "Hvorfor er norske biler så trege? Fordi de alltid går i sneglefart gjennom bomstasjonene! 🚗",
        "Hva kaller du en bjørn uten tenner? En gummy bear! 🐻",
        "Hvorfor klemte mannen klokken? Fordi tiden flyr! ⏰",
        "Hva gjør en lat hund? Han bjeffelansen! 🐕",
        "Hvorfor tok fisken dårlige karakterer? Fordi han var under C-nivået! 🐟",
        "Hva sa den ene veggen til den andre? Vi møtes i hjørnet! 🏠",
        "Hvorfor er matematikkboken alltid trist? Den har så mange problemer! 📚",
        "Hva kaller du en sau uten bein? En sky! ☁️🐑",
        "Hvorfor lo sjiraffen? Fordi gresset kilte ham under føttene! 🦒",
        "Hva sa tomatmamma til tomatbarn som sakket akterut? Ketchup! 🍅",
        "Hvorfor kan ikke sykler stå av seg selv? De er to-hjulet! 🚲",
        "Hva slags sko bruker spioner? Sneak-ers! 👟",
        "Hvorfor er havet så vennlig? Det vinker alltid! 🌊",
        "Hva kaller du en dinosaur som alltid sover? En dino-snore! 🦕",
        "Hvorfor gikk tomaten rød? Den så salatdressingen! 🥗",
        "Hva sa null til åtte? 'Fin belte!' 🔢",
        "Hvorfor kan ikke elefanter bruke datamaskiner? De er redde for musen! 🐘🖱️",
        "Hva er en vampyrs favorittfrukt? Blodappelsin! 🧛",
    ]

# ============================================================================
# AI-GENERERT INNHOLD
# ============================================================================
@retry_on_failure(max_attempts=2)
def generer_ai_hilsen() -> str:
    """Generer AI-basert hilsen med retry"""
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY ikke satt, bruker standardhilsen")
        return "God morgen! Håper du får en fantastisk dag! 🌅"
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        idag = hent_naverende_dato()
        dag_navn = hent_dagens_navn(idag)
        dato_str = idag.strftime("%d. %B")
        
        prompt = f"""Du er en morgenbot som gir personlige, positive morgenhilsener på norsk.
        I dag er {dag_navn} {dato_str}. Gi en kort, varm og personlig morgenhilsen (2-3 setninger).
        Bruk emojis og vær inspirerende. Ikke gjenta deg selv."""
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            max_tokens=100,
            temperature=0.7
        )
        
        hilsen = response.choices[0].message.content
        logger.info("AI-hilsen generert")
        return hilsen
    
    except Exception as e:
        logger.error(f"Feil ved AI-generering: {e}")
        vitser = hent_vitser()
        return f"God morgen! Håper du får en strålende dag! Her er en vits for å starte dagen: {random.choice(vitser)}"

# ============================================================================
# DISCORD MELDING
# ============================================================================
def lag_discord_melding() -> Dict[str, Any]:
    """Lager Discord-melding med all data"""
    try:
        idag = hent_naverende_dato()
        dag_navn = hent_dagens_navn(idag)
        dato_str = idag.strftime("%d. %B %Y")
        
        # Hent data med feilhåndtering
        logger.info("Henter værdata...")
        vaer = hent_vaer(BY) or {}
        
        logger.info("Henter nyheter...")
        nyheter = hent_nyheter()
        
        logger.info("Henter økonomidata...")
        okonomi = hent_okonomi()
        
        logger.info("Henter kryptodata...")
        krypto = hent_krypto()
        
        logger.info("Henter AI-hilsen...")
        ai_hilsen = generer_ai_hilsen()
        
        # Bygg melding
        embed = {
            "title": f"🌅 God {dag_navn.lower()}!",
            "description": f"**{dag_navn} {dato_str}**\n\n{ai_hilsen}",
            "color": 4521799,  # Norsk blåfarge
            "fields": [],
            "footer": {
                "text": "Morgenbot - Din daglige oppsummering",
                "icon_url": "https://cdn.discordapp.com/attachments/123456789/123456789/morgenbot.png"
            },
            "timestamp": idag.isoformat()
        }
        
        # Vær
        if vaer:
            vaer_text = f"**{vaer.get('temperatur', 'N/A')}** {vaer.get('symbol', '')}\n"
            vaer_text += f"Vind: {vaer.get('vind', 'N/A')}\n"
            vaer_text += f"Nedbør: {vaer.get('nedbør', 'N/A')}\n"
            if vaer.get('strompris') != "Ikke tilgjengelig":
                vaer_text += f"Strøm: {vaer.get('strompris', 'N/A')}"
            
            embed["fields"].append({
                "name": f"🌤️ Vær i {BY}",
                "value": vaer_text,
                "inline": False
            })
            
            embed["fields"].append({
                "name": " ",
                "value": vaer.get('klesanbefaling', ''),
                "inline": False
            })
        
        # Fridager og hendelser
        fridager = hent_fridager()
        kommende_fridager = []
        
        dagens_dato_str = idag.strftime("%Y-%m-%d")
        
        # Sjekk dagens spesielle hendelser
        if dagens_dato_str in fridager:
            fridag_info = fridager[dagens_dato_str]
            if fridag_info["type"] == "ferie":
                embed["fields"].append({
                    "name": "🎉 Spesielt i dag",
                    "value": f"{fridag_info['navn']}! {fridag_info.get('slutt', '')}",
                    "inline": False
                })
            else:
                embed["fields"].append({
                    "name": "🎉 Spesielt i dag",
                    "value": fridag_info["navn"],
                    "inline": False
                })
        
        # Finn kommende fridager
        for dato_str, info in sorted(fridager.items()):
            if dato_str > dagens_dato_str:
                dager_frem = (datetime.strptime(dato_str, "%Y-%m-%d").date() - idag.date()).days
                if dager_frem <= 30:  # Vis fridager innen 30 dager
                    countdown = tell_ned_til_dato(datetime.strptime(dato_str, "%Y-%m-%d"))
                    if countdown:
                        if info["type"] == "ferie":
                            kommende_fridager.append(f"• {info['navn']} ({countdown})")
                        else:
                            kommende_fridager.append(f"• {info['navn']} ({countdown})")
        
        if kommende_fridager:
            embed["fields"].append({
                "name": "📅 Kommende fridager",
                "value": "\n".join(kommende_fridager),
                "inline": False
            })
        
        # Navnedager
        navnedager = hent_navnedag(idag)
        if navnedager:
            embed["fields"].append({
                "name": "🎂 Navnedager",
                "value": ", ".join(navnedager),
                "inline": False
            })
        
        # Nyheter
        if nyheter:
            nyheter_text = "\n".join([f"• [{n['tittel']}]({n['link']})" for n in nyheter[:3]])
            embed["fields"].append({
                "name": "📰 Siste nytt",
                "value": nyheter_text,
                "inline": False
            })
        
        # Økonomi
        okonomi_data = okonomi or {}
        aksjer = okonomi_data.get("aksjer", [])
        valuta = okonomi_data.get("valuta", [])
        
        if aksjer:
            aksjer_text = "\n".join([f"{a['emoji']} **{a['navn']}**: {a['pris']:.2f} ({a['endring_str']})" for a in aksjer[:3]])
            embed["fields"].append({
                "name": "📈 Aksjer",
                "value": aksjer_text,
                "inline": True
            })
        
        if valuta:
            valuta_text = "\n".join([f"{v['emoji']} **{v['par']}**: {v['kurs']}" for v in valuta])
            embed["fields"].append({
                "name": "💱 Valuta",
                "value": valuta_text,
                "inline": True
            })
        
        # Krypto
        if krypto:
            krypto_text = "\n".join([f"{k['emoji']} **{k['navn']}**: {k['pris_nok']:.2f} NOK ({k['endring_str']})" for k in krypto[:3]])
            embed["fields"].append({
                "name": "₿ Kryptovaluta",
                "value": krypto_text,
                "inline": False
            })
        
        # Motivasjon
        sitater = hent_sitater()
        if sitater:
            embed["fields"].append({
                "name": "💪 Dagens motivasjon",
                "value": f"*{random.choice(sitater)}*",
                "inline": False
            })
        
        return embed
    
    except Exception as e:
        logger.error(f"Feil ved oppretting av melding: {e}")
        return {
            "title": "❌ Feil",
            "description": "Kunne ikke generere dagens oppsummering. Sjekk loggene for detaljer.",
            "color": 15158332
        }

# ============================================================================
# DISCORD SENDING
# ============================================================================
@retry_on_failure(max_attempts=3)
def send_discord_melding() -> bool:
    """Sender melding til Discord med retry"""
    if not DISCORD_WEBHOOK:
        logger.error("DISCORD_WEBHOOK ikke satt")
        return False
    
    try:
        melding = lag_discord_melding()
        
        embed = melding
        embed["thumbnail"] = {
            "url": "https://cdn.discordapp.com/attachments/123456789/123456789/morgenbot_logo.png"
        }
        
        payload = {"embeds": [embed]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(DISCORD_WEBHOOK, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 204:
            logger.info("Melding sendt til Discord!")
            return True
        else:
            logger.error(f"Feil ved sending til Discord: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Nettverksfeil ved sending til Discord: {e}")
        return False
    except Exception as e:
        logger.error(f"Uventet feil ved sending til Discord: {e}")
        return False

# ============================================================================
# TESTING OG HOVEDFUNKSJON
# ============================================================================
def test_funksjoner():
    """Test alle kritiske funksjoner"""
    logger.info("Starter test av funksjoner...")
    
    # Test vær
    logger.info(f"Tester vær for {BY}...")
    vaer = hent_vaer(BY)
    logger.info(f"Vær: {'OK' if vaer else 'FEILET'}")
    
    # Test nyheter
    logger.info("Tester nyheter...")
    nyheter = hent_nyheter()
    logger.info(f"Nyheter: {'OK' if nyheter and len(nyheter) > 0 else 'FEILET'}")
    
    # Test økonomi
    logger.info("Tester økonomi...")
    okonomi = hent_okonomi()
    logger.info(f"Økonomi: {'OK' if okonomi else 'FEILET'}")
    
    # Test krypto
    logger.info("Tester krypto...")
    krypto = hent_krypto()
    logger.info(f"Krypto: {'OK' if krypto else 'FEILET'}")
    
    # Test fridager
    logger.info("Tester fridager...")
    fridager = hent_fridager()
    logger.info(f"Fridager: {'OK' if fridager else 'FEILET'}")
    
    logger.info("Test fullført!")
    return True

def main():
    """Hovedfunksjon"""
    try:
        logger.info("=" * 50)
        logger.info("MORGENBOT STARTER")
        logger.info("=" * 50)
        
        # Valider miljøvariabler
        if not DISCORD_WEBHOOK:
            logger.warning("DISCORD_WEBHOOK ikke satt. Bruk: export DISCORD_WEBHOOK='din-webhook-url'")
            return False
        
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY ikke satt. AI-hilsen vil bruke standard melding.")
        
        logger.info(f"By: {BY}")
        logger.info(f"Webhook konfigurert: {'Ja' if DISCORD_WEBHOOK else 'Nei'}")
        logger.info(f"Groq API konfigurert: {'Ja' if GROQ_API_KEY else 'Nei'}")
        
        # Kjør test hvis i test-modus
        if os.environ.get("TEST_MODE") == "true":
            return test_funksjoner()
        
        # Send melding
        success = send_discord_melding()
        
        logger.info("=" * 50)
        logger.info(f"MORGENBOT FERDIG: {'SUKSRESS' if success else 'FEILET'}")
        logger.info("=" * 50)
        
        return success
        
    except Exception as e:
        logger.error(f"Kritisk feil i main: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)