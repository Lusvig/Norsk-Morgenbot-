# Fjern proxy-innstillinger
import os
import requests
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

from dotenv import load_dotenv
load_dotenv()

import requests
import feedparser
import json
import random
import re
from datetime import datetime, timedelta
from groq import Groq

# Miljøvariabler
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BY = os.environ.get("BY", "Moss")

# ============================================================================
# HELLIGDAGER OG FERIER
# ============================================================================
HELLIGDAGER = {
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
"2026-01-01": "Første nyttårsdag",
"2026-04-02": "Skjærtorsdag",
"2026-04-03": "Langfredag",
"2026-04-05": "Første påskedag",
"2026-04-06": "Andre påskedag",
"2026-05-01": "Arbeidernes dag",
"2026-05-14": "Kristi himmelfartsdag",
"2026-05-17": "Grunnlovsdagen",
"2026-05-24": "Første pinsedag",
"2026-05-25": "Andre pinsedag",
"2026-12-25": "Første juledag",
"2026-12-26": "Andre juledag",
"2027-01-01": "Første nyttårsdag",
"2027-03-25": "Skjærtorsdag",
"2027-03-26": "Langfredag",
"2027-03-28": "Første påskedag",
"2027-03-29": "Andre påskedag",
"2027-05-01": "Arbeidernes dag",
"2027-05-06": "Kristi himmelfartsdag",
"2027-05-16": "Første pinsedag",
"2027-05-17": "Grunnlovsdagen / Andre pinsedag",
"2027-12-25": "Første juledag",
"2027-12-26": "Andre juledag",
}

FERIER = {
"2025-02-17": ("Vinterferie starter", "2025-02-21"),
"2025-04-14": ("Påskeferie starter", "2025-04-21"),
"2025-06-20": ("Sommerferie starter", "2025-08-15"),
"2025-10-06": ("Høstferie starter", "2025-10-10"),
"2025-12-22": ("Juleferie starter", "2026-01-02"),
"2026-02-16": ("Vinterferie starter", "2026-02-20"),
"2026-03-30": ("Påskeferie starter", "2026-04-06"),
"2026-06-19": ("Sommerferie starter", "2026-08-14"),
"2026-10-05": ("Høstferie starter", "2026-10-09"),
"2026-12-21": ("Juleferie starter", "2027-01-01"),
}

# ============================================================================
# STORE EVENTER Å TELLE NED TIL
# ============================================================================
STORE_EVENTER = {
"2025-06-21": ("☀️ Sommeren starter!", "Sommersolverv"),
"2025-12-24": ("🎄 Julaften", "Jul"),
"2025-12-31": ("🎆 Nyttårsaften", "Nyttår"),
"2026-02-06": ("🏈 Super Bowl LX", "Super Bowl"),
"2026-06-11": ("⚽ VM 2026 starter!", "FIFA World Cup"),
"2026-02-06": ("🏅 Vinter-OL 2026", "Milano-Cortina"),
"2025-05-10": ("🎤 Eurovision 2025", "Basel"),
"2025-07-04": ("🚴 Tour de France starter", "Sykkel"),
}

# ============================================================================
# BYER MED KOORDINATER
# ============================================================================
BY_KOORDINATER = {
"Moss": {"lat": 59.43, "lon": 10.66, "strompris_sone": "NO1"},
"Oslo": {"lat": 59.91, "lon": 10.75, "strompris_sone": "NO1"},
"Bergen": {"lat": 60.39, "lon": 5.32, "strompris_sone": "NO5"},
"Trondheim": {"lat": 63.43, "lon": 10.39, "strompris_sone": "NO3"},
"Stavanger": {"lat": 58.97, "lon": 5.73, "strompris_sone": "NO2"},
"Tromsø": {"lat": 69.65, "lon": 18.96, "strompris_sone": "NO4"},
"Kristiansand": {"lat": 58.15, "lon": 8.00, "strompris_sone": "NO2"},
"Drammen": {"lat": 59.74, "lon": 10.20, "strompris_sone": "NO1"},
"Fredrikstad": {"lat": 59.22, "lon": 10.93, "strompris_sone": "NO1"},
"Sarpsborg": {"lat": 59.28, "lon": 11.11, "strompris_sone": "NO1"},
"Sandnes": {"lat": 58.85, "lon": 5.74, "strompris_sone": "NO2"},
"Bodø": {"lat": 67.28, "lon": 14.40, "strompris_sone": "NO4"},
"Ålesund": {"lat": 62.47, "lon": 6.15, "strompris_sone": "NO3"},
"Tønsberg": {"lat": 59.27, "lon": 10.41, "strompris_sone": "NO1"},
"Haugesund": {"lat": 59.41, "lon": 5.27, "strompris_sone": "NO2"},
"Sandefjord": {"lat": 59.13, "lon": 10.22, "strompris_sone": "NO1"},
"Larvik": {"lat": 59.05, "lon": 10.03, "strompris_sone": "NO1"},
"Halden": {"lat": 59.12, "lon": 11.39, "strompris_sone": "NO1"},
"Lillehammer": {"lat": 61.12, "lon": 10.47, "strompris_sone": "NO1"},
"Molde": {"lat": 62.74, "lon": 7.16, "strompris_sone": "NO3"},
"Hamar": {"lat": 60.79, "lon": 11.07, "strompris_sone": "NO1"},
"Kongsberg": {"lat": 59.67, "lon": 9.65, "strompris_sone": "NO1"},
"Gjøvik": {"lat": 60.80, "lon": 10.69, "strompris_sone": "NO1"},
"Harstad": {"lat": 68.80, "lon": 16.54, "strompris_sone": "NO4"},
"Narvik": {"lat": 68.44, "lon": 17.43, "strompris_sone": "NO4"},
"Alta": {"lat": 69.97, "lon": 23.27, "strompris_sone": "NO4"},
"Hammerfest": {"lat": 70.66, "lon": 23.68, "strompris_sone": "NO4"},
"Kirkenes": {"lat": 69.73, "lon": 30.05, "strompris_sone": "NO4"},
}

