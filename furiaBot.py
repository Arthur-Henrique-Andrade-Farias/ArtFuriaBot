
import asyncio
import logging
import os
from datetime import datetime
from typing import List, Tuple, Optional

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Config & Logger
# --------------------------------------------------------------------------- #
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Defina BOT_TOKEN no .env ou export no shell")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

TEAM_ID_HLTV = 8297
LIQUIPEDIA_URL = "https://liquipedia.net/counterstrike/FURIA"
HLTV_URL = f"https://www.hltv.org/team/{TEAM_ID_HLTV}/furia"

# --------------------------------------------------------------------------- #
# Dados – Roster c/ links Liquipedia
# --------------------------------------------------------------------------- #
STUB_ROSTER: List[Tuple[str, str, Optional[str]]] = [
    ("KSCERATO", "Rifler", "https://liquipedia.net/counterstrike/KSCERATO"),
    ("yuurih", "Rifler", "https://liquipedia.net/counterstrike/Yuurih"),
    ("arT", "IGL / AWPer", "https://liquipedia.net/counterstrike/ArT"),
    ("chelo", "Entry", "https://liquipedia.net/counterstrike/Chelo"),
]
STUB_COACH = ("guerri", "Coach", "https://liquipedia.net/counterstrike/Guerri")
STUB_MANAGER = ("decenty", "Manager", None)

# --------------------------------------------------------------------------- #
# Stubs: Resultados, Agenda, Notícias
# --------------------------------------------------------------------------- #
STUB_RESULTS = [
    ("09/04/2025", "FURIA 0 × 2 The MongolZ", "PGL Bucharest 2025", HLTV_URL),
    ("08/04/2025", "FURIA 0 × 2 Virtus.pro", "PGL Bucharest 2025.", HLTV_URL),
    ("07/04/2025", "FURIA 1 × 2 Complexity", "PGL Bucharest 2025.", HLTV_URL),

]

STUB_SCHEDULE: List[Tuple[str, str, str, float, str]] = [
    ("10/05/2025", "FURIA × The MongolZ", "PGL Astana 2025", 0.62, "https://www.hltv.org/live?matchId=2382203"),
]

STUB_NEWS = [
    ("FURIA garante vaga na IEM Dallas após vitória sobre MIBR!", "https://ge.globo.com/esports/csgo/noticia/2025/04/30/furia-classificada-iem-dallas.ghtml"),
    ("arT comenta ajustes táticos para a temporada de 2025.", "https://dust2.com.br/noticia/60000"),
]

# --------------------------------------------------------------------------- #
# Scraping util (HLTV simplificado)
# --------------------------------------------------------------------------- #
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = httpx.Timeout(10.0)

