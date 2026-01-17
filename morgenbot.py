import requests
import feedparser
import os
import json
import random
from datetime import datetime, timedelta
from groq import Groq

# Miljøvariabler
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BY = os.environ.get("BY", "Moss")

# Norske helligdager 2025
HELLIGDAGER_2025 = {
    "2025-01-01": "Første nyttårsdag",
    "2025-04-13": "Palmesøndag",
    "2025-04-17": "Skjærtorsdag",
    "2025-04-18": "Langfredag",
    "2025-04-20": "Første påskedag",
    "2025-04-21": "Andre påskedag",
    "2025-05-01": "Arbeidernes dag",
    "2025-05-17": "Grunnlovsdagen",
    "2025-05-29": "Kristi himmelfartsdag",
    "2025-06-08": "Første pinsedag",
    "2025-06-09": "Andre pinsedag",
    "2025-12-25": "Første juledag",
    "2025-12-26": "Andre juledag",
}

# Norske skoleferier 2025
FERIER_2025 = {
    "2025-02-17": ("Vinterferie starter", "2025-02-21"),
    "2025-04-14": ("Påskeferie starter", "2025-04-21"),
    "2025-06-20": ("Sommerferie starter", "2025-08-15"),
    "2025-10-06": ("Høstferie starter", "2025-10-10"),
    "2025-12-22": ("Juleferie starter", "2026-01-02"),
}

# Norske byer med koordinater
BY_KOORDINATER = {
    "Moss": {"lat": 59.43, "lon": 10.66},
    "Oslo": {"lat": 59.91, "lon": 10.75},
    "Bergen": {"lat": 60.39, "lon": 5.32},
    "Trondheim": {"lat": 63.43, "lon": 10.39},
    "Stavanger": {"lat": 58.97, "lon": 5.73},
    "Tromsø": {"lat": 69.65, "lon": 18.96},
    "Kristiansand": {"lat": 58.15, "lon": 8.00},
    "Drammen": {"lat": 59.74, "lon": 10.20},
    "Fredrikstad": {"lat": 59.22, "lon": 10.93},
}

# Motiverende sitater
SITATER = [
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
]

# Oversettelse av værsymboler
VAER_SYMBOLER = {
    "clearsky": "☀️ Klar himmel",
    "fair": "🌤️ Lettskyet",
    "partlycloudy": "⛅ Delvis skyet",
    "cloudy": "☁️ Overskyet",
    "rain": "🌧️ Regn",
    "lightrain": "🌦️ Lett regn",
    "heavyrain": "🌧️ Kraftig regn",
    "snow": "❄️ Snø",
    "sleet": "🌨️ Sludd",
    "fog": "🌫️ Tåke",
    "thunder": "⛈️ Torden",
}

# Norske dager og måneder
DAGER = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
MAANEDER = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember"
]