# ============================================================================
# NAVNEDAGER (Norske)
# ============================================================================
NAVNEDAGER = {
"01-01": ["Nyttår"],
"01-02": ["Dagfinn", "Dagfrid"],
"01-03": ["Alfred", "Alf"],
"01-04": ["Roar", "Roger"],
"01-05": ["Hanna", "Hanne"],
"01-06": ["Aslaug", "Åslaug"],
"01-07": ["Eldbjørg", "Knut"],
"01-08": ["Turid", "Torfinn"],
"01-09": ["Gunnar", "Gunn"],
"01-10": ["Sigmund", "Sigrun"],
"01-11": ["Børge", "Børre"],
"01-12": ["Reinhard", "Reinert"],
"01-13": ["Gisle", "Gislaug"],
"01-14": ["Herbjørn", "Herbjørg"],
"01-15": ["Laurits", "Laura"],
"01-16": ["Hjalmar", "Hilmar"],
"01-17": ["Anton", "Tønnes", "Tony"],
"01-18": ["Hildur", "Hild"],
"01-19": ["Marius", "Marion"],
"01-20": ["Fabian", "Sebastian"],
"01-21": ["Agnes", "Agnete"],
"01-22": ["Ivan", "Vanja"],
"01-23": ["Emilie", "Emil"],
"01-24": ["Joar", "Jarle"],
"01-25": ["Paul", "Pål"],
"01-26": ["Øystein", "Esten"],
"01-27": ["Gaute", "Gurli"],
"01-28": ["Karl", "Karoline"],
"01-29": ["Herdis", "Hermod"],
"01-30": ["Gunnhild", "Gunda"],
"01-31": ["Idun", "Ivar"],
"02-01": ["Birte", "Bjarte"],
"02-02": ["Jomar", "Jostein"],
"02-03": ["Ansgar", "Asgeir"],
"02-04": ["Veronika", "Vera"],
"02-05": ["Agate", "Ågot"],
"02-06": ["Dortea", "Dorte"],
"02-07": ["Rikard", "Rikke"],
"02-08": ["Åshild", "Åsne"],
"02-09": ["Lone", "Leikny"],
"02-10": ["Ingfrid", "Ingrid"],
"02-11": ["Bøye", "Bård"],
"02-12": ["Jordan", "Jørund"],
"02-13": ["Svanhild", "Svanlaug"],
"02-14": ["Valentin"],
"02-15": ["Sigfred", "Sigbjørn"],
"02-16": ["Julian", "Juliane"],
"02-17": ["Aleksandra", "Sandra"],
"02-18": ["Frøydis", "Frøya"],
"02-19": ["Ella", "Elna"],
"02-20": ["Vidar", "Vemund"],
"02-21": ["Samuel", "Selma"],
"02-22": ["Tina", "Tim"],
"02-23": ["Torstein", "Torunn"],
"02-24": ["Mattias", "Mattis"],
"02-25": ["Viktor", "Viktoria"],
"02-26": ["Inger", "Ingerid"],
"02-27": ["Laila", "Lill"],
"02-28": ["Marina", "Marin"],
"02-29": ["Lise", "Liss"],
"03-01": ["Audny", "Audun"],
"03-02": ["Erna", "Ernst"],
"03-03": ["Gunnvor", "Gunnvald"],
"03-04": ["Ada", "Oddhild"],
"03-05": ["Patrick", "Patricia"],
"03-06": ["Annfrid", "Andor"],
"03-07": ["Arnfinn", "Arnstein"],
"03-08": ["Beate", "Betty"],
"03-09": ["Sverre", "Sindre"],
"03-10": ["Edel", "Edle"],
"03-11": ["Edvin", "Ervin"],
"03-12": ["Gregor", "Gro"],
"03-13": ["Greta", "Grete"],
"03-14": ["Mathilde", "Mette"],
"03-15": ["Kristen", "Kristin"],
"03-16": ["Gudmund", "Gudny"],
"03-17": ["Gerda", "Gjertrud"],
"03-18": ["Aleksander", "Sander"],
"03-19": ["Josef", "Josefine"],
"03-20": ["Joakim", "Kim"],
"03-21": ["Bendik", "Bengt"],
"03-22": ["Paula", "Pauline"],
"03-23": ["Gerhard", "Gerd"],
"03-24": ["Ulrikke", "Ulla"],
"03-25": ["Maria", "Marie"],
"03-26": ["Gabriel", "Glenn"],
"03-27": ["Rudolf", "Rudi"],
"03-28": ["Åsta", "Ester"],
"03-29": ["Jonas", "Jonatan"],
"03-30": ["Holger", "Olga"],
"03-31": ["Vebjørn", "Vegard"],
"04-01": ["Aron", "Arve"],
"04-02": ["Sigvard", "Sivert"],
"04-03": ["Gunnvald", "Gunilla"],
"04-04": ["Nanna", "Nancy"],
"04-05": ["Irene", "Eirin"],
"04-06": ["Åsmund", "Asmund"],
"04-07": ["Oddvar", "Oddveig"],
"04-08": ["Asle", "Atle"],
"04-09": ["Rannveig", "Rønnaug"],
"04-10": ["Ingvald", "Ingveig"],
"04-11": ["Ylva", "Ulf"],
"04-12": ["Julius", "Julie"],
"04-13": ["Asta", "Astrid"],
"04-14": ["Ellinor", "Nora"],
"04-15": ["Oda", "Odin"],
"04-16": ["Magnus", "Mons"],
"04-17": ["Elise", "Else"],
"04-18": ["Eilif", "Eira"],
"04-19": ["Arnulf", "Arne"],
"04-20": ["Kjellaug", "Kjellrun"],
"04-21": ["Jeanette", "Jannike"],
"04-22": ["Oddgeir", "Oddny"],
"04-23": ["Georg", "Jørgen"],
"04-24": ["Albert", "Olaug"],
"04-25": ["Markus", "Mark"],
"04-26": ["Terese", "Tea"],
"04-27": ["Charles", "Charlotte"],
"04-28": ["Vivi", "Vivian"],
"04-29": ["Toralf", "Torolf"],
"04-30": ["Filip", "Filippa"],
"05-01": ["Valborg", "Ragna"],
"05-02": ["Åsa", "Åse"],
"05-03": ["Gjermund", "Gørill"],
"05-04": ["Monika", "Mona"],
"05-05": ["Gudbrand", "Gullborg"],
"05-06": ["Guri", "Gyri"],
"05-07": ["Maia", "Mai"],
"05-08": ["Åge", "Åke"],
"05-09": ["Kasper", "Jesper"],
"05-10": ["Asbjørg", "Asbjørn"],
"05-11": ["Magda", "Malvin"],
"05-12": ["Noralf", "Norvald"],
"05-13": ["Linda", "Line"],
"05-14": ["Kristoffer", "Krister"],
"05-15": ["Hallvard", "Halvor"],
"05-16": ["Sara", "Siren"],
"05-17": ["Harald", "Ragnhild"],
"05-18": ["Eirik", "Erik"],
"05-19": ["Torjus", "Truls"],
"05-20": ["Lilja", "Lilly"],
"05-21": ["Helene", "Ellen"],
"05-22": ["Henning", "Henny"],
"05-23": ["Oddlaug", "Oddrun"],
"05-24": ["Ester", "Iris"],
"05-25": ["Ragna", "Ragnar"],
"05-26": ["Annbjørg", "Annlaug"],
"05-27": ["Katinka", "Katrine"],
"05-28": ["Vilhelm", "William"],
"05-29": ["Magnar", "Magnhild"],
"05-30": ["Gard", "Geir"],
"05-31": ["Pernille", "Petter"],
"06-01": ["Juni", "Juniann"],
"06-02": ["Runa", "Runar"],
"06-03": ["Rasmus", "Rakel"],
"06-04": ["Heidi", "Heid"],
"06-05": ["Torbjørg", "Torbjørn"],
"06-06": ["Gustav", "Gyda"],
"06-07": ["Robert", "Robin"],
"06-08": ["Renate", "Renee"],
"06-09": ["Kolbein", "Kolbjørn"],
"06-10": ["Ingolf", "Ingunn"],
"06-11": ["Borgar", "Bjørg"],
"06-12": ["Sigfrid", "Sigrid"],
"06-13": ["Tone", "Tonje"],
"06-14": ["Erlend", "Erland"],
"06-15": ["Vigdis", "Viggo"],
"06-16": ["Torvald", "Trond"],
"06-17": ["Botolf", "Bodil"],
"06-18": ["Bjørnar", "Bjørnhild"],
"06-19": ["Erling", "Elling"],
"06-20": ["Salve", "Sølve"],
"06-21": ["Agnar", "Annar"],
"06-22": ["Håkon", "Maud"],
"06-23": ["Elfrid", "Eldrid"],
"06-24": ["Johannes", "Jone"],
"06-25": ["Ingve", "Yngve"],
"06-26": ["Jesper", "Jenny"],
"06-27": ["Arild", "Arill"],
"06-28": ["Lea", "Leo"],
"06-29": ["Peter", "Petra"],
"06-30": ["Solveig", "Solvor"],
"07-01": ["Ask", "Embla"],
"07-02": ["Kjartan", "Kjersti"],
"07-03": ["Andrea", "Andrine"],
"07-04": ["Ulrik", "Ulla"],
"07-05": ["Svein", "Svend"],
"07-06": ["Siv", "Synnøve"],
"07-07": ["Kjellfrid", "Kjellrun"],
"07-08": ["Sunniva", "Synnøve"],
"07-09": ["Gøran", "Jøran"],
"07-10": ["Anita", "Anja"],
"07-11": ["Kjetil", "Kjell"],
"07-12": ["Elias", "Eldar"],
"07-13": ["Mildrid", "Melissa"],
"07-14": ["Solfrid", "Solrun"],
"07-15": ["Oddmund", "Oddvin"],
"07-16": ["Susanne", "Sanna"],
"07-17": ["Guttorm", "Gorm"],
"07-18": ["Arnhild", "Arngeir"],
"07-19": ["Gerhard", "Gjert"],
"07-20": ["Margareta", "Margit"],
"07-21": ["Johanne", "Janne"],
"07-22": ["Malene", "Malin"],
"07-23": ["Brita", "Brit"],
"07-24": ["Kristine", "Kristin"],
"07-25": ["Jakob", "Jack"],
"07-26": ["Anna", "Anne"],
"07-27": ["Marit", "Mari"],
"07-28": ["Reidar", "Reidun"],
"07-29": ["Olav", "Ola"],
"07-30": ["Audvar", "Audgunn"],
"07-31": ["Elin", "Eline"],
"08-01": ["Peder", "Per"],
"08-02": ["Karen", "Karin"],
"08-03": ["Olve", "Oliver"],
"08-04": ["Arnljot", "Arvid"],
"08-05": ["Osvald", "Oskar"],
"08-06": ["Gunnlaug", "Gunnleiv"],
"08-07": ["Donata", "Dordi"],
"08-08": ["Eivind", "Eivin"],
"08-09": ["Ronny", "Roy"],
"08-10": ["Lorents", "Lars"],
"08-11": ["Torill", "Tordis"],
"08-12": ["Klara", "Klaus"],
"08-13": ["Hilde", "Hildegunn"],
"08-14": ["Hallgeir", "Hallgjerd"],
"08-15": ["Margot", "Mary"],
"08-16": ["Brynjulf", "Brynhild"],
"08-17": ["Verner", "Wenche"],
"08-18": ["Tormod", "Torodd"],
"08-19": ["Sigvart", "Sigve"],
"08-20": ["Bernhard", "Bernt"],
"08-21": ["Ragnvald", "Ragni"],
"08-22": ["Harriet", "Harry"],
"08-23": ["Signe", "Signy"],
"08-24": ["Belinda", "Bertil"],
"08-25": ["Ludvig", "Louise"],
"08-26": ["Orvald", "Orvind"],
"08-27": ["Roald", "Rolf"],
"08-28": ["Artur", "August"],
"08-29": ["Johan", "Jone"],
"08-30": ["Benjamin", "Ben"],
"08-31": ["Berta", "Birte"],
"09-01": ["Solbjørg", "Solgunn"],
"09-02": ["Lisa", "Lise"],
"09-03": ["Alise", "Alvhild"],
"09-04": ["Ida", "Idar"],
"09-05": ["Brede", "Brian"],
"09-06": ["Sollaug", "Silje"],
"09-07": ["Regine", "Regina"],
"09-08": ["Amalie", "Allan"],
"09-09": ["Trygve", "Tyra"],
"09-10": ["Tord", "Tor"],
"09-11": ["Dagny", "Dag"],
"09-12": ["Jofrid", "Jorid"],
"09-13": ["Stian", "Stig"],
"09-14": ["Ingebjørg", "Ingeborg"],
"09-15": ["Aslak", "Eskil"],
"09-16": ["Liv", "Hege"],
"09-17": ["Hildur", "Hild"],
"09-18": ["Henriette", "Henrik"],
"09-19": ["Konstanse", "Connie"],
"09-20": ["Fritjof", "Frida"],
"09-21": ["Trine", "Trygve"],
"09-22": ["Maurits", "Morten"],
"09-23": ["Snorre", "Snefrid"],
"09-24": ["Jan", "Jens"],
"09-25": ["Ingvar", "Yngvar"],
"09-26": ["Einar", "Eina"],
"09-27": ["Dagmar", "Dagrun"],
"09-28": ["Lena", "Lene"],
"09-29": ["Mikkel", "Mikal"],
"09-30": ["Helga", "Helge"],
"10-01": ["Rebekka", "Remi"],
"10-02": ["Live", "Liv"],
"10-03": ["Evald", "Evelyn"],
"10-04": ["Frans", "Frank"],
"10-05": ["Brynjar", "Boye"],
"10-06": ["Målfrid", "Møyfrid"],
"10-07": ["Birgitte", "Birgit"],
"10-08": ["Benedikte", "Bente"],
"10-09": ["Leif", "Leiv"],
"10-10": ["Fridtjof", "Frits"],
"10-11": ["Kevin", "Kennet"],
"10-12": ["Valter", "Vibeke"],
"10-13": ["Torgeir", "Terje"],
"10-14": ["Kai", "Kay"],
"10-15": ["Hedvig", "Hedda"],
"10-16": ["Flemming", "Finn"],
"10-17": ["Marja", "Marija"],
"10-18": ["Kord", "Kordelia"],
"10-19": ["Tora", "Tore"],
"10-20": ["Henrik", "Heine"],
"10-21": ["Bergljot", "Birger"],
"10-22": ["Karianne", "Karine"],
"10-23": ["Severin", "Søren"],
"10-24": ["Eilert", "Eilif"],
"10-25": ["Henriette", "Henrikke"],
"10-26": ["Amanda", "Amandus"],
"10-27": ["Sturla", "Sture"],
"10-28": ["Simon", "Simen"],
"10-29": ["Norbert", "Norunn"],
"10-30": ["Aksel", "Åskel"],
"10-31": ["Edit", "Eddy"],
"11-01": ["Veslemøy", "Vetle"],
"11-02": ["Tove", "Tuva"],
"11-03": ["Raymond", "Ragna"],
"11-04": ["Otto", "Ottar"],
"11-05": ["Egil", "Egon"],
"11-06": ["Leonard", "Lennart"],
"11-07": ["Ingebrigt", "Ingelin"],
"11-08": ["Ingvild", "Yngvild"],
"11-09": ["Tordis", "Teodor"],
"11-10": ["Gudbjørg", "Gudveig"],
"11-11": ["Martin", "Marte"],
"11-12": ["Torkjell", "Torkil"],
"11-13": ["Kirsten", "Kirsti"],
"11-14": ["Fredrik", "Fred"],
"11-15": ["Oddfrid", "Oddny"],
"11-16": ["Edmund", "Edgar"],
"11-17": ["Hugo", "Hogne"],
"11-18": ["Magne", "Magny"],
"11-19": ["Elisabeth", "Lisbet"],
"11-20": ["Halvard", "Halldis"],
"11-21": ["Mariann", "Marianne"],
"11-22": ["Cecilie", "Sissel"],
"11-23": ["Klement", "Klaus"],
"11-24": ["Gudrun", "Guro"],
"11-25": ["Katarina", "Kari"],
"11-26": ["Konrad", "Kurt"],
"11-27": ["Torlaug", "Torleif"],
"11-28": ["Ruben", "Rut"],
"11-29": ["Sofie", "Sonja"],
"11-30": ["Andreas", "Anders"],
"12-01": ["Arnold", "Arnt"],
"12-02": ["Borghild", "Borgny"],
"12-03": ["Sveinung", "Svein"],
"12-04": ["Barbara", "Barbro"],
"12-05": ["Stine", "Stein"],
"12-06": ["Nils", "Nikolai"],
"12-07": ["Hallfrid", "Hallstein"],
"12-08": ["Andrea", "Andre"],
"12-09": ["Anniken", "Anine"],
"12-10": ["Judit", "Jytte"],
"12-11": ["Daniel", "Dan"],
"12-12": ["Pia", "Peggy"],
"12-13": ["Lucia", "Lydia"],
"12-14": ["Steinar", "Stein"],
"12-15": ["Hilda", "Hilmar"],
"12-16": ["Adelheid", "Adele"],
"12-17": ["Inga", "Inge"],
"12-18": ["Kristoffer", "Kate"],
"12-19": ["Isak", "Iselin"],
"12-20": ["Abraham", "Amund"],
"12-21": ["Thomas", "Tom"],
"12-22": ["Ingemar", "Ingar"],
"12-23": ["Sigurd", "Sjur"],
"12-24": ["Adam", "Eva"],
"12-25": ["Første juledag"],
"12-26": ["Stefan", "Steffen"],
"12-27": ["Narve", "Natalie"],
"12-28": ["Unni", "Une"],
"12-29": ["Vidar", "Vebjørn"],
"12-30": ["David", "Diana"],
"12-31": ["Sylfest", "Sylvia"],
}

