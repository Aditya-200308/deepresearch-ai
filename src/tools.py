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

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

HEADERS = {
    'User-Agent': 'DeepResearchBot/2.0 (Mozilla/5.0 Enterprise Research; https://github.com/Aditya-200308/deepresearch-ai)',
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
    spam_triggers = ['solitaire', 'casino', 'poker', 'download free games', 'card game',
                     'horoscope', 'crossword', 'sudoku', 'recipe']
    for spam in spam_triggers:
        if spam in (t_lower + ' ' + s_lower) and not any(spam in kw for kw in topic_keywords):
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


def search_wikipedia(query: str, topic_keywords: List[str] = None, max_results: int = 1) -> List[Dict[str, str]]:
    """
    Fetches rich encyclopedic definitions and background from Wikipedia
    using Wikipedia Query Search and Extracts API (prop=extracts&exintro=true&explaintext=true).
    """
    clean_q = re.sub(r'^(who|what|where|why|how|tell me about|explain)\s+(is|was|are|were)?\s*', '', query, flags=re.I).strip(' ?.:')
    if not clean_q:
        clean_q = query.strip(' ?.:')

    headers = {'User-Agent': 'DeepResearchBot/2.0 (Academic Research; https://github.com/Aditya-200308/deepresearch-ai)'}
    results = []
    
    # 1. Search Wikipedia for best matching article title
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(clean_q)}&srlimit=2&format=json"
    try:
        r = requests.get(search_url, headers=headers, timeout=5)
        if r.status_code == 200:
            items = r.json().get('query', {}).get('search', [])
            if items:
                best_title = items[0]['title']
                # 2. Fetch full introductory encyclopedic extract
                extract_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&titles={requests.utils.quote(best_title)}&format=json"
                r2 = requests.get(extract_url, headers=headers, timeout=5)
                if r2.status_code == 200:
                    pages = r2.json().get('query', {}).get('pages', {})
                    for pid, pdata in pages.items():
                        extract = pdata.get('extract', '').strip()
                        if extract and len(extract) > 40:
                            clean_extract = re.sub(r'\s*\([^)]*?(?:IPA|IAST|Sanskrit|listen|pronounced)[^)]*?\)', '', extract)
                            clean_extract = re.sub(r'\s{2,}', ' ', clean_extract).strip()
                            slug = best_title.replace(' ', '_')
                            results.append({
                                'title': f"Wikipedia: {best_title}",
                                'url': f"https://en.wikipedia.org/wiki/{slug}",
                                'snippet': clean_extract[:1600]
                            })
                            break
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
                items = re.findall(r'<h3[^>]*>(.*?)</h3>.*?<div[^>]*class="compText"[^>]*>(.*?)</div>', r.text, re.DOTALL)
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
    """Executes multi-engine search concurrently with guaranteed Wikipedia encyclopedic priority."""
    all_results = []
    seen_titles = set()

    primary_topic = queries[0] if queries else ''
    keywords = extract_keywords(primary_topic)

    wiki_results = []
    news_results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        wiki_future = executor.submit(search_wikipedia, primary_topic, keywords, 1)
        news_futures = [executor.submit(search_google_news, q, keywords, 3) for q in queries[:2]]

        try:
            wiki_results = wiki_future.result(timeout=5.0)
        except Exception:
            wiki_results = []

        for f in news_futures:
            try:
                items = f.result(timeout=5.0)
                if items:
                    news_results.extend(items)
            except Exception:
                pass

    # Wikipedia encyclopedic grounding is guaranteed top priority
    for item in wiki_results:
        t = item.get('title', '').strip()
        if t and t not in seen_titles:
            seen_titles.add(t)
            all_results.append(item)

    # Followed by verified primary news articles
    for item in news_results:
        t = item.get('title', '').strip()
        if t and t not in seen_titles:
            seen_titles.add(t)
            all_results.append(item)

    return all_results


def format_search_dossier(search_results: List[Dict[str, str]]) -> str:
    """Formats search results into an authoritative research evidence document."""
    formatted = []
    for idx, s in enumerate(search_results, 1):
        formatted.append(f"[{idx}] SOURCE: {s.get('title', 'Web Intelligence')}\nURL: {s.get('url', '#')}\nEVIDENCE & EXCERPTS: {s.get('snippet', '')}")
    return "\n\n" + ("\n\n" + "="*50 + "\n\n").join(formatted)