async def fetch_html(url: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(url, headers=HEADERS)
            r.raise_for_status()
            return r.text
    except Exception as exc:
        logging.warning("Falha fetch %s: %s", url, exc)
        return None

async def scrape_latest_results(limit: int = 3):
    html = await fetch_html(HLTV_URL)
    if not html:
        return STUB_RESULTS[:limit]
    soup = BeautifulSoup(html, "html.parser")
    res = []
    for row in soup.select(".result-con .inline-results-con")[:limit]:
        date_span = row.select_one(".time")
        if not date_span:
            continue
        date = datetime.fromtimestamp(int(date_span["data-unix"]) / 1000).strftime("%d/%m/%Y")
        score = row.select_one(".result-score").get_text(strip=True)
        opponent = row.select(".team-teamname")[-1].get_text(strip=True)
        event = row.find_parent(".result-con").select_one(".event-name").get_text(strip=True)
        link = "https://www.hltv.org" + row.parent["href"]
        res.append((date, f"FURIA {score} {opponent}", event, link))
    return res or STUB_RESULTS[:limit]

async def scrape_news(limit: int = 3):
    return STUB_NEWS[:limit]

# --------------------------------------------------------------------------- #
# Helpers de formatação
# --------------------------------------------------------------------------- #

def link_or_bold(name: str, url: Optional[str]):
    return f"<a href='{url}'><b>{name}</b></a>" if url else f"<b>{name}</b>"


def format_roster():
    lines = [f"🟦 {link_or_bold(n, u)} – {r}" for n, r, u in STUB_ROSTER]
    lines.append(f"🟥 {link_or_bold(STUB_COACH[0], STUB_COACH[2])} – {STUB_COACH[1]}")
    lines.append(f"🟧 {link_or_bold(STUB_MANAGER[0], STUB_MANAGER[2])} – {STUB_MANAGER[1]}")
    return "<b>Elenco & Staff</b>\n" + "\n".join(lines)


def format_results(res):
    return "<b>Últimos resultados</b>\n" + "\n".join(
        f"{d} • <a href='{link}'>{score}</a> – {event}" for d, score, event, link in res
    )


def format_schedule(sched):
    return "<b>Próximos jogos</b>\n" + "\n".join(
        f"{d} • <a href='{stream}'>{match}</a> – {event} (⧖ {prob*100:.0f}% win)" for d, match, event, prob, stream in sched
    )


def format_news(news):
    return "<b>Notícias</b>\n" + "\n".join(f"• <a href='{url}'>{title}</a>" for title, url in news)

# --------------------------------------------------------------------------- #
# Textos
# --------------------------------------------------------------------------- #
ABOUT_TEXT = (
    "<b>FURIA Esports</b> é uma organização brasileira fundada em 2017.\n"
    "Sua line de <i>Counter‑Strike 2</i> é famosa pelo estilo agressivo de arT.\n\n"
    "🏆 Conquistas:\n• IEM New York 2020\n• Elisa Masters 2024\n• Legends Stage em 3 Majors seguidos (2022‑2023)\n\n"
    "Use /links para acesso rápido a portais oficiais."
)

LINKS_TEXT = (
    f"<b>Links úteis</b>\n"
    f"• <a href='{LIQUIPEDIA_URL}'>Liquipedia</a>\n"
    f"• <a href='{HLTV_URL}'>HLTV</a>\n"
    "• <a href='https://twitter.com/FURIA'>Twitter oficial</a>\n"
    "• <a href='https://instagram.com/furiagg'>Instagram</a>"
)

# --------------------------------------------------------------------------- #
# Keyboards
# --------------------------------------------------------------------------- #
main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ℹ️ Sobre", callback_data="about")],
    [InlineKeyboardButton(text="📋 Roster", callback_data="roster")],
    [InlineKeyboardButton(text="✅ Resultados", callback_data="results"), InlineKeyboardButton(text="⏰ Próximos", callback_data="schedule")],
    [InlineKeyboardButton(text="📰 Notícias", callback_data="news")],
    [InlineKeyboardButton(text="🔗 Links", callback_data="links")],
])

# --------------------------------------------------------------------------- #
# Handlers – Commands
# --------------------------------------------------------------------------- #
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        "🐍 <b>FURIA Fans Bot</b> pronto para o clutch!\n"
        "Acompanhe resultados, agenda, roster e notícias em tempo real.",
        reply_markup=main_kb,
    )

@dp.message(Command("about"))
async def cmd_about(m: types.Message):
    await m.reply(ABOUT_TEXT)

@dp.message(Command("roster"))
async def cmd_roster(m: types.Message):
    await m.reply(format_roster())

@dp.message(Command("results"))
async def cmd_results(m: types.Message):
    await m.reply(format_results(await scrape_latest_results()))

@dp.message(Command("schedule"))
async def cmd_schedule(m: types.Message):
    await m.reply(format_schedule(STUB_SCHEDULE))

@dp.message(Command("news"))
async def cmd_news(m: types.Message):
    await m.reply(format_news(await scrape_news()))

@dp.message(Command("links"))
async def cmd_links(m: types.Message):
    await m.reply(LINKS_TEXT)

# --------------------------------------------------------------------------- #
# Handlers – Callbacks
# --------------------------------------------------------------------------- #
@dp.callback_query(F.data == "about")
async def cb_about(q: types.CallbackQuery):
    await q.answer()
    await q.message.edit_text(ABOUT_TEXT, reply_markup=main_kb)
@dp.callback_query(F.data == "roster")
async def cb_roster(q: types.CallbackQuery):
    await q.answer()
    await q.message.edit_text(format_roster(), reply_markup=main_kb)
@dp.callback_query(F.data == "results")
async def cb_results(q: types.CallbackQuery):
    await q.answer()
    await q.message.edit_text(format_results(await scrape_latest_results()), reply_markup=main_kb)
@dp.callback_query(F.data == "schedule")
async def cb_schedule(q):
    await q.answer(); await q.message.edit_text(format_schedule(STUB_SCHEDULE), reply_markup=main_kb)
@dp.callback_query(F.data == "news")
async def cb_news(q):
    await q.answer(); await q.message.edit_text(format_news(await scrape_news()), reply_markup=main_kb)
@dp.callback_query(F.data == "links")
async def cb_links(q):
    await q.answer(); await q.message.edit_text(LINKS_TEXT, reply_markup=main_kb)

# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #
async def main():
    logging.info("🤖 Bot iniciado…")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot encerrado.")
