"""Data client for MyHadith (JAKIM).

Two backends share one interface (`async_get_featured`):
- ScrapeBackend: reads the public website (current default).
- ApiBackend: placeholder for the key-gated /api/hadith endpoint, to be
  filled in once JAKIM issues an API key and documents the response.
"""
from __future__ import annotations

import html
import re
from dataclasses import asdict, dataclass, field
from typing import Any

import aiohttp

from .const import BASE_URL, REQUEST_TIMEOUT, USER_AGENT


class MyHadithError(Exception):
    """Generic error talking to MyHadith."""


class MyHadithAuthError(MyHadithError):
    """API key missing or rejected."""


@dataclass
class Hadith:
    """One hadith as shown on MyHadith."""

    hadith_id: int
    title: str
    url: str
    matan: str = ""
    maksud: str = ""
    penghayatan: str = ""
    sumber_rujukan: list[str] = field(default_factory=list)
    nombor_hadith: str | None = None
    koleksi: str | None = None
    kitab: str | None = None
    bab: str | None = None
    perawi: str | None = None
    status: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------- helpers
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t\r\f\v]+")


def _clean(fragment: str | None) -> str:
    """HTML fragment -> readable plain text, keeping paragraph/list breaks."""
    if not fragment:
        return ""
    text = re.sub(r"(?i)<br\s*/?>", "\n", fragment)
    text = re.sub(r"(?i)</(p|li|ol|ul|div|h\d)>", "\n", text)
    text = _TAG.sub("", text)
    text = html.unescape(text).replace("\xa0", " ")
    lines = [_WS.sub(" ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln)


def _div_inner(page: str, opening_regex: str) -> str | None:
    """Return the inner HTML of the first <div> matching opening_regex,
    honouring nested divs."""
    m = re.search(opening_regex, page, re.S)
    if not m:
        return None
    pos, depth = m.end(), 1
    for tag in re.finditer(r"(?i)<(/?)div\b[^>]*>", page[pos:]):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            return page[pos : pos + tag.start()]
    return None


def _info_value(page: str, label: str) -> str | None:
    m = re.search(
        r'<span class="info-label">\s*' + re.escape(label) + r'\s*</span>\s*'
        r'<div class="info-value">(.*?)</div>',
        page,
        re.S,
    )
    value = _clean(m.group(1)) if m else ""
    return value or None


def parse_hadith_page(page: str, hadith_id: int) -> Hadith:
    """Parse /hadith/{id} HTML."""
    title_m = re.search(r'<h2 class="hadith-card-title">(.*?)</h2>', page, re.S)
    if not title_m:
        raise MyHadithError(f"Hadith {hadith_id}: page layout not recognised")
    title = _clean(title_m.group(1))

    matan = _clean(_div_inner(page, r'<div class="arabic-text"[^>]*>'))
    maksud = _clean(_div_inner(page, r'<div class="translation-text"[^>]*>'))

    penghayatan_raw = _div_inner(page, r'<div id="pengajaranContent"[^>]*>') or ""
    sumber: list[str] = []
    # "Sumber Rujukan" is typed by editors in several ways: its own <p>,
    # <strong> inside a <p>, with or without a colon, any case.
    split = re.split(
        r"(?is)<p[^>]*>\s*(?:<strong>)?\s*Sumber\s+Rujukan\s*:?\s*(?:</strong>)?\s*:?",
        penghayatan_raw,
        maxsplit=1,
    )
    if len(split) == 2:
        penghayatan_raw, sumber_raw = split
        for line in _clean(sumber_raw).split("\n"):
            line = re.sub(r"^\s*\d+[.)]\s*", "", line).strip()
            if line:
                sumber.append(line)

    return Hadith(
        hadith_id=hadith_id,
        title=title,
        url=f"{BASE_URL}/hadith/{hadith_id}",
        matan=matan,
        maksud=maksud,
        penghayatan=_clean(penghayatan_raw),
        sumber_rujukan=sumber,
        nombor_hadith=_info_value(page, "Nombor Hadith"),
        koleksi=_info_value(page, "Koleksi"),
        kitab=_info_value(page, "Kitab"),
        bab=_info_value(page, "Bab"),
        perawi=_info_value(page, "Perawi"),
        status=_info_value(page, "Status Kesahihan"),
    )


def parse_featured_ids(page: str) -> list[int]:
    """Hadith IDs in the homepage Mutiara Hadith carousel, in page order.
    The first one is the hadith JAKIM currently features."""
    section = page.split("mySwiperMutiara", 1)
    source = section[1] if len(section) == 2 else page
    ids: list[int] = []
    for m in re.finditer(r"/hadith/(\d+)", source):
        hid = int(m.group(1))
        if hid not in ids:
            ids.append(hid)
    return ids


# ---------------------------------------------------------------- backends
class ScrapeBackend:
    """Reads the public MyHadith website."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _get(self, path: str) -> str:
        try:
            async with self._session.get(
                f"{BASE_URL}{path}",
                headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status != 200:
                    raise MyHadithError(f"GET {path} returned HTTP {resp.status}")
                return await resp.text()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise MyHadithError(f"GET {path} failed: {err}") from err

    async def async_get_hadith(self, hadith_id: int) -> Hadith:
        return parse_hadith_page(await self._get(f"/hadith/{hadith_id}"), hadith_id)

    async def async_get_featured(self) -> Hadith:
        ids = parse_featured_ids(await self._get("/"))
        if not ids:
            raise MyHadithError("No Mutiara Hadith found on the homepage")
        last_err: Exception | None = None
        for hid in ids[:3]:  # fall back to the next card if one page 404s
            try:
                return await self.async_get_hadith(hid)
            except MyHadithError as err:
                last_err = err
        raise MyHadithError(f"Could not load featured hadith: {last_err}")


class ApiBackend:
    """Key-gated JSON API at /api/hadith (api_key query or X-API-KEY header).

    The response format is not public yet. `async_validate` already works;
    `async_get_featured` is mapped once JAKIM issues a key.
    """

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    async def _get_json(self, path: str, params: dict | None = None) -> Any:
        try:
            async with self._session.get(
                f"{BASE_URL}{path}",
                params=params,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                    "X-API-KEY": self._api_key,
                },
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status in (401, 403):
                    raise MyHadithAuthError("API key missing, invalid or inactive")
                if resp.status != 200:
                    raise MyHadithError(f"GET {path} returned HTTP {resp.status}")
                return await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise MyHadithError(f"GET {path} failed: {err}") from err

    async def async_validate(self) -> None:
        await self._get_json("/api/hadith")

    async def async_get_featured(self) -> Hadith:
        raise MyHadithError(
            "API mode is not mapped yet. Use scrape mode until the API format is known."
        )
