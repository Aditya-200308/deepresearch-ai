# ============================================================
# FILE: src/tools.py
# PURPOSE: Enterprise Multi-Source Search & Web Scraping Engine (Zero-Dependency Resilient)
# ============================================================

import sys
import os
import re
import json
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import xml.etree.ElementTree as ET

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}


def extract_keywords(topic: str) -> List[str]:
    """Extracts high-signal meaningful keywords from a topic query."""
    stopwords = {
        'the', 'and', 'for', 'with', 'full', 'review', 'released', 'from', 'about',
        'what', 'this', 'that', 'who', 'how', 'why', 'when', 'where', 'are', 'was',
        'were', 'been', 'have', 'has', 'had', 'does', 'did', 'will', 'would', 'could',
        'should', 'is', 'in', 'on', 'at', 'by', 'an', 'a', 'to', 'of', 'top', 'tell', 'me'
    }
    words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', topic)]
    keywords = [w for w in words if w not in stopwords]
    return keywords if keywords else words[:2]


def is_relevant(title: str, snippet: str, topic_keywords: List[str]) -> bool:
    """Strict relevance check: Title or snippet must directly match the topic entity."""
    t_lower = title.lower()
    s_lower = snippet.lower()
    
    if not topic_keywords:
        return True

    # Immediate discard for spam, games, or mismatch triggers
    spam_triggers = ["solitaire", "casino", "poker", "download free games", "card game",
                     "horoscope", "crossword", "sudoku", "recipe"]
    for spam in spam_triggers:
        if spam in (t_lower + " " + s_lower) and not any(spam in kw for kw in topic_keywords):
            return False

    # Primary rule: The article title must contain at least one primary topic keyword
    title_matches = [kw for kw in topic_keywords if kw in t_lower]
    if title_matches:
        return True

    snippet_matches = sum(1 for kw in topic_keywords if kw in s_lower)
    return snippet_matches >= 2


def search_google_news(query: str, topic_keywords: List[str], max_results: int = 4) -> List[Dict[str, str]]:
    """Fetches verified articles from Google Live News Index with strict relevance filtering."""
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            root = ET.fromstring(r.text)
            for item in root.findall('./channel/item'):
                t = item.find('title').text if item.find('title') is not None else ''
                l = item.find('link').text if item.find('link') is not None else ''
                desc = item.find('description').text if item.find('description') is not None else ''
                clean_desc = re.sub(r'<[^>]+>', ' ', desc).strip()
                if t and len(clean_desc) > 10 and is_relevant(t, clean_desc, topic_keywords):
                    results.append({'title': t, 'url': l, 'snippet': clean_desc})
                if len(results) >= max_results:
                    break
    except Exception:
        pass
    return results


def search_wikipedia(query: str, topic_keywords: List[str], max_results: int = 2) -> List[Dict[str, str]]:
    """Fetches encyclopedic context from Wikipedia API using pure standard library requests."""
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={requests.utils.quote(query)}&limit={max_results}&namespace=0&format=json"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=4)
        if r.status_code == 200:
            data = r.json()
            titles, snippets, urls = data[1], data[2], data[3]
            for t, s, u in zip(titles, snippets, urls):
                if s and len(s) > 20 and is_relevant(t, s, topic_keywords):
                    results.append({'title': f"Wikipedia: {t}", 'url': u, 'snippet': s})
    except Exception:
        pass
    return results


def search_yahoo_filtered(query: str, topic_keywords: List[str], max_results: int = 3) -> List[Dict[str, str]]:
    """Fetches web results with resilient multi-parser fallback (bs4 or standard regex)."""
    url = f"https://search.yahoo.com/search?p={requests.utils.quote(query)}"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r.text, 'html.parser')
                for item in soup.find_all('div', class_='algo'):
                    t = item.find('h3')
                    d = item.find('div', class_='compText')
                    link = item.find('a')
                    if t and d:
                        title_text = t.get_text(strip=True)
                        desc_text = d.get_text(strip=True)
                        if is_relevant(title_text, desc_text, topic_keywords):
                            raw_url = link.get('href', '') if link else ''
                            match = re.search(r'/RU=(https?%3a%2f%2f[^/]+.*?)/RK=', raw_url)
                            clean_url = requests.utils.unquote(match.group(1)) if match else raw_url
                            results.append({'title': title_text, 'url': clean_url, 'snippet': desc_text})
                    if len(results) >= max_results:
                        break
            except ImportError:
                # Built-in standard library regex fallback (Zero external package dependency)
                items = re.findall(r'<h3[^>]*>(.*?)</h3>.*?<div[^>]*class="[^"]*compText[^"]*"[^>]*>(.*?)</div>', r.text, re.DOTALL)
                for title_html, desc_html in items:
                    title_text = re.sub(r'<[^>]+>', ' ', title_html).strip()
                    desc_text = re.sub(r'<[^>]+>', ' ', desc_html).strip()
                    if title_text and is_relevant(title_text, desc_text, topic_keywords):
                        results.append({'title': title_text, 'url': f"https://news.google.com/search?q={requests.utils.quote(title_text)}", 'snippet': desc_text})
                    if len(results) >= max_results:
                        break
    except Exception:
        pass
    return results


def parallel_search_web(queries: List[str], max_results_per_query: int = 4) -> List[Dict[str, str]]:
    """Executes multi-engine search with strict subject-matter validation."""
    all_results = []
    seen_titles = set()

    primary_topic = queries[0] if queries else ""
    keywords = extract_keywords(primary_topic)

    # Step 1: Run Google News
    for q in queries[:2]:
        for item in search_google_news(q, keywords, 3):
            t = item.get('title', '').strip()
            if t and t not in seen_titles:
                seen_titles.add(t)
                all_results.append(item)

    # Step 2: Add Filtered Web & Wikipedia Results
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(search_yahoo_filtered, q, keywords, 2) for q in queries[:2]]
        futures.append(executor.submit(search_wikipedia, primary_topic, keywords, 2))
        for f in as_completed(futures, timeout=4.0):
            try:
                for item in f.result():
                    t = item.get('title', '').strip()
                    if t and t not in seen_titles:
                        seen_titles.add(t)
                        all_results.append(item)
            except Exception:
                pass

    return all_results


def format_search_dossier(search_results: List[Dict[str, str]]) -> str:
    """Formats search results into an authoritative research evidence document."""
    formatted = []
    for idx, s in enumerate(search_results, 1):
        formatted.append(f"[{idx}] SOURCE: {s.get('title', 'Web Intelligence')}\nURL: {s.get('url', '#')}\nEVIDENCE & EXCERPTS: {s.get('snippet', '')}")
    return "\n\n" + ("\n\n" + "="*50 + "\n\n").join(formatted)