# ============================================================================
# NORSKE VITSER OG ORDTAK
# ============================================================================
VITSER = [
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

ORDTAK = [
"Borte bra, men hjemme best.",
"Den som venter på noe godt, venter ikke forgjeves.",
"Det er ikke gull alt som glimrer.",
"Øvelse gjør mester.",
"Bedre føre var enn etter snar.",
"Den som ler sist, ler best.",
"Smått er godt.",
"Man skal ikke skue hunden på hårene.",
"Ingen roser uten torner.",
"Sakte, men sikkert.",
"Etter regn kommer sol.",
"Det nytter ikke å gråte over spilt melk.",
"Morgenstund har gull i munn.",
"Alle gode ting er tre.",
"Den som graver en grav for andre, faller selv i den.",
]

# ============================================================================
# MOTIVERENDE SITATER
# ============================================================================
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

# ============================================================================
# FUN FACTS - MORSOMME FAKTA
# ============================================================================
FUN_FACTS = [
"🧠 Hjernen din bruker 20% av kroppens energi, selv om den bare utgjør 2% av vekten.",
"🐙 Blekkspruter har tre hjerter og blått blod!",
"🍯 Honning blir aldri dårlig. Arkeologer har funnet 3000 år gammel honning som fortsatt var spiselig.",
"🦈 Haier har eksistert lenger enn trær. De er over 400 millioner år gamle!",
"🌙 Det er fotspor på månen som vil vare i millioner av år fordi det ikke er vind der.",
"🐝 En bie besøker 50-100 blomster per tur for å samle nektar.",
"⚡ Et lyn er fem ganger varmere enn overflaten av solen!",
"🦋 Sommerfugler smaker med føttene.",
"🏔️ Mount Everest vokser med ca. 4mm hvert år.",
"🎸 Lyden av en gitar når deg før lyden av tordenen, selv om lynet skjer samtidig.",
"🐘 Elefanter er det eneste dyret som ikke kan hoppe.",
"🌍 Jorda roterer med 1670 km/t ved ekvator.",
"🦀 Hummere kan leve i over 100 år.",
"🌻 Solsikker følger solen gjennom dagen - det kalles heliotropisme.",
"🐧 Pingviner kan hoppe nesten 2 meter opp i luften!",
"🧊 90% av en isfjells masse er under vann.",
"🦩 Flamingoer er egentlig hvite - maten deres gjør dem rosa!",
"🌲 Det finnes et tre i Sverige som er over 9500 år gammelt.",
"🐨 Koalaer sover 18-22 timer i døgnet.",
"🌈 Det finnes ingen to snøfnugg som er helt like.",
"🦷 Tennene til en hai er like sterke som stål.",
"🦔 Pinnsvin har ca. 5000 pigger på kroppen.",
"🐄 Kuer har beste venner og blir stresset når de skilles.",
"🌊 Stillehavet er større enn all landjorda på jorden til sammen.",
"🦜 Papegøyer kan leve til de blir over 80 år.",
]

# ============================================================================
# DENNE DAGEN I HISTORIEN
# ============================================================================
DENNE_DAG_I_HISTORIEN = {
"01-01": ["1863: Abraham Lincoln signerte frigjøringsproklamasjonen", "1959: Cuba ble frigjort fra diktatur"],
"01-02": ["1959: Luna 1 ble det første romfartøyet til å forlate jordas gravitasjon"],
"01-03": ["1959: Alaska ble USAs 49. stat"],
"01-04": ["2004: NASAs Mars-rover Spirit landet på Mars"],
"01-05": ["1933: Byggingen av Golden Gate Bridge startet"],
"01-06": ["1838: Samuel Morse demonstrerte telegrafen for første gang"],
"01-07": ["1610: Galileo oppdaget Jupiters måner"],
"01-08": ["1889: Herman Hollerith patenterte hullkortmaskinen"],
"01-09": ["2007: Steve Jobs presenterte den første iPhone"],
"01-10": ["1946: Radar kontaktet månen for første gang"],
"01-11": ["1922: Insulin ble brukt til behandling av diabetes for første gang"],
"01-12": ["1966: 'Batman' TV-serien hadde premiere"],
"01-13": ["1898: Émile Zola publiserte 'J'Accuse!'"],
"01-14": ["1954: Marilyn Monroe giftet seg med Joe DiMaggio"],
"01-15": ["1759: British Museum åpnet for publikum"],
"01-16": ["1920: Alkoholforbudet startet i USA"],
"01-17": ["1706: Benjamin Franklin ble født", "1995: Jordskjelvet i Kobe, Japan"],
"01-18": ["1778: James Cook oppdaget Hawaii"],
"01-19": ["1983: Apple Lisa, den første PC med grafisk brukergrensesnitt, ble lansert"],
"01-20": ["1961: John F. Kennedy ble USAs president"],
"01-21": ["1976: Concorde startet passasjerflyvninger"],
"01-22": ["1984: Apple Macintosh ble lansert"],
"01-23": ["1849: Elizabeth Blackwell ble USAs første kvinnelige lege"],
"01-24": ["1848: Gullet ble oppdaget i California"],
"01-25": ["1924: De første vinter-OL åpnet i Chamonix, Frankrike"],
"01-26": ["1788: Det første skipet med europeere ankom Australia"],
"01-27": ["1880: Thomas Edison fikk patent på lyspæren", "1945: Auschwitz ble frigjort"],
"01-28": ["1986: Romfergen Challenger eksploderte"],
"01-29": ["1886: Karl Benz patenterte verdens første bil"],
"01-30": ["1933: Adolf Hitler ble Tysklands kansler"],
"01-31": ["1958: USA sendte sin første satellitt, Explorer 1"],
"02-01": ["2003: Romfergen Columbia forulykket"],
"02-02": ["1925: Siste del av hundesleden som fraktet serum til Nome, Alaska"],
"02-03": ["1959: 'The Day the Music Died' - Buddy Holly, Ritchie Valens og The Big Bopper døde"],
"02-04": ["2004: Facebook ble grunnlagt av Mark Zuckerberg"],
"02-05": ["1919: United Artists ble grunnlagt av Charlie Chaplin og andre"],
"02-06": ["1952: Dronning Elizabeth II ble dronning av Storbritannia"],
"02-07": ["1964: The Beatles ankom USA for første gang"],
"02-08": ["1910: Boy Scouts of America ble grunnlagt"],
"02-09": ["1964: The Beatles opptrådte på The Ed Sullivan Show"],
"02-10": ["1996: IBMs Deep Blue slo Garry Kasparov i sjakk"],
"02-11": ["1990: Nelson Mandela ble løslatt etter 27 år i fengsel"],
"02-12": ["1809: Charles Darwin og Abraham Lincoln ble født på samme dag"],
"02-13": ["1633: Galileo ankom Roma for å stilles for inkvisisjonen"],
"02-14": ["1876: Alexander Graham Bell og Elisha Gray søkte om patent på telefonen samme dag"],
"02-15": ["1965: Canada fikk sitt nåværende flagg med lønnebladet"],
"02-16": ["1923: Howard Carter åpnet Tutankhamons grav"],
"02-17": ["1959: USA lanserte Vanguard II, den første værsatellitten"],
"02-18": ["1930: Clyde Tombaugh oppdaget Pluto"],
"02-19": ["1878: Thomas Edison patenterte fonografen"],
"02-20": ["1962: John Glenn ble den første amerikaneren i bane rundt jorda"],
"02-21": ["1848: Det kommunistiske manifest ble publisert"],
"02-22": ["1980: USAs ishockeylag slo Sovjetunionen - 'Miracle on Ice'"],
"02-23": ["1455: Gutenberg-bibelen ble trykt - den første trykte boken"],
"02-24": ["1989: Første flyvning med Boeing 747-400"],
"02-25": ["1836: Samuel Colt patenterte revolveren"],
"02-26": ["1815: Napoleon rømte fra eksil på Elba"],
"02-27": ["1933: Riksdagsbrannen i Berlin"],
"02-28": ["1953: Watson og Crick oppdaget DNA-strukturen"],
"02-29": ["1940: Hattie McDaniel ble den første afroamerikaner som vant en Oscar"],
"03-01": ["1872: Yellowstone ble verdens første nasjonalpark"],
"03-02": ["1877: Rutherford B. Hayes ble USAs president etter det mest omstridte valget i historien"],
"03-03": ["1847: Alexander Graham Bell ble født"],
"03-04": ["1789: USAs grunnlov trådte i kraft"],
"03-05": ["1946: Winston Churchill holdt sin berømte 'jerntepe'-tale"],
"03-06": ["1899: Aspirin ble patentert av Bayer"],
"03-07": ["1876: Alexander Graham Bell fikk patent på telefonen"],
"03-08": ["1917: Den russiske revolusjonen startet"],
"03-09": ["1959: Barbie-dukken ble lansert"],
"03-10": ["1876: Alexander Graham Bell gjennomførte den første telefonsamtalen"],
"03-11": ["2011: Jordskjelv og tsunami rammet Japan"],
"03-12": ["1894: Coca-Cola ble solgt i flasker for første gang"],
"03-13": ["1781: William Herschel oppdaget planeten Uranus"],
"03-14": ["1879: Albert Einstein ble født", "Pi-dagen (3.14)"],
"03-15": ["44 f.Kr.: Julius Cæsar ble myrdet"],
"03-16": ["1802: United States Military Academy (West Point) ble etablert"],
"03-17": ["461: Sankt Patricks dag - Irlands nasjonaldag"],
"03-18": ["1965: Aleksei Leonov ble det første mennesket til å gå i verdensrommet"],
"03-19": ["1918: USA innførte sommertid for første gang"],
"03-20": ["1852: 'Onkel Toms hytte' ble publisert"],
"03-21": ["1871: Otto von Bismarck ble Tysklands første kansler"],
"03-22": ["1895: Lumiére-brødrene viste film offentlig for første gang"],
"03-23": ["1983: President Reagan lanserte 'Star Wars'-programmet"],
"03-24": ["1989: Exxon Valdez-ulykken i Alaska"],
"03-25": ["1807: Storbritannia avskaffet slavehandel"],
"03-26": ["1979: Egypt og Israel signerte fredsavtalen"],
"03-27": ["1968: Jurij Gagarin omkom i en flyulykke"],
"03-28": ["1979: Harrisburg-ulykken (Three Mile Island)"],
"03-29": ["1974: Terrakottahæren ble oppdaget i Kina"],
"03-30": ["1867: USA kjøpte Alaska fra Russland"],
"03-31": ["1889: Eiffeltårnet ble offisielt åpnet"],
"04-01": ["1976: Apple ble grunnlagt av Steve Jobs og Steve Wozniak"],
"04-02": ["1513: Juan Ponce de León oppdaget Florida"],
"04-03": ["1860: Pony Express startet postlevering i USA"],
"04-04": ["1968: Martin Luther King Jr. ble drept"],
"04-05": ["1955: Winston Churchill trakk seg som Storbritannias statsminister"],
"04-06": ["1896: De første moderne olympiske leker åpnet i Athen"],
"04-07": ["1948: Verdens helseorganisasjon (WHO) ble grunnlagt"],
"04-08": ["1820: Venus de Milo ble oppdaget på den greske øya Milos"],
"04-09": ["1865: Den amerikanske borgerkrigen endte"],
"04-10": ["1912: RMS Titanic la ut på sin første og siste reise"],
"04-11": ["1970: Apollo 13 ble skutt opp"],
"04-12": ["1961: Jurij Gagarin ble det første mennesket i verdensrommet"],
"04-13": ["1742: Händels 'Messias' hadde premiere i Dublin"],
"04-14": ["1912: RMS Titanic traff isfjellet", "1865: Abraham Lincoln ble skutt"],
"04-15": ["1912: RMS Titanic sank", "1452: Leonardo da Vinci ble født"],
"04-16": ["1943: Albert Hofmann oppdaget LSD-rusen ved et uhell"],
"04-17": ["1961: Bay of Pigs-invasjonen startet"],
"04-18": ["1906: San Francisco-jordskjelvet"],
"04-19": ["1775: Den amerikanske revolusjonen startet"],
"04-20": ["1889: Adolf Hitler ble født"],
"04-21": ["753 f.Kr.: Roma ble grunnlagt (ifølge legenden)"],
"04-22": ["1970: Første jordensdag ble feiret"],
"04-23": ["1564: William Shakespeare ble født (og døde)"],
"04-24": ["1990: Hubble-teleskopet ble skutt opp"],
"04-25": ["1953: Watson og Crick publiserte DNA-strukturen"],
"04-26": ["1986: Tsjernobyl-ulykken"],
"04-27": ["1994: Sør-Afrika holdt sitt første frie valg"],
"04-28": ["1945: Benito Mussolini ble henrettet"],
"04-29": ["1945: Adolf Hitler giftet seg med Eva Braun"],
"04-30": ["1789: George Washington ble innsatt som USAs første president"],
"05-01": ["1931: Empire State Building ble offisielt åpnet"],
"05-02": ["2011: Osama bin Laden ble drept"],
"05-03": ["1937: 'Tatt av vinden' av Margaret Mitchell vant Pulitzer-prisen"],
"05-04": ["1979: Margaret Thatcher ble Storbritannias første kvinnelige statsminister"],
"05-05": ["1961: Alan Shepard ble den første amerikaneren i verdensrommet"],
"05-06": ["1937: Hindenburg-katastrofen"],
"05-07": ["1945: Nazi-Tyskland overga seg betingelsesløst"],
"05-08": ["1945: VE-Day - Seiersdagen i Europa"],
"05-09": ["1754: Benjamin Franklin publiserte den første politiske tegneserien i USA"],
"05-10": ["1869: Den første transkontinentale jernbanen ble fullført i USA"],
"05-11": ["330: Konstantinopel ble hovedstad i Romerriket"],
"05-12": ["1949: Berlinblokaden ble hevet"],
"05-13": ["1981: Pave Johannes Paul II ble skutt på Petersplassen"],
"05-14": ["1796: Edward Jenner utviklet den første vaksinen"],
"05-15": ["1928: Mickey Mouse dukket opp for første gang"],
"05-16": ["1929: De første Oscar-utdelingene ble holdt"],
"05-17": ["1814: Norges grunnlov ble signert på Eidsvoll"],
"05-18": ["1980: Mount St. Helens hadde utbrudd"],
"05-19": ["1536: Anne Boleyn ble henrettet"],
"05-20": ["1873: Levi Strauss patenterte blå jeans"],
"05-21": ["1927: Charles Lindbergh fullførte første solo-flyging over Atlanterhavet"],
"05-22": ["1906: Wright-brødrene fikk patent på flyet sitt"],
"05-23": ["1934: Bonnie og Clyde ble drept"],
"05-24": ["1844: Samuel Morse sendte det første telegrammet"],
"05-25": ["1977: Star Wars hadde premiere"],
"05-26": ["1897: Bram Stokers 'Dracula' ble publisert"],
"05-27": ["1937: Golden Gate Bridge ble åpnet"],
"05-28": ["1987: Mathias Rust landet et småfly på Den røde plass i Moskva"],
"05-29": ["1953: Edmund Hillary og Tenzing Norgay nådde toppen av Mount Everest"],
"05-30": ["1431: Jeanne d'Arc ble brent på bålet"],
"05-31": ["1911: RMS Titanic ble sjøsatt"],
"06-01": ["1967: The Beatles ga ut 'Sgt. Pepper's Lonely Hearts Club Band'"],
"06-02": ["1953: Dronning Elizabeth II ble kronet"],
"06-03": ["1965: Ed White ble den første amerikaneren til å gå i verdensrommet"],
"06-04": ["1989: Massakren på Den himmelske freds plass i Beijing"],
"06-05": ["1981: De første AIDS-tilfellene ble rapportert"],
"06-06": ["1944: D-dagen - Invasjonen av Normandie"],
"06-07": ["1942: Slaget ved Midway endte"],
"06-08": ["632: Profeten Muhammad døde"],
"06-09": ["68: Keiser Nero begikk selvmord"],
"06-10": ["1935: Anonyme Alkoholikere ble grunnlagt"],
"06-11": ["1962: Frank Morris og brødrene Anglin rømte fra Alcatraz"],
"06-12": ["1942: Anne Frank begynte å skrive dagboken sin"],
"06-13": ["1983: Pioneer 10 passerte Neptuns bane"],
"06-14": ["1777: Det amerikanske flagget ble vedtatt"],
"06-15": ["1215: Magna Carta ble signert"],
"06-16": ["1903: Ford Motor Company ble grunnlagt"],
"06-17": ["1972: Watergate-innbruddet"],
"06-18": ["1815: Slaget ved Waterloo"],
"06-19": ["1865: Juneteenth - Frigjøringsdagen for slaver i Texas"],
"06-20": ["1782: Den amerikanske kongressens store segl ble vedtatt"],
"06-21": ["1788: USAs grunnlov ble ratifisert"],
"06-22": ["1941: Operasjon Barbarossa - Nazi-Tyskland angrep Sovjetunionen"],
"06-23": ["1868: Christopher Latham Sholes patenterte skrivemaskinen"],
"06-24": ["1948: Berlin-blokaden startet"],
"06-25": ["1950: Koreakrigen startet"],
"06-26": ["1974: Det første produktet med strekkode ble skannet"],
"06-27": ["1967: Verdens første minibank ble åpnet i London"],
"06-28": ["1914: Skuddene i Sarajevo startet første verdenskrig"],
"06-29": ["2007: Første iPhone ble lansert"],
"06-30": ["1936: 'Tatt av vinden' ble publisert"],
"07-01": ["1867: Canada ble en selvstendig nasjon"],
"07-02": ["1937: Amelia Earhart forsvant over Stillehavet"],
"07-03": ["1863: Slaget ved Gettysburg endte"],
"07-04": ["1776: USAs uavhengighetserklæring ble signert"],
"07-05": ["1996: Dolly the sheep ble født - det første klonede pattedyret"],
"07-06": ["1885: Louis Pasteur testet vellykket rabiesvaksinen"],
"07-07": ["2005: Terrorangrepene i London"],
"07-08": ["1889: Wall Street Journal ble publisert for første gang"],
"07-09": ["1877: Første Wimbledon-turnering"],
"07-10": ["1962: Telstar 1, den første kommunikasjonssatellitten, ble skutt opp"],
"07-11": ["1804: Alexander Hamilton ble drept i duell med Aaron Burr"],
"07-12": ["1862: Congredalmedaljen ble opprettet"],
"07-13": ["1985: Live Aid-konsertene"],
"07-14": ["1789: Storming av Bastillen - Den franske revolusjonen startet"],
"07-15": ["1099: Jerusalem ble erobret under det første korstoget"],
"07-16": ["1969: Apollo 11 ble skutt opp mot månen"],
"07-17": ["1955: Disneyland åpnet"],
"07-18": ["64: Romas brann startet under keiser Nero"],
"07-19": ["1799: Rosetta-steinen ble oppdaget"],
"07-20": ["1969: Neil Armstrong og Buzz Aldrin landet på månen"],
"07-21": ["1969: Neil Armstrong gikk på månen"],
"07-22": ["1934: FBI-agenter drepte John Dillinger"],
"07-23": ["1903: Ford solgte sin første bil, Modell A"],
"07-24": ["1969: Apollo 11 returnerte trygt til jorda"],
"07-25": ["1978: Verdens første prøverørsbarn ble født"],
"07-26": ["1945: Potsdam-deklarasjonen ble utstedt"],
"07-27": ["1953: Våpenhvilen i Koreakrigen ble signert"],
"07-28": ["1914: Første verdenskrig startet"],
"07-29": ["1981: Prins Charles og Lady Diana giftet seg"],
"07-30": ["1619: Første representative forsamling i Amerika møttes"],
"07-31": ["1790: Det første amerikanske patentet ble utstedt"],
"08-01": ["1981: MTV startet sendinger"],
"08-02": ["1990: Irak invaderte Kuwait"],
"08-03": ["1492: Christopher Columbus la ut på sin første reise"],
"08-04": ["1944: Anne Frank og familien ble arrestert"],
"08-05": ["1963: Prøvestansavtalen for atomvåpen ble signert"],
"08-06": ["1945: Atombomben ble sluppet over Hiroshima"],
"08-07": ["1942: Slaget om Guadalcanal startet"],
"08-08": ["1974: Richard Nixon annonserte sin avgang"],
"08-09": ["1945: Atombomben ble sluppet over Nagasaki"],
"08-10": ["1846: Smithsonian Institution ble grunnlagt"],
"08-11": ["1999: Total solformørkelse over Europa"],
"08-12": ["1981: IBM lanserte sin første personlige datamaskin"],
"08-13": ["1961: Byggingen av Berlinmuren startet"],
"08-14": ["1945: Japan overga seg - Andre verdenskrig endte"],
"08-15": ["1969: Woodstock-festivalen startet"],
"08-16": ["1977: Elvis Presley døde"],
"08-17": ["1978: Første ballongferd over Atlanterhavet"],
"08-18": ["1920: Den 19. grunnlovsendringen ga amerikanske kvinner stemmerett"],
"08-19": ["1839: Daguerreotypi-prosessen ble offentliggjort"],
"08-20": ["1977: Voyager 2 ble skutt opp"],
"08-21": ["1959: Hawaii ble USAs 50. stat"],
"08-22": ["1862: Røde Kors ble grunnlagt"],
"08-23": ["1939: Molotov-Ribbentrop-pakten ble signert"],
"08-24": ["79: Mount Vesuvius hadde utbrudd og begravde Pompeii"],
"08-25": ["1835: Månebløffen - New York Sun publiserte at det var liv på månen"],
"08-26": ["1920: Kvinner i USA fikk stemmerett"],
"08-27": ["1883: Krakatoa hadde utbrudd"],
"08-28": ["1963: Martin Luther King Jr. holdt 'I Have a Dream'-talen"],
"08-29": ["2005: Orkanen Katrina traff kysten av USA"],
"08-30": ["1963: Den røde telefonen mellom Washington og Moskva ble installert"],
"08-31": ["1997: Prinsesse Diana døde i en bilulykke i Paris"],
"09-01": ["1939: Andre verdenskrig startet - Tyskland invaderte Polen"],
"09-02": ["1945: Japan signerte overgivelsespapirene"],
"09-03": ["1939: Storbritannia og Frankrike erklærte krig mot Tyskland"],
"09-04": ["1998: Google ble grunnlagt"],
"09-05": ["1977: Voyager 1 ble skutt opp"],
"09-06": ["1901: President McKinley ble skutt"],
"09-07": ["1940: The Blitz - Bombingen av London startet"],
"09-08": ["1966: Star Trek hadde premiere på TV"],
"09-09": ["1976: Mao Zedong døde"],
"09-10": ["2008: Large Hadron Collider ble aktivert for første gang"],
"09-11": ["2001: Terrorangrepene på World Trade Center og Pentagon"],
"09-12": ["1940: Lascaux-hulen med hulemalerier ble oppdaget"],
"09-13": ["1993: Oslo-avtalen ble signert av Israel og PLO"],
"09-14": ["1814: Francis Scott Key skrev 'The Star-Spangled Banner'"],
"09-15": ["1935: Nürnberglovene ble innført i Nazi-Tyskland"],
"09-16": ["1620: Mayflower la ut fra Plymouth, England"],
"09-17": ["1787: USAs grunnlov ble signert"],
"09-18": ["1970: Jimi Hendrix døde"],
"09-19": ["1893: New Zealand ble det første landet som ga kvinner stemmerett"],
"09-20": ["1854: Slaget ved Alma under Krimkrigen"],
"09-21": ["1937: Hobbiten av J.R.R. Tolkien ble publisert"],
"09-22": ["1862: Lincoln kunngjorde frigjøringsproklamasjonen"],
"09-23": ["1846: Neptun ble oppdaget"],
"09-24": ["1789: Høyesterett i USA ble opprettet"],
"09-25": ["1513: Vasco Núñez de Balboa oppdaget Stillehavet"],  # Added comment symbol
"09-26": ["1983: Stanislav Petrov forhindret atomkrig ved å ignorere falsk alarm"],
"09-27": ["1998: Google ble offentlig lansert"],
"09-28": ["1928: Alexander Fleming oppdaget penicillin"],
"09-29": ["1829: Londons Metropolitan Police ble etablert"],
"09-30": ["1955: James Dean døde i en bilulykke"],
"10-01": ["1908: Ford Model T ble lansert"],
"10-02": ["1950: Peanuts (Knøttene) ble publisert for første gang"],
"10-03": ["1990: Tyskland ble gjenforent"],
"10-04": ["1957: Sputnik 1, den første satellitten, ble skutt opp"],
"10-05": ["1962: The Beatles ga ut sin første singel, 'Love Me Do'"],
"10-06": ["1973: Yom Kippur-krigen startet"],
"10-07": ["1959: Første bilder av månens bakside ble tatt av Luna 3"],
"10-08": ["1871: Den store brannen i Chicago startet"],
"10-09": ["1967: Che Guevara ble henrettet"],
"10-10": ["1964: De olympiske leker i Tokyo åpnet"],
"10-11": ["1975: Saturday Night Live hadde premiere"],
"10-12": ["1492: Christopher Columbus ankom Amerika"],
"10-13": ["1307: Tempelridderne ble arrestert - opprinnelsen til fredag 13."],
"10-14": ["1066: Slaget ved Hastings"],
"10-15": ["1815: Napoleon ankom eksil på St. Helena"],
"10-16": ["1793: Marie Antoinette ble henrettet"],
"10-17": ["1989: Jordskjelvet i San Francisco under World Series"],
"10-18": ["1867: USA overtok Alaska fra Russland"],
"10-19": ["1781: Britene overga seg ved Yorktown"],
"10-20": ["1973: Sydney Opera House åpnet"],
"10-21": ["1879: Thomas Edison fullførte den første praktiske lyspæren"],
"10-22": ["1962: President Kennedy kunngjorde cubakrisen"],
    "10-23": ["1983: Bombeangrepet i Beirut drepte 241 amerikanske soldater"],
    "10-24": ["1945: FN ble offisielt grunnlagt"],
    "10-25": ["1854: Kavaleriangrep i Krimkrigen - 'The Charge of the Light Brigade'"],
    "10-26": ["1881: Skuddvekslingen ved O.K. Corral"],
    "10-27": ["1904: New Yorks første undergrunnsbane åpnet"],
    "10-28": ["1886: Frihetsgudinnen ble avduket"],
    "10-29": ["1929: Black Tuesday - Børskrakket"],
    "10-30": ["1938: Orson Welles' 'Klodenes kamp' skapte panikk"],
    "10-31": ["1517: Martin Luther slo opp sine 95 teser"],
    "11-01": ["1952: USA detonerte den første hydrogenbomben"],
    "11-02": ["1947: Spruce Goose fløy for første og eneste gang"],
    "11-03": ["1957: Laika ble det første dyret i bane rundt jorda"],
    "11-04": ["1922: Tutankhamons grav ble oppdaget"],
    "11-05": ["1605: Kruttkomplottets dag i England"],
    "11-06": ["1860: Abraham Lincoln ble valgt til president"],
    "11-07": ["1917: Oktoberrevolusjonen i Russland"],
    "11-08": ["1895: Wilhelm Röntgen oppdaget røntgenstråler"],
    "11-09": ["1989: Berlinmuren falt"],
    "11-10": ["1969: Sesame Street hadde premiere"],
    "11-11": ["1918: Første verdenskrig endte"],
    "11-12": ["1990: Tim Berners-Lee publiserte forslaget til World Wide Web"],
    "11-13": ["1985: Vulkanen Nevado del Ruiz hadde utbrudd i Colombia"],
    "11-14": ["1889: Nellie Bly begynte sin reise rundt verden på 72 dager"],
    "11-15": ["1971: Intel lanserte den første mikroprosessoren"],
    "11-16": ["1945: UNESCO ble grunnlagt"],
    "11-17": ["1970: Datamusen ble patentert"],
    "11-18": ["1928: Mickey Mouse debuterte i 'Steamboat Willie'"],
    "11-19": ["1863: Gettysburg-talen av Abraham Lincoln"],
    "11-20": ["1945: Nürnberg-prosessen startet"],
    "11-21": ["1877: Thomas Edison annonserte fonografen"],
    "11-22": ["1963: John F. Kennedy ble drept i Dallas"],
    "11-23": ["1963: Doctor Who hadde premiere på BBC"],
    "11-24": ["1859: Charles Darwin publiserte 'Artenes opprinnelse'"],
    "11-25": ["1952: Agatha Christies 'Musefellen' hadde premiere"],
    "11-26": ["1922: Howard Carter åpnet Tutankhamons gravkammer"],
    "11-27": ["1895: Alfred Nobels testament etablerte Nobelprisen"],
    "11-28": ["1520: Magellan nådde Stillehavet"],
    "11-29": ["1929: Richard Byrd fløy over Sydpolen"],
    "11-30": ["1939: Vinterkrigen mellom Sovjet og Finland startet"],
    "12-01": ["1955: Rosa Parks nektet å gi opp setet sitt på bussen"],
    "12-02": ["1942: Den første kontrollerte kjernereakjonen"],
    "12-03": ["1992: Den første SMS-meldingen ble sendt"],
    "12-04": ["1872: Mary Celeste ble funnet forlatt til havs"],
    "12-05": ["1933: Alkoholforbudet i USA ble opphevet"],
    "12-06": ["1877: Thomas Edison demonstrerte fonografen"],
    "12-07": ["1941: Pearl Harbor ble angrepet"],
    "12-08": ["1980: John Lennon ble drept"],
    "12-09": ["1979: Kopper ble erklært utryddet"],
    "12-10": ["1901: De første Nobelprisene ble utdelt"],
    "12-11": ["1936: Edward VIII abdiserte for å gifte seg med Wallis Simpson"],
    "12-12": ["1901: Guglielmo Marconi sendte første radiosignal over Atlanterhavet"],
    "12-13": ["2003: Saddam Hussein ble tatt til fange"],
    "12-14": ["1911: Roald Amundsen nådde Sydpolen"],
    "12-15": ["1939: 'Tatt av vinden' hadde premiere"],
    "12-16": ["1773: Boston Tea Party"],
    "12-17": ["1903: Wright-brødrene fløy for første gang"],
    "12-18": ["1865: Det 13. grunnlovstillegget avskaffet slaveri i USA"],
    "12-19": ["1843: 'A Christmas Carol' av Charles Dickens ble publisert"],
    "12-20": ["1860: South Carolina ble første stat til å melde seg ut av USA"],
    "12-21": ["1968: Apollo 8 ble skutt opp - første mennesker rundt månen"],
    "12-22": ["1849: Fjodor Dostojevskij ble 'henrettet' - men benådet i siste sekund"],
    "12-23": ["1888: Vincent van Gogh skadet sitt eget øre"],
    "12-24": ["1914: Julevåpenhvilen under første verdenskrig"],
    "12-25": ["1991: Sovjetunionen ble offisielt oppløst"],
    "12-26": ["2004: Det katastrofale jordskjelvet og tsunamien i Det indiske hav"],
    "12-27": ["1831: HMS Beagle la ut på reisen med Charles Darwin"],
    "12-28": ["1895: Lumiére-brødrene holdt den første offentlige filmvisningen"],
    "12-29": ["1890: Massakren ved Wounded Knee"],
    "12-30": ["1922: Sovjetunionen ble offisielt dannet"],
    "12-31": ["1879: Thomas Edison demonstrerte lyspæren offentlig"],
}

# ============================================================================
# VÆRSYMBOLER
# ============================================================================

VAER_SYMBOLER = {
    "clearsky": "☀️ Klar himmel",
    "fair": "🌤️ Lettskyet",
    "partlycloudy": "⛅ Delvis skyet",
    "cloudy": "☁️ Overskyet",
    "rain": "🌧️ Regn",
    "lightrain": "🌦️ Lett regn",
    "heavyrain": "🌧️ Kraftig regn",
    "lightrainshowers": "🌦️ Lette regnbyger",
    "rainshowers": "🌧️ Regnbyger",
    "heavyrainshowers": "🌧️ Kraftige regnbyger",
    "snow": "❄️ Snø",
    "lightsnow": "🌨️ Lett snø",
    "heavysnow": "❄️ Kraftig snø",
    "snowshowers": "🌨️ Snøbyger",
    "sleet": "🌨️ Sludd",
    "sleetshowers": "🌨️ Sluddbyger",
    "fog": "🌫️ Tåke",
    "thunder": "⛈️ Torden",
    "rainandthunder": "⛈️ Regn og torden",
    "snowandthunder": "⛈️ Snø og torden",
    "sleetandthunder": "⛈️ Sludd og torden",
}

# Norske dager og måneder
DAGER = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
MAANEDER = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember"
]

