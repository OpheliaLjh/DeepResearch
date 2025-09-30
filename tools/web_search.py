import os
import requests
from typing import Dict, Any, List, Optional

from logger import logger
from time import sleep

BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

def _normalize_freshness(recency_days: Optional[int]) -> Optional[str]:
    if recency_days is None:
        return None
    try:
        d = int(recency_days)
    except Exception:
        return None
    if d <= 0 or d > 365:
        return None
    return f"{d}d"

def _extract_brave_results(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in data.get("web", {}).get("results", []):
        out.append({
            "title": it.get("title"),
            "url": it.get("url"),
            "snippet": it.get("description"),
            "published_at": it.get("age", "") or it.get("meta_url", {}).get("lastmod", "")
        })
    return out

def _brave_search(query: str, top_k: int = 5, recency_days: int = 3650) -> Optional[List[Dict[str, Any]]]:
    # 1) Read and validate token
    sleep(1)  # to avoid rate limits
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key or not api_key.strip():
        logger.warning("[web_search:brave] BRAVE_API_KEY is unset or empty; skipping Brave.")
        return None
    api_key = api_key.strip()

    count = max(1, min(int(top_k or 5), 20))
    search_lang = os.getenv("DR_SEARCH_LANG", "en")
    freshness = _normalize_freshness(recency_days)

    headers = {
        "X-Subscription-Token": api_key,
        "Accept": "application/json",
        "User-Agent": "DeepResearchBot/1.0 (+https://example.org)"
    }

    # 2) Create session; optionally disable proxies to avoid header stripping
    session = requests.Session()
    session.headers.update(headers)
    if os.getenv("DR_DISABLE_PROXIES_FOR_BRAVE", "0") == "1":
        session.trust_env = False  # ignore http_proxy/https_proxy envs
        logger.info("[web_search:brave] Proxies disabled for Brave request (DR_DISABLE_PROXIES_FOR_BRAVE=1).")

    params = {
        "q": query,
        "count": count,
        "search_lang": search_lang,
        "safesearch": "moderate",
    }
    if freshness:
        params["freshness"] = freshness

    # Safe header logging (do not print the token)
    logger.info(f"[web_search:brave] Query='{query}' count={count} lang={search_lang} freshness={params.get('freshness')} token_present=YES")

    try:
        r = session.get(BRAVE_ENDPOINT, params=params, timeout=20)
        if r.status_code in (400, 401, 403, 422):
            # Log server payload for debugging but do not leak token
            try:
                payload = r.json()
            except Exception:
                payload = {"text": r.text[:500]}
            logger.warning(f"[web_search:brave] {r.status_code} on first attempt. payload={payload}")

            # Retry without freshness or extras
            params_retry = {"q": query, "count": count, "search_lang": search_lang}
            logger.info("[web_search:brave] Retrying without freshness/extra params...")
            r = session.get(BRAVE_ENDPOINT, params=params_retry, timeout=20)

        r.raise_for_status()
        data = r.json()
        results = _extract_brave_results(data)
        logger.info(f"[web_search:brave] Got {len(results)} results")
        return results

    except requests.HTTPError as e:
        try:
            payload = r.json()
        except Exception:
            payload = {"text": r.text[:500]}
        logger.error(f"[web_search:brave] HTTPError {e}. payload={payload}")
        return []
    except Exception as e:
        logger.error(f"[web_search:brave] Unexpected error: {e}")
        return []

def web_search_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool entrypoint: returns {"results": [ {title,url,snippet,published_at}, ... ]}
    """
    query = args.get("query", "")
    top_k = int(args.get("top_k", 5))
    recency_days = int(args.get("recency_days", 3650))

    results = (
        _brave_search(query, top_k, recency_days)
    )
    return {"results": results or []}
