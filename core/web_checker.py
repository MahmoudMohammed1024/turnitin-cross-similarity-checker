import requests
import re
import base64
import urllib.parse
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup


def decode_bing_url(url: str) -> str:
    """
    Decodes Bing's tracking URL into the real target website URL.
    """
    if 'bing.com/ck/a' in url and 'u=' in url:
        try:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            u_param = qs.get('u', [''])[0]
            if u_param.startswith('a1'):
                b64 = u_param[2:]
                b64 += '=' * ((4 - len(b64) % 4) % 4)
                decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                if decoded.startswith('http'):
                    return decoded
        except Exception:
            pass
    return url


class InternetPlagiarismChecker:
    """
    Performs live academic and web searches for Internet Sources (🌐) and Publications (📚):
    1. CrossRef Official Academic DOI Index (150M+ publications, journals, books)
    2. Wikipedia & Open Web Encyclopedia API
    3. DuckDuckGo Theses & Academic Web Form
    4. Bing Verified Search
    """
    def __init__(self, max_queries: int = 45, timeout: int = 4):
        self.max_queries = max_queries
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8'
        }

    def _verify_snippet_match(self, raw_sentence: str, snippet: str) -> float:
        """
        Calculates meaningful academic token overlap between sentence and search snippet.
        """
        stop_words = {
            'the', 'is', 'in', 'at', 'of', 'on', 'and', 'a', 'to', 'for', 'with', 'as', 'by', 'that', 'this',
            'it', 'from', 'or', 'an', 'be', 'are', 'was', 'were', 'which', 'has', 'have', 'had', 'been',
            'these', 'those', 'their', 'they', 'than', 'more', 'also', 'such', 'some',
            'من', 'في', 'على', 'إلى', 'عن', 'مع', 'هذا', 'هذه', 'تم', 'كان', 'كانت', 'أن', 'إن', 'التي', 'الذي'
        }
        s_words = set(w for w in re.findall(r'\w+', raw_sentence.lower()) if len(w) > 2 and w not in stop_words)
        snip_words = set(w for w in re.findall(r'\w+', snippet.lower()) if len(w) > 2 and w not in stop_words)
        if not s_words or not snip_words:
            return 0.0

        common = s_words & snip_words
        if len(common) < 3:
            return 0.0

        ratio = len(common) / min(len(s_words), 10)
        return min(1.0, ratio)

    def _query_crossref_academic(self, raw_sentence: str) -> Optional[Dict[str, Any]]:
        """
        Queries CrossRef to check if the sentence matches published research papers, journals, or books.
        """
        words = [w for w in re.findall(r'\w+', raw_sentence) if len(w) > 3][:6]
        if len(words) < 3:
            return None
        q = ' '.join(words)

        try:
            url = f"https://api.crossref.org/works?query={urllib.parse.quote(q)}&rows=1"
            r = requests.get(
                url,
                headers={'User-Agent': 'AcademicSimilarityBot/2.0 (mailto:checker@similarity-bot.org)'},
                timeout=self.timeout
            )
            if r.status_code == 200:
                items = r.json().get('message', {}).get('items', [])
                if items:
                    title = items[0].get('title', [''])[0]
                    doi = items[0].get('DOI', '')
                    item_url = items[0].get('URL', f"https://doi.org/{doi}" if doi else '')
                    venue = items[0].get('container-title', [''])[0] if items[0].get('container-title') else ''

                    overlap = self._verify_snippet_match(raw_sentence, title)
                    if overlap >= 0.25:
                        is_web = any(k in venue.lower() or k in item_url.lower() for k in ['mdpi', 'theses', 'dspace', 'commons', 'researchsquare', 'arxiv'])
                        src_type = 'internet' if is_web else 'publication'
                        domain = venue[:35] if venue else (f"Publication ({doi[:18]})" if doi else "Academic Journal")

                        return {
                            'url': item_url,
                            'domain': domain,
                            'snippet': title[:180],
                            'matched_phrase': q,
                            'overlap': overlap,
                            'type': src_type
                        }
        except Exception:
            pass
        return None

    def _query_wikipedia_web(self, raw_sentence: str) -> Optional[Dict[str, Any]]:
        """
        Queries Wikipedia / Open Web Encyclopedia API for direct knowledge/definition matches.
        """
        words = [w for w in re.findall(r'\w+', raw_sentence) if len(w) > 3][:6]
        if len(words) < 3:
            return None
        q = ' '.join(words)
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&utf8=&format=json"
            r = requests.get(url, headers=self.headers, timeout=self.timeout)
            if r.status_code == 200:
                results = r.json().get('query', {}).get('search', [])
                for res in results[:2]:
                    raw_snip = res.get('snippet', '')
                    clean_snip = BeautifulSoup(raw_snip, 'html.parser').get_text()
                    title = res.get('title', '')
                    overlap = self._verify_snippet_match(raw_sentence, title + " " + clean_snip)
                    if overlap >= 0.25:
                        return {
                            'url': f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                            'domain': f"Wikipedia ({title[:25]})",
                            'snippet': clean_snip[:180],
                            'matched_phrase': q,
                            'overlap': overlap,
                            'type': 'internet'
                        }
        except Exception:
            pass
        return None

    def _query_ddg_academic(self, phrase: str, raw_sentence: str) -> Optional[Dict[str, Any]]:
        """
        Queries DuckDuckGo search to find academic papers, theses repositories, and web articles.
        """
        words = phrase.split()
        if len(words) < 5:
            return None
        q_text = ' '.join(words[:7])
        try:
            r = requests.post(
                'https://html.duckduckgo.com/html/',
                data={'q': q_text},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'Referer': 'https://html.duckduckgo.com/'
                },
                timeout=2.0
            )
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for res in soup.find_all('div', class_='result')[:3]:
                    snip_tag = res.find('a', class_='result__snippet')
                    url_tag = res.find('a', class_='result__url')
                    if not snip_tag:
                        continue
                    snippet = snip_tag.text.strip()
                    overlap = self._verify_snippet_match(raw_sentence, snippet)
                    if overlap >= 0.25:
                        raw_u = url_tag.text.strip() if url_tag else ''
                        clean_url = f"https://{raw_u}" if not raw_u.startswith('http') else raw_u
                        domain = urllib.parse.urlparse(clean_url).netloc or raw_u.split('/')[0]
                        is_pub = any(x in domain.lower() for x in ('journal', 'univ', 'edu', 'springer', 'sciencedirect', 'researchgate', 'doi', 'ncbi', 'mdpi', 'frontiers', 'wiley'))
                        return {
                            'url': clean_url,
                            'domain': domain or 'Web Thesis / Portal',
                            'snippet': snippet[:180],
                            'matched_phrase': q_text,
                            'overlap': overlap,
                            'type': 'publication' if is_pub else 'internet'
                        }
        except Exception:
            pass
        return None

    def _query_bing_verified(self, phrase: str, raw_sentence: str) -> Optional[Dict[str, Any]]:
        """
        Queries Bing and verifies the returned snippet actually matches the sentence text.
        """
        words = phrase.split()
        if len(words) < 4:
            return None
        q_text = ' '.join(words[:6])
        encoded = urllib.parse.quote_plus(q_text)
        url = f"https://www.bing.com/search?q={encoded}"

        try:
            r = requests.get(url, headers=self.headers, timeout=2.5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                results = soup.find_all('li', class_='b_algo')
                for res in results[:2]:
                    cite_tag = res.find('cite')
                    link_tag = res.find('h2').find('a') if res.find('h2') else None
                    title_text = link_tag.get_text() if link_tag else ''
                    body_text = res.get_text()

                    raw_url = link_tag.get('href', '') if link_tag else ''
                    clean_url = decode_bing_url(raw_url)
                    domain = cite_tag.text.strip() if cite_tag else urllib.parse.urlparse(clean_url).netloc
                    domain = re.sub(r'https?://', '', domain).split('/')[0].split('›')[0].strip()

                    overlap = self._verify_snippet_match(raw_sentence, title_text + " " + body_text)
                    if overlap >= 0.25:
                        is_pub = any(x in domain.lower() or x in clean_url.lower() for x in ('journal', 'springer', 'sciencedirect', 'researchgate', 'doi', 'ncbi', 'mdpi', 'wiley', 'tandfonline'))
                        return {
                            'url': clean_url,
                            'domain': domain or 'Web Source',
                            'snippet': title_text[:120] if title_text else domain,
                            'matched_phrase': q_text,
                            'overlap': overlap,
                            'type': 'publication' if is_pub else 'internet'
                        }
        except Exception:
            pass
        return None

    def check_single_sentence(self, sentence_obj: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raw = sentence_obj['raw']
        # 1. CrossRef Official Academic DOI Index (Publications)
        res = self._query_crossref_academic(raw)
        if res:
            return res
        # 2. Wikipedia & Open Web Encyclopedia API (Internet Sources)
        res = self._query_wikipedia_web(raw)
        if res:
            return res
        # 3. DuckDuckGo Theses & Academic Web Portals
        res = self._query_ddg_academic(raw, raw)
        if res:
            return res
        # 4. Live Web Search (Bing verified)
        return self._query_bing_verified(raw, raw)

    def check_document_internet(self, sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans candidate sentences live against Internet and Publications repositories.
        """
        candidates = [
            s for s in sentences
            if 7 <= s.get('word_count', 0) <= 45 and not s.get('is_ref', False)
        ]

        if not candidates:
            return {'internet_matches': [], 'internet_percentage': 0.0, 'matched_domains': []}

        # Select well-distributed candidate sentences
        max_q = min(len(candidates), self.max_queries)
        step = max(1, len(candidates) // max_q)
        sampled = candidates[::step][:max_q]

        matches = []
        domains_found = set()
        matched_words = 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_s = {
                executor.submit(self.check_single_sentence, s): s
                for s in sampled
            }
            for future in future_to_s:
                s = future_to_s[future]
                try:
                    res = future.result()
                    if res:
                        w_cnt = s.get('word_count', len(s['raw'].split()))
                        matches.append({
                            'sentence_id': s.get('id', 0),
                            'text': s['raw'],
                            'word_count': w_cnt,
                            'domain': res['domain'],
                            'url': res['url'],
                            'snippet': res['snippet'],
                            'type': res.get('type', 'internet'),
                            'overlap': res.get('overlap', 0.5)
                        })
                        domains_found.add(res['domain'])
                        matched_words += w_cnt
                except Exception:
                    continue

        sample_ratio = len(matches) / max(1, len(sampled))
        total_words = sum(s.get('word_count', len(s['raw'].split())) for s in sentences) or 1

        # Calculate raw percentage of matched words
        internet_pct = round((matched_words / total_words) * 100, 1)

        return {
            'internet_matches': matches,
            'internet_percentage': internet_pct,
            'sample_ratio': round(sample_ratio, 2),
            'matched_words': matched_words,
            'matched_domains': list(domains_found)
        }