# ============================================================================
# FUNKSJONER
# ============================================================================

def hent_vaer(by):
    """Henter værdata fra Meteorologisk institutt."""
    try:
        by_lower = by.lower()
        by_data = None
        for city_name, coords in BY_KOORDINATER.items():
            if city_name.lower() == by_lower:
                by_data = coords
                break

        if not by_data:
            by_data = BY_KOORDINATER["Moss"]
            print(f"By '{by}' ikke funnet, bruker Moss")

        lat = by_data["lat"]
        lon = by_data["lon"]

        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        headers = {"User-Agent": "MorgenBot/2.0 github.com/morgenbot"}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        timeseries = data["properties"]["timeseries"][0]
        instant = timeseries["data"]["instant"]["details"]

        temp = instant["air_temperature"]
        vind = instant["wind_speed"]
        fuktighet = instant.get("relative_humidity", None)
        lufttrykk = instant.get("air_pressure_at_sea_level", None)

        # Hent værsymbol
        if "next_1_hours" in timeseries["data"]:
            symbol_code = timeseries["data"]["next_1_hours"]["summary"]["symbol_code"]
        elif "next_6_hours" in timeseries["data"]:
            symbol_code = timeseries["data"]["next_6_hours"]["summary"]["symbol_code"]
        else:
            symbol_code = "cloudy"

        symbol_base = symbol_code.split("_")[0]
        symbol = VAER_SYMBOLER.get(symbol_base, f"❓ {symbol_code}")

        # Klesanbefaling
        if temp < -15:
            klaer = "🥶 EKSTREMT kaldt! Full vinterutrustning, begrens tid ute"
        elif temp < -10:
            klaer = "🧥 Veldig kaldt! Boblejakke, lue, votter, skjerf og ullundertøy"
        elif temp < 0:
            klaer = "🧥 Kaldt! Varm jakke, lue og hansker anbefales"
        elif temp < 5:
            klaer = "🧥 Kjølig. Jakke og lag-på-lag"
        elif temp < 10:
            klaer = "🧥 Friskt. Lett jakke eller tykk genser"
        elif temp < 15:
            klaer = "👕 Behagelig. Genser eller lett jakke"
        elif temp < 20:
            klaer = "👕 Fint vær! T-skjorte og lett bukse"
        elif temp < 25:
            klaer = "☀️ Varmt! T-skjorte og shorts"
        else:
            klaer = "🥵 Veldig varmt! Lett, luftig klær. Husk solkrem!"

        if "rain" in symbol_code.lower() or "sleet" in symbol_code.lower():
            klaer += " 🌂 Ta med paraply!"
        if "snow" in symbol_code.lower():
            klaer += " ❄️ Vær obs på glatte veier!"

        # Føles som temperatur (wind chill)
        if vind > 0 and temp < 10:
            feels_like = 13.12 + 0.6215 * temp - 11.37 * (vind * 3.6)**0.16 + 0.3965 * temp * (vind * 3.6)**0.16
        else:
            feels_like = temp

        return {
            "temp": temp,
            "feels_like": round(feels_like, 1),
            "vind": vind,
            "fuktighet": fuktighet,
            "lufttrykk": lufttrykk,
            "symbol": symbol,
            "symbol_code": symbol_code,
            "klaer": klaer,
        }

    except Exception as e:
        print(f"Feil ved henting av vær: {e}")
        return {"error": str(e)}


