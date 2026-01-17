# 🌅 Morgenbot

En personlig morgenbot som sender deg en daglig oppsummering på Discord kl. 06:00 norsk tid med vær, nyheter, aksjer, fridager og motivasjon.

## ✨ Funksjoner

- 🌤️ **Værvarsel** fra Yr.no (Meteorologisk institutt) med temperatur, vind og klesanbefaling
- 📰 **Nyheter** fra NRK (toppsaker og verdensnyheter)
- 📈 **Økonomi** med aksjekurser fra Oslo Børs og valutakurser
- 🗓️ **Fridager** med oversikt over kommende helligdager og ferier
- 💪 **Motivasjon** med dagens inspirerende sitat
- 🤖 **AI-generert hilsning** med personlig velkomstmelding

## 🚀 Oppsett

### 1. Forutsetninger

- Python 3.11 eller nyere
- GitHub-konto
- Discord-konto med en server

### 2. Fork eller klon dette depotet

```bash
git clone https://github.com/ditt-brukernavn/morgenbot.git
cd morgenbot
```

### 3. Installer Python-avhengigheter

```bash
pip install -r requirements.txt
```

Eller installer pakken i utviklingsmodus:

```bash
pip install -e .
```

### 4. Opprett Discord Webhook

1. Gå til din Discord-server
2. Åpne serverinnstillinger (Server Settings)
3. Gå til "Integrations" → "Webhooks"
4. Klikk "New Webhook"
5. Gi den et navn (f.eks. "Morgenbot")
6. Velg hvilken kanal meldingene skal sendes til
7. Kopier webhook URL-en

### 5. Få Groq API-nøkkel

1. Gå til [groq.com](https://groq.com)
2. Opprett en gratis konto
3. Gå til API-keys i dashboardet
4. Opprett en ny API-nøkkel
5. Kopier nøkkelen

### 6. Konfigurer miljøvariabler

Kopier eksempel-miljøfilen og rediger den:

```bash
cp .env.example .env
```

Rediger `.env` og fyll inn dine verdier:
- `DISCORD_WEBHOOK`: Din Discord webhook URL (påkrevd)
- `GROQ_API_KEY`: Din Groq API-nøkkel for AI-funksjoner (valgfritt)
- `BY`: Din by (valgfritt, standard er "Moss")

For GitHub Actions, legg til følgende secrets i repository settings:

| Secret navn | Verdi |
|-------------|-------|
| `DISCORD_WEBHOOK` | Din Discord webhook URL (hel URL) |
| `GROQ_API_KEY` | Din Groq API-nøkkel (valgfritt) |
| `BY` | Din by (valgfritt, standard er "Moss") |

Støttede byer: `Moss`, `Oslo`, `Bergen`, `Trondheim`, `Stavanger`, `Tromsø`, `Kristiansand`, `Drammen`, `Fredrikstad`

## 🧪 Manuell testing

Du kan teste boten manuelt ved å kjøre:

```bash
python morgenbot.py
```

For å teste på GitHub Actions:

1. Gå til "Actions" i ditt GitHub-depot
2. Velg "Morgenbot" workflow
3. Klikk "Run workflow" → "Run workflow"

For å teste uten å sende til Discord (test mode):

```bash
TEST_MODE=true python morgenbot.py
```

## ⚙️ Tilpasning

### Legge til egne byer

Rediger `data/cities.json` eller bruk miljøvariabelen `CUSTOM_CITIES`:

```bash
export CUSTOM_CITIES='{"DinBy": {"lat": 59.91, "lon": 10.75, "strompris_sone": "NO1"}}'
```

### Tilpasse sitater

Rediger `data/quotes.json` eller bruk miljøvariabelen `CUSTOM_QUOTES`:

```bash
export CUSTOM_QUOTES='["Ditt eget sitat", "Enda et sitat"]'
```

### Endre aksjer

Bruk miljøvariabelen `KONFIGURER_AKSJER`:

```bash
export KONFIGURER_AKSJER="^OSEAX,Oslo Børs;EQNR.OL,Equinor;DNB.OL,DNB"
```

Format: `SYMBOL,Navn;SYMBOL,Navn`

### Endre tidspunkt

Rediger cron-uttrykket i `.github/workflows/morgenbot.yml`:

```yaml
schedule:
  - cron: '0 5 * * *'  # 05:00 UTC = 06:00 norsk vintertid
```

Cron-formatet er: `minutt time dag måned ukedag` (UTC-tid)

### Endre farge på Discord-melding

Rediger `color`-verdien i `lag_discord_melding()`-funksjonen (desimal fargekode).

## 📂 Datafiler

Morgenbot bruker JSON-filer i `data/`-mappen for konfigurasjon:

- `cities.json` - Bykoordinater og strømsone
- `weather_symbols.json` - Værsymboler for Yr.no API
- `quotes.json` - Motiverende sitater
- `jokes.json` - Norske vitser
- `proverbs.json` - Norske ordtak
- `holidays.json` - Norske helligdager
- `name_days.json` - Navnedager
- `vacations.json` - Skoleferier (kan utvides)
- `events.json` - Store hendelser (kan utvides)

Alle disse filene kan redigeres direkte for å tilpasse innholdet.

## 🌆 Støttede byer

Morgenbot støtter følgende norske byer:

- Moss (standard)
- Oslo
- Bergen
- Trondheim
- Stavanger
- Tromsø
- Kristiansand
- Drammen
- Fredrikstad

Endre by ved å oppdatere `BY` secret eller angi som miljøvariabel.

## 📊 Datakilder

Morgenbot bruker følgende gratis tjenester:

- **Vær**: [Yr.no / Meteorologisk institutt](https://www.met.no/) (gratis API)
- **Nyheter**: [NRK](https://www.nrk.no/) (RSS-feeds)
- **Aksjer**: [Yahoo Finance](https://finance.yahoo.com/) (gratis API)
- **Valuta**: [ExchangeRate-API](https://www.exchangerate-api.com/) (gratis tier)
- **AI**: [Groq](https://groq.com/) (gratis tier med Llama 3.1)

## 📝 Lisens

Dette prosjektet er åpen kildekode. Du kan fritt bruke, endre og distribuere det etter behov.

## 🤝 Bidrag

Føler du for å bidra? 

- Rapporter bugs eller issues
- Foreslå nye funksjoner
- Send inn pull requests

## 💡 Tips

- Boten sender melding kl. 06:00 norsk tid (05:00 UTC om vinteren)
- Om sommeren (når Norge er UTC+2) vil meldingen komme kl. 07:00. Du kan endre cron til `'0 4 * * *'` hvis du vil ha kl. 06:00 også om sommeren.
- All kode er kommentert på norsk for enkel forståelse
- Boten håndterer feil forsiktig - hvis én datakilde feiler, sendes likevel meldingen

---

Laget med ❤️ for norske morgener! 🇳🇴
