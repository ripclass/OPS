"""
URL source extraction helpers for public web pages.

Fetch public article/report/blog URLs server-side and extract readable text content
without browser automation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from readability import Document


USER_AGENT = (
    "OPS-URL-Importer/1.0 (+https://github.com/ripclass/OPS) "
    "requests public article extraction"
)
SUPPORTED_TEXT_TYPES = (
    "text/html",
    "application/xhtml+xml",
    "text/plain",
)


class URLSourceExtractionError(Exception):
    """Raised when a URL source cannot be fetched or parsed."""


@dataclass
class URLSource:
    url: str
    title: str
    text: str
    content_type: str

    @property
    def artifact_filename(self) -> str:
        parsed = urlparse(self.url)
        host = re.sub(r"[^A-Za-z0-9.-]+", "_", parsed.netloc or "source")
        slug_source = self.title or (parsed.path.rsplit("/", 1)[-1] if parsed.path else "")
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", slug_source).strip("._") or "article"
        return f"url_{host}_{slug[:48]}.txt"


def _normalize_text(value: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+\n", "\n", value)).strip()


def _extract_plain_text(html: str) -> str:
    try:
        summary_html = Document(html).summary(html_partial=True)
        soup = BeautifulSoup(summary_html, "html.parser")
        text = soup.get_text("\n", strip=True)
        if text.strip():
            return _normalize_text(text)
    except Exception:
        pass

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()
    return _normalize_text(soup.get_text("\n", strip=True))


def fetch_public_url_source(url: str, timeout_seconds: int = 15) -> URLSource:
    normalized_url = str(url or "").strip()
    if not normalized_url:
        raise URLSourceExtractionError("URL is empty")

    parsed = urlparse(normalized_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise URLSourceExtractionError("Only http/https public URLs are supported")

    try:
        response = requests.get(
            normalized_url,
            timeout=timeout_seconds,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise URLSourceExtractionError(f"Failed to fetch URL: {exc}") from exc

    content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if content_type and content_type not in SUPPORTED_TEXT_TYPES:
        raise URLSourceExtractionError(f"Unsupported content type: {content_type}")

    text_body: Optional[str] = None
    title: str = ""

    if content_type == "text/plain":
        text_body = _normalize_text(response.text)
        title = parsed.path.rsplit("/", 1)[-1] or parsed.netloc
    else:
        html = response.text
        try:
            title = Document(html).short_title() or ""
        except Exception:
            title = ""
        if not title:
            soup = BeautifulSoup(html, "html.parser")
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
        text_body = _extract_plain_text(html)

    if not text_body:
        raise URLSourceExtractionError("No readable text could be extracted from this URL")

    if len(text_body) < 80:
        raise URLSourceExtractionError("Extracted URL text is too short to use as a simulation source")

    if not title:
        title = parsed.netloc

    return URLSource(
        url=normalized_url,
        title=title.strip(),
        text=text_body,
        content_type=content_type or "text/html",
    )