def hent_soloppgang_solnedgang(by):
    """Henter soloppgang og solnedgang tider."""
    try:
        by_data = BY_KOORDINATER.get(by, BY_KOORDINATER["Moss"])
        lat = by_data["lat"]
        lon = by_data["lon"]

        dato = datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.met.no/weatherapi/sunrise/3.0/sun?lat={lat}&lon={lon}&date={dato}&offset=+01:00"
        headers = {"User-Agent": "MorgenBot/2.0"}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        sunrise = data["properties"]["sunrise"]["time"]
        sunset = data["properties"]["sunset"]["time"]

        # Parse og formater tider
        sunrise_dt = datetime.fromisoformat(sunrise.replace("Z", "+00:00"))
        sunset_dt = datetime.fromisoformat(sunset.replace("Z", "+00:00"))

        # Beregn dagslys timer
        daylight = sunset_dt - sunrise_dt
        hours = daylight.seconds // 3600
        minutes = (daylight.seconds % 3600) // 60

        return {
            "sunrise": sunrise_dt.strftime("%H:%M"),
            "sunset": sunset_dt.strftime("%H:%M"),
            "daylight_hours": hours,
            "daylight_minutes": minutes,
        }

    except Exception as e:
        print(f"Feil ved henting av sol-data: {e}")
        return None