def hent_vaer(by):
    """Henter værdata fra Meteorologisk institutt for en gitt by."""
    try:
        # Hent koordinater for byen
        by_lower = by.lower()
        by_data = None
        for city_name, coords in BY_KOORDINATER.items():
            if city_name.lower() == by_lower:
                by_data = coords
                break
        
        if not by_data:
            # Bruk Moss som standard hvis byen ikke finnes
            by_data = BY_KOORDINATER["Moss"]
            print(f"By '{by}' ikke funnet, bruker Moss som standard")
        
        lat = by_data["lat"]
        lon = by_data["lon"]
        
        # Hent værdata fra Met.no API
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        headers = {
            "User-Agent": "MorgenBot/1.0 github.com/user/morgenbot"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Trekk ut værdata
        timeseries = data["properties"]["timeseries"][0]
        instant = timeseries["data"]["instant"]["details"]
        
        temp = instant["air_temperature"]
        vind = instant["wind_speed"]
        
        # Hent værsymbol
        symbol = "Ukjent"
        if "next_1_hours" in timeseries["data"]:
            symbol_code = timeseries["data"]["next_1_hours"]["summary"]["symbol_code"]
        elif "next_6_hours" in timeseries["data"]:
            symbol_code = timeseries["data"]["next_6_hours"]["summary"]["symbol_code"]
        else:
            symbol_code = "cloudy"
        
        # Fjern _day eller _night suffix
        symbol_base = symbol_code.split("_")[0]
        symbol = VAER_SYMBOLER.get(symbol_base, f"❓ {symbol_code}")
        
        # Klesanbefaling basert på temperatur
        if temp < -10:
            klaer = "🧥 Veldig kaldt! Boblejakke, lue, votter og skjerf"
        elif temp < 0:
            klaer = "🧥 Kaldt! Varm jakke og lue anbefales"
        elif temp < 10:
            klaer = "🧥 Kjølig. Jakke og lag-på-lag"
        elif temp < 20:
            klaer = "👕 Behagelig. Lett jakke eller genser"
        else:
            klaer = "☀️ Varmt! T-skjorte og shorts"
        
        return {
            "temp": temp,
            "vind": vind,
            "symbol": symbol,
            "klaer": klaer,
        }
        
    except Exception as e:
        print(f"Feil ved henting av vær: {e}")
        return {"error": f"Kunne ikke hente værdata: {str(e)}"}


def hent_nyheter():
    """Henter nyheter fra NRK."""
    try:
        rss_feeds = [
            "https://www.nrk.no/toppsaker.rss",
            "https://www.nrk.no/verden/toppsaker.rss"
        ]
        
        nyheter = []
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                # Hent første 3 nyheter fra hver feed
                for entry in feed.entries[:3]:
                    if len(nyheter) >= 6:  # Maks 6 nyheter totalt
                        break
                    nyheter.append({
                        "tittel": entry.title,
                        "link": entry.link
                    })
            except Exception as e:
                print(f"Feil ved parsing av RSS feed {feed_url}: {e}")
                continue
        
        return nyheter[:6]  # Returner maks 6 nyheter
        
    except Exception as e:
        print(f"Feil ved henting av nyheter: {e}")
        return []


def hent_aksjer():
    """Henter aksjekurser og valutakurser."""
    try:
        aksjer_info = []
        
        # Aksjer å hente fra Yahoo Finance
        aksjer = [
            ("OSEBX", "Oslo Børs Hovedindeks"),
            ("EQNR.OL", "Equinor"),
            ("DNB.OL", "DNB Bank"),
            ("TEL.OL", "Telenor"),
            ("MOWI.OL", "Mowi"),
            ("ORK.OL", "Orkla"),
        ]
        
        headers = {
            "User-Agent": "MorgenBot/1.0 github.com/user/morgenbot"
        }
        
        for symbol, navn in aksjer:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                meta = data["chart"]["result"][0]["meta"]
                
                current = meta["regularMarketPrice"]
                previous = meta["previousClose"]
                
                endring = ((current - previous) / previous) * 100
                
                emoji = "📈" if endring >= 0 else "📉"
                endring_str = f"+{endring:.2f}%" if endring >= 0 else f"{endring:.2f}%"
                
                aksjer_info.append(f"{emoji} **{navn}**: {current:.2f} ({endring_str})")
                
            except Exception as e:
                print(f"Feil ved henting av {symbol}: {e}")
                continue
        
        # Hent valutakurser
        try:
            # USD til NOK
            url_usd = "https://api.exchangerate-api.com/v4/latest/USD"
            response_usd = requests.get(url_usd, timeout=10)
            response_usd.raise_for_status()
            data_usd = response_usd.json()
            nok_per_usd = data_usd["rates"]["NOK"]
            aksjer_info.append(f"💵 **USD**: 1 = {nok_per_usd:.2f} NOK")
            
            # EUR til NOK
            url_eur = "https://api.exchangerate-api.com/v4/latest/EUR"
            response_eur = requests.get(url_eur, timeout=10)
            response_eur.raise_for_status()
            data_eur = response_eur.json()
            nok_per_eur = data_eur["rates"]["NOK"]
            aksjer_info.append(f"💶 **EUR**: 1 = {nok_per_eur:.2f} NOK")
            
        except Exception as e:
            print(f"Feil ved henting av valutakurser: {e}")
        
        return aksjer_info
        
    except Exception as e:
        print(f"Feil ved henting av aksjer: {e}")
        return []


def finn_neste_fridag():
    """Finner neste helligdag og ferie."""
    try:
        idag = datetime.now().date()
        
        # Finn neste helligdag
        neste_helligdag = None
        dager_til_helligdag = None
        helligdag_dato = None
        
        for dato_str, navn in sorted(HELLIGDAGER_2025.items()):
            dato = datetime.strptime(dato_str, "%Y-%m-%d").date()
            if dato >= idag:
                neste_helligdag = navn
                helligdag_dato = dato
                dager_til_helligdag = (dato - idag).days
                break
        
        # Finn neste ferie
        neste_ferie = None
        dager_til_ferie = None
        ferie_dato = None
        
        for dato_str, (navn, slutt_dato_str) in sorted(FERIER_2025.items()):
            dato = datetime.strptime(dato_str, "%Y-%m-%d").date()
            if dato >= idag:
                neste_ferie = navn
                ferie_dato = dato
                dager_til_ferie = (dato - idag).days
                break
        
        return {
            "helligdag": neste_helligdag,
            "dager_til_helligdag": dager_til_helligdag,
            "helligdag_dato": helligdag_dato,
            "ferie": neste_ferie,
            "dager_til_ferie": dager_til_ferie,
            "ferie_dato": ferie_dato,
        }
        
    except Exception as e:
        print(f"Feil ved finn_neste_fridag: {e}")
        return {
            "helligdag": None,
            "dager_til_helligdag": None,
            "helligdag_dato": None,
            "ferie": None,
            "dager_til_ferie": None,
            "ferie_dato": None,
        }


def hent_sitat():
    """Returnerer et tilfeldig motiverende sitat."""
    return random.choice(SITATER)


def generer_melding_med_ai(data):
    """Genererer personlig hilsning ved hjelp av Groq AI."""
    try:
        if not GROQ_API_KEY:
            print("GROQ_API_KEY ikke satt, hopper over AI-generering")
            return None
        
        client = Groq(api_key=GROQ_API_KEY)
        
        # Formater data for prompt
        vaer_info = f"{data['vaer']['temp']}°C, {data['vaer']['symbol']}"
        
        nyheter_tekst = ", ".join([n["tittel"] for n in data["nyheter"][:3]])
        
        helligdag_info = ""
        if data["fridager"]["helligdag"]:
            dager = data["fridager"]["dager_til_helligdag"]
            navn = data["fridager"]["helligdag"]
            if dager == 0:
                helligdag_info = f"I dag er det {navn}"
            elif dager == 1:
                helligdag_info = f"I morgen er det {navn}"
            else:
                helligdag_info = f"{navn} om {dager} dager"
        else:
            helligdag_info = "Ingen kommende helligdager"
        
        prompt = f"""Du er en hyggelig norsk morgenassistent. Lag en kort, personlig og positiv oppsummering basert på denne informasjonen:

Vær: {vaer_info}
Nyheter: {nyheter_tekst}
Neste fridag: {helligdag_info}

Skriv 2-3 setninger som er varme, personlige og motiverende. Bruk norsk. Ikke bruk emojis."""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Feil ved AI-generering: {e}")
        return None


def lag_discord_melding(by):
    """Lager komplett Discord melding med alle data."""
    try:
        # Hent all data
        vaer = hent_vaer(by)
        nyheter = hent_nyheter()
        aksjer = hent_aksjer()
        fridager = finn_neste_fridag()
        sitat = hent_sitat()
        
        # Generer AI hilsning
        ai_data = {
            "vaer": vaer,
            "nyheter": nyheter,
            "fridager": fridager,
        }
        ai_hilsning = generer_melding_med_ai(ai_data)
        
        # Formater dato på norsk
        naa = datetime.now()
        dag_navn = DAGER[naa.weekday()]
        dag = naa.day
        maaned_navn = MAANEDER[naa.month - 1]
        aar = naa.year
        formatert_dato = f"{dag_navn} {dag}. {maaned_navn} {aar}"
        
        # Bygg felter
        felter = []
        
        # Vær-felt
        if "error" not in vaer:
            vaer_felt = {
                "name": f"🌤️ Været i {by}",
                "value": (
                    f"**{vaer['symbol']}**\n"
                    f"🌡️ Temperatur: {vaer['temp']}°C\n"
                    f"💨 Vind: {vaer['vind']} m/s\n"
                    f"👔 {vaer['klaer']}"
                ),
                "inline": False
            }
            felter.append(vaer_felt)
        
        # Nyheter-felt
        if nyheter:
            nyhet_tekst = ""
            for i, nyhet in enumerate(nyheter[:5], 1):
                nyhet_tekst += f"{i}. [{nyhet['tittel']}]({nyhet['link']})\n"
            nyheter_felt = {
                "name": "📰 Dagens Nyheter",
                "value": nyhet_tekst,
                "inline": False
            }
            felter.append(nyheter_felt)
        
        # Aksjer-felt
        if aksjer:
            aksjer_tekst = "\n".join(aksjer)
            aksjer_felt = {
                "name": "📈 Økonomi & Aksjer",
                "value": aksjer_tekst,
                "inline": True
            }
            felter.append(aksjer_felt)
        
        # Fridager-felt
        fridag_tekst = ""
        if fridager["helligdag"] and fridager["dager_til_helligdag"] is not None:
            dager = fridager["dager_til_helligdag"]
            navn = fridager["helligdag"]
            if dager == 0:
                fridag_tekst += f"📅 **I dag er det {navn}!**\n\n"
            elif dager == 1:
                fridag_tekst += f"📅 **I morgen er det {navn}**\n\n"
            else:
                fridag_tekst += f"📅 **{navn}**\nOm {dager} dager\n\n"
        else:
            fridag_tekst += "📅 Ingen kommende helligdager\n\n"
        
        if fridager["ferie"] and fridager["dager_til_ferie"] is not None:
            dager = fridager["dager_til_ferie"]
            navn = fridager["ferie"]
            if dager == 0:
                fridag_tekst += f"🏖️ **I dag starter {navn}!**"
            elif dager == 1:
                fridag_tekst += f"🏖️ **I morgen starter {navn}**"
            else:
                fridag_tekst += f"🏖️ **{navn}**\nOm {dager} dager"
        else:
            fridag_tekst += "🏖️ Ingen kommende ferier"
        
        felter.append({
            "name": "🗓️ Kommende Fridager",
            "value": fridag_tekst,
            "inline": True
        })
        
        # Motivasjon-felt
        felter.append({
            "name": "💪 Dagens Motivasjon",
            "value": f"*\"{sitat}\"*",
            "inline": False
        })
        
        # Bygg embed
        embed = {
            "title": f"☀️ God morgen! {formatert_dato}",
            "description": ai_hilsning if ai_hilsning else None,
            "color": 5814783,  # Blå farge
            "fields": felter,
            "footer": {
                "text": f"Din personlige morgenbot 🤖 | {by}"
            },
            "timestamp": naa.isoformat()
        }
        
        # Fjern description hvis den er None
        if embed["description"] is None:
            del embed["description"]
        
        melding = {
            "embeds": [embed]
        }
        
        return melding
        
    except Exception as e:
        print(f"Feil ved lag_discord_melding: {e}")
        return None


def send_til_discord(melding):
    """Sender melding til Discord webhook."""
    try:
        if not DISCORD_WEBHOOK:
            print("DISCORD_WEBHOOK miljøvariabel ikke satt")
            return False
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(DISCORD_WEBHOOK, json=melding, headers=headers, timeout=10)
        
        if response.status_code == 204:
            print("Melding sendt til Discord!")
            return True
        else:
            print(f"Feil ved sending til Discord: Status {response.status_code}")
            print(f"Respons: {response.text}")
            return False
        
    except Exception as e:
        print(f"Feil ved send_til_discord: {e}")
        return False


def main():
    """Hovedfunksjon."""
    print("🌅 Morgenbot starter...")
    print(f"📍 By: {BY}")
    
    # Sjekk at nødvendige miljøvariabler er satt
    if not DISCORD_WEBHOOK:
        print("⚠️ ADVARSEL: DISCORD_WEBHOOK ikke satt!")
    
    if not GROQ_API_KEY:
        print("⚠️ ADVARSEL: GROQ_API_KEY ikke satt. AI-generering vil bli hoppet over.")
    
    # Lag og send melding
    print("📨 Lager melding...")
    melding = lag_discord_melding(BY)
    
    if melding:
        print("📤 Sender melding til Discord...")
        suksess = send_til_discord(melding)
        
        if suksess:
            print("✅ Morgenbot fullført!")
        else:
            print("❌ Kunne ikke sende melding til Discord")
    else:
        print("❌ Kunne ikke lage melding")
    
    print(f"🏁 Ferdig! Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