def hent_nyheter_utvidet():
    """Henter nyheter fra flere kilder med kategorier."""
    try:
        nyheter = {
            "topp": [],
            "verden": [],
            "sport": [],
            "kultur": [],
            "tech": [],
        }

        feeds = {
            "topp": [
                "https://www.nrk.no/toppsaker.rss",
                "https://www.vg.no/rss/feed/?categories=1069&limit=10",
            ],
            "verden": [
                "https://www.nrk.no/verden/toppsaker.rss",
            ],
            "sport": [
                "https://www.nrk.no/sport/toppsaker.rss",
                "https://www.vg.no/rss/feed/?categories=1070&limit=5",
            ],
            "kultur": [
                "https://www.nrk.no/kultur/toppsaker.rss",
            ],
            "tech": [
                "https://www.nrk.no/viten/toppsaker.rss",
            ],
        }

        for kategori, urls in feeds.items():
            for url in urls:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:3]:
                        if len(nyheter[kategori]) < 5:
                            nyheter[kategori].append({
                                "tittel": entry.title,
                                "link": entry.link,
                                "kilde": "NRK" if "nrk.no" in url else "VG"
                            })
                except Exception as e:
                    print(f"Feil ved RSS {url}: {e}")
                    continue

        return nyheter

    except Exception as e:
        print(f"Feil ved henting av nyheter: {e}")
        return {"topp": [], "verden": [], "sport": [], "kultur": [], "tech": []}


def hent_aksjer():
    """Henter aksjer og valutakurser."""
    try:
        aksjer_info = []

        aksjer = [
            ("^OSEAX", "Oslo Børs"),
            ("EQNR.OL", "Equinor"),
            ("DNB.OL", "DNB"),
            ("TEL.OL", "Telenor"),
            ("MOWI.OL", "Mowi"),
            ("NHY.OL", "Norsk Hydro"),
            ("YAR.OL", "Yara"),
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

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
                print(f"Feil ved {symbol}: {e}")
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
            print(f"Feil ved valutakurser: {e}")

        return {"aksjer": aksjer_info, "valuta": valuta}

    except Exception as e:
        print(f"Feil ved henting av aksjer: {e}")
        return {"aksjer": [], "valuta": []}


def hent_krypto():
    """Henter kryptovaluta priser."""
    try:
        krypto_info = []

        coins = ["bitcoin", "ethereum", "solana", "dogecoin", "cardano"]

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins)}&vs_currencies=nok,usd&include_24hr_change=true"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        emoji_map = {
            "bitcoin": "₿",
            "ethereum": "Ξ",
            "solana": "◎",
            "dogecoin": "🐕",
            "cardano": "₳",
        }

        for coin in coins:
            if coin in data:
                pris_nok = data[coin].get("nok", 0)
                endring = data[coin].get("nok_24h_change", 0)

                emoji = emoji_map.get(coin, "🪙")
                trend = "📈" if endring >= 0 else "📉"
                endring_str = f"+{endring:.1f}%" if endring >= 0 else f"{endring:.1f}%"

                krypto_info.append({
                    "navn": coin.capitalize(),
                    "emoji": emoji,
                    "pris": pris_nok,
                    "endring": endring,
                    "endring_str": endring_str,
                    "trend": trend
                })

        return krypto_info

    except Exception as e:
        print(f"Feil ved krypto: {e}")
        return []


def hent_strompris(by):
    """Henter dagens strømpriser."""
    try:
        by_data = BY_KOORDINATER.get(by, BY_KOORDINATER["Moss"])
        sone = by_data.get("strompris_sone", "NO1")

        dato = datetime.now().strftime("%Y/%m-%d")
        url = f"https://www.hvakosterstrommen.no/api/v1/prices/{dato}_{sone}.json"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        # Finn billigste og dyreste time
        billigst = min(data, key=lambda x: x["NOK_per_kWh"])
        dyrest = max(data, key=lambda x: x["NOK_per_kWh"])

        # Nåværende time
        current_hour = datetime.now().hour
        current_price = None
        for item in data:
            if f"T{current_hour:02d}" in item["time_start"]:
                current_price = item["NOK_per_kWh"]
                break

        # Gjennomsnitt
        avg_price = sum(item["NOK_per_kWh"] for item in data) / len(data)

        return {
            "sone": sone,
            "naa": round(current_price * 100, 1) if current_price else None,
            "snitt": round(avg_price * 100, 1),
            "billigst_time": billigst["time_start"][11:16],
            "billigst_pris": round(billigst["NOK_per_kWh"] * 100, 1),
            "dyrest_time": dyrest["time_start"][11:16],
            "dyrest_pris": round(dyrest["NOK_per_kWh"] * 100, 1),
        }

    except Exception as e:
        print(f"Feil ved strømpris: {e}")
        return None


def finn_neste_fridag():
    """Finner neste helligdag, ferie og store eventer."""
    try:
        idag = datetime.now().date()

        # Finn neste helligdag
        neste_helligdag = None
        dager_til_helligdag = None

        for dato_str, navn in sorted(HELLIGDAGER.items()):
            dato = datetime.strptime(dato_str, "%Y-%m-%d").date()
            if dato >= idag:
                neste_helligdag = navn
                dager_til_helligdag = (dato - idag).days
                break

        # Finn neste ferie
        neste_ferie = None
        dager_til_ferie = None

        for dato_str, (navn, slutt) in sorted(FERIER.items()):
            dato = datetime.strptime(dato_str, "%Y-%m-%d").date()
            if dato >= idag:
                neste_ferie = navn
                dager_til_ferie = (dato - idag).days
                break

        # Finn neste store event
        neste_event = None
        dager_til_event = None
        event_emoji = None

        for dato_str, (emoji_navn, beskrivelse) in sorted(STORE_EVENTER.items()):
            dato = datetime.strptime(dato_str, "%Y-%m-%d").date()
            if dato >= idag:
                neste_event = emoji_navn
                dager_til_event = (dato - idag).days
                break

        return {
            "helligdag": neste_helligdag,
            "dager_til_helligdag": dager_til_helligdag,
            "ferie": neste_ferie,
            "dager_til_ferie": dager_til_ferie,
            "event": neste_event,
            "dager_til_event": dager_til_event,
        }

    except Exception as e:
        print(f"Feil ved fridager: {e}")
        return {}


def hent_navnedag():
    """Henter dagens navnedag."""
    try:
        dato = datetime.now().strftime("%m-%d")
        navner = NAVNEDAGER.get(dato, [])
        return navner
    except:
        return []


def hent_denne_dag_i_historien():
    """Henter historiske hendelser for dagens dato."""
    try:
        dato = datetime.now().strftime("%m-%d")
        hendelser = DENNE_DAG_I_HISTORIEN.get(dato, [])
        if isinstance(hendelser, list) and len(hendelser) > 0:
            if isinstance(hendelser[0], list):
                hendelser = hendelser[0]
        return hendelser
    except:
        return []


def hent_tilfeldig_innhold():
    """Henter tilfeldig morsomt innhold."""
    valg = random.choice(["vits", "ordtak", "fact", "sitat"])

    if valg == "vits":
        return {"type": "vits", "emoji": "😂", "tittel": "Dagens Vits", "innhold": random.choice(VITSER)}
    elif valg == "ordtak":
        return {"type": "ordtak", "emoji": "📜", "tittel": "Norsk Ordtak", "innhold": random.choice(ORDTAK)}
    elif valg == "fact":
        return {"type": "fact", "emoji": "🤓", "tittel": "Visste du at...", "innhold": random.choice(FUN_FACTS)}
    else:
        return {"type": "sitat", "emoji": "💡", "tittel": "Dagens Motivasjon", "innhold": f'*"{random.choice(SITATER)}"*'}


def hent_daglig_utfordring():
    """Genererer en daglig utfordring/aktivitet."""
    utfordringer = [
        "💪 Gjør 20 pushups før lunsj!",
        "🚶 Gå 10 000 skritt i dag",
        "📚 Les minst 20 sider i en bok",
        "🧘 Ta 10 minutter meditasjon",
        "💧 Drikk 8 glass vann i dag",
        "📵 1 time uten sosiale medier",
        "🍎 Spis 5 porsjoner frukt/grønt",
        "😊 Gi 3 komplimenter til andre",
        "📝 Skriv ned 3 ting du er takknemlig for",
        "🎵 Lytt til et album du aldri har hørt før",
        "📞 Ring en venn du ikke har snakket med på lenge",
        "🌳 Tilbring 30 min ute i naturen",
        "🧹 Rydd et rom i hjemmet ditt",
        "🍳 Lag en ny oppskrift til middag",
        "✍️ Skriv et håndskrevet brev til noen",
        "🎨 Gjør noe kreativt i 15 minutter",
        "🏃 Ta trappen i stedet for heisen hele dagen",
        "😴 Legg deg 30 min tidligere enn vanlig",
        "📖 Lær et nytt ord på et fremmed språk",
        "🌅 Se soloppgangen eller solnedgangen",
    ]
    return random.choice(utfordringer)


def generer_melding_med_ai(data):
    """Genererer personlig hilsning med AI."""
    try:
        if not GROQ_API_KEY:
            return None

        client = Groq(api_key=GROQ_API_KEY)

        vaer_info = f"{data['vaer'].get('temp', 'ukjent')}°C, {data['vaer'].get('symbol', 'ukjent')}"
        nyheter_tekst = ", ".join([n["tittel"] for n in data.get("nyheter", {}).get("topp", [])[:3]])

        helligdag_info = ""
        if data.get("fridager", {}).get("helligdag"):
            dager = data["fridager"]["dager_til_helligdag"]
            navn = data["fridager"]["helligdag"]
            if dager == 0:
                helligdag_info = f"I dag er det {navn}!"
            elif dager == 1:
                helligdag_info = f"I morgen er det {navn}"
            elif dager <= 7:
                helligdag_info = f"{navn} om {dager} dager"

        naa = datetime.now()
        dag_navn = DAGER[naa.weekday()]

        prompt = f"""Du er en hyggelig norsk morgenassistent. Lag en kort, personlig morgenmelding.

Dag: {dag_navn}
Vær: {vaer_info}
Nyheter: {nyheter_tekst}
{helligdag_info}

Skriv 2-3 setninger. Vær varm og positiv. Tilpass til ukedagen. Ikke bruk emojis. Skriv på norsk."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Feil ved AI: {e}")
        return None


def lag_discord_melding(by):
    """Lager komplett Discord-melding."""
    try:
        # Hent all data
        vaer = hent_vaer(by)
        sol = hent_soloppgang_solnedgang(by)
        nyheter = hent_nyheter_utvidet()
        okonomi = hent_aksjer()
        krypto = hent_krypto()
        strom = hent_strompris(by)
        fridager = finn_neste_fridag()
        navnedag = hent_navnedag()
        historie = hent_denne_dag_i_historien()
        morsomt = hent_tilfeldig_innhold()
        utfordring = hent_daglig_utfordring()

        # AI hilsning
        ai_data = {"vaer": vaer, "nyheter": nyheter, "fridager": fridager}
        ai_hilsning = generer_melding_med_ai(ai_data)

        # Formater dato
        naa = datetime.now()
        dag_navn = DAGER[naa.weekday()].capitalize()
        dag = naa.day
        maaned = MAANEDER[naa.month - 1]
        aar = naa.year
        uke = naa.isocalendar()[1]
        formatert_dato = f"{dag_navn} {dag}. {maaned} {aar} (Uke {uke})"

        felter = []

        # ═══════════════════════════════════════════════════════════
        # VÆR
        # ═══════════════════════════════════════════════════════════
        if "error" not in vaer:
            vaer_tekst = f"**{vaer['symbol']}**\n"
            vaer_tekst += f"🌡️ **{vaer['temp']}°C** (føles som {vaer['feels_like']}°C)\n"
            vaer_tekst += f"💨 Vind: {vaer['vind']} m/s\n"

            if vaer.get('fuktighet'):
                vaer_tekst += f"💧 Fuktighet: {vaer['fuktighet']:.0f}%\n"

            if sol:
                vaer_tekst += f"🌅 Sol opp: {sol['sunrise']} | 🌇 Sol ned: {sol['sunset']}\n"
                vaer_tekst += f"☀️ Dagslys: {sol['daylight_hours']}t {sol['daylight_minutes']}min\n"

            vaer_tekst += f"\n👔 {vaer['klaer']}"

            felter.append({
                "name": f"🌤️ Været i {by}",
                "value": vaer_tekst,
                "inline": False
            })

        # ═══════════════════════════════════════════════════════════
        # STRØMPRIS
        # ═══════════════════════════════════════════════════════════
        if strom:
            pris_emoji = "🟢" if strom['naa'] and strom['naa'] < 50 else "🟡" if strom['naa'] and strom['naa'] < 100 else "🔴"
            strom_tekst = f"{pris_emoji} **Nå:** {strom['naa']} øre/kWh\n"
            strom_tekst += f"📊 Snitt: {strom['snitt']} øre/kWh\n"
            strom_tekst += f"🟢 Billigst: kl {strom['billigst_time']} ({strom['billigst_pris']} øre)\n"
            strom_tekst += f"🔴 Dyrest: kl {strom['dyrest_time']} ({strom['dyrest_pris']} øre)"

            felter.append({
                "name": f"⚡ Strømpris ({strom['sone']})",
                "value": strom_tekst,
                "inline": True
            })

        # ═══════════════════════════════════════════════════════════
        # NYHETER
        # ═══════════════════════════════════════════════════════════
        if nyheter.get("topp"):
            nyhet_tekst = ""
            for i, n in enumerate(nyheter["topp"][:5], 1):
                nyhet_tekst += f"**{i}.** [{n['tittel']}]({n['link']})\n"

            felter.append({
                "name": "📰 Dagens Toppsaker",
                "value": nyhet_tekst,
                "inline": False
            })

        # Sport nyheter
        if nyheter.get("sport") and len(nyheter["sport"]) > 0:
            sport_tekst = ""
            for n in nyheter["sport"][:3]:
                sport_tekst += f"• [{n['tittel']}]({n['link']})\n"

            felter.append({
                "name": "⚽ Sport",
                "value": sport_tekst,
                "inline": True
            })

        # Tech/vitenskap
        if nyheter.get("tech") and len(nyheter["tech"]) > 0:
            tech_tekst = ""
            for n in nyheter["tech"][:3]:
                tech_tekst += f"• [{n['tittel']}]({n['link']})\n"

            felter.append({
                "name": "🔬 Vitenskap & Tech",
                "value": tech_tekst,
                "inline": True
            })

        # ═══════════════════════════════════════════════════════════
        # ØKONOMI
        # ═══════════════════════════════════════════════════════════
        if okonomi.get("aksjer"):
            aksje_tekst = ""
            for a in okonomi["aksjer"][:5]:
                aksje_tekst += f"{a['emoji']} **{a['navn']}**: {a['pris']:.2f} ({a['endring_str']})\n"

            felter.append({
                "name": "📈 Aksjer",
                "value": aksje_tekst,
                "inline": True
            })

        if okonomi.get("valuta"):
            valuta_tekst = ""
            for v in okonomi["valuta"]:
                valuta_tekst += f"{v['emoji']} **{v['par']}**: {v['kurs']}\n"

            felter.append({
                "name": "💱 Valuta",
                "value": valuta_tekst,
                "inline": True
            })

        # ═══════════════════════════════════════════════════════════
        # KRYPTO
        # ═══════════════════════════════════════════════════════════
        if krypto:
            krypto_tekst = ""
            for k in krypto[:4]:
                krypto_tekst += f"{k['emoji']} **{k['navn']}**: {k['pris']:,.0f} NOK {k['trend']} {k['endring_str']}\n"

            felter.append({
                "name": "🪙 Krypto (24t)",
                "value": krypto_tekst,
                "inline": True
            })

        # ═══════════════════════════════════════════════════════════
        # FRIDAGER OG NEDTELLINGER
        # ═══════════════════════════════════════════════════════════
        fridag_tekst = ""

        if fridager.get("helligdag"):
            dager = fridager["dager_til_helligdag"]
            if dager == 0:
                fridag_tekst += f"🎉 **I DAG: {fridager['helligdag']}!**\n\n"
            elif dager == 1:
                fridag_tekst += f"📅 **I morgen:** {fridager['helligdag']}\n\n"
            elif dager <= 14:
                fridag_tekst += f"📅 **{fridager['helligdag']}** om {dager} dager\n\n"

        if fridager.get("ferie"):
            dager = fridager["dager_til_ferie"]
            if dager <= 30:
                fridag_tekst += f"🏖️ **{fridager['ferie']}** om {dager} dager\n\n"

        if fridager.get("event"):
            dager = fridager["dager_til_event"]
            if dager <= 60:
                fridag_tekst += f"🎯 **{fridager['event']}** om {dager} dager"

        if fridag_tekst:
            felter.append({
                "name": "🗓️ Nedtellinger",
                "value": fridag_tekst.strip(),
                "inline": True
            })

        # ═══════════════════════════════════════════════════════════
        # NAVNEDAG
        # ═══════════════════════════════════════════════════════════
        if navnedag:
            navne_tekst = "🎂 **" + ", ".join(navnedag) + "**"
            felter.append({
                "name": "📛 Gratulerer med navnedagen!",
                "value": navne_tekst,
                "inline": True
            })

        # ═══════════════════════════════════════════════════════════
        # DENNE DAG I HISTORIEN
        # ═══════════════════════════════════════════════════════════
        if historie:
            hendelse = random.choice(historie) if isinstance(historie, list) else historie
            felter.append({
                "name": "📜 Denne dag i historien",
                "value": f"*{hendelse}*",
                "inline": False
            })

        # ═══════════════════════════════════════════════════════════
        # MORSOMT INNHOLD
        # ═══════════════════════════════════════════════════════════
        felter.append({
            "name": f"{morsomt['emoji']} {morsomt['tittel']}",
            "value": morsomt['innhold'],
            "inline": False
        })

        # ═══════════════════════════════════════════════════════════
        # DAGLIG UTFORDRING
        # ═══════════════════════════════════════════════════════════
        felter.append({
            "name": "🎯 Dagens Utfordring",
            "value": utfordring,
            "inline": False
        })

        # Velg farge basert på ukedag
        farger = {
            0: 0x3498db,  # Mandag - blå
            1: 0x2ecc71,  # Tirsdag - grønn
            2: 0x9b59b6,  # Onsdag - lilla
            3: 0xe67e22,  # Torsdag - oransje
            4: 0xe74c3c,  # Fredag - rød
            5: 0xf39c12,  # Lørdag - gul
            6: 0x1abc9c,  # Søndag - turkis
        }

        embed = {
            "title": f"☀️ God morgen! {formatert_dato}",
            "color": farger.get(naa.weekday(), 0x5814ff),
            "fields": felter,
            "footer": {
                "text": f"🤖 Morgenbot v2.0 | {by} | Oppdatert"
            },
            "timestamp": naa.isoformat()
        }

        if ai_hilsning:
            embed["description"] = ai_hilsning

        return {"embeds": [embed]}

    except Exception as e:
        print(f"Feil ved melding: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_til_discord(melding):
    """Sender melding til Discord."""
    try:
        if not DISCORD_WEBHOOK:
            print("DISCORD_WEBHOOK ikke satt")
            return False

        response = requests.post(
            DISCORD_WEBHOOK,
            json=melding,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 204:
            print("✅ Melding sendt!")
            return True
        else:
            print(f"❌ Feil: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Feil ved sending: {e}")
        return False


def main():
    """Hovedfunksjon."""
    print("=" * 50)
    print("🌅 MORGENBOT v2.0 starter...")
    print("=" * 50)
    print(f"📍 By: {BY}")
    print(f"⏰ Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if not DISCORD_WEBHOOK:
        print("⚠️ DISCORD_WEBHOOK ikke satt!")

    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY ikke satt - AI hopper over")

    print("📨 Lager melding...")
    melding = lag_discord_melding(BY)

    if melding:
        print("📤 Sender til Discord...")
        if send_til_discord(melding):
            print("✅ Morgenbot fullført!")
        else:
            print("❌ Kunne ikke sende")
    else:
        print("❌ Kunne ikke lage melding")

    print()
    print("=" * 50)
    print(f"🏁 Ferdig: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
