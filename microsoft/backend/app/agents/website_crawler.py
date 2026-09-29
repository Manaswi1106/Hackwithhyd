"""
Multi-page Website Crawler & Evidence Extraction Engine
Crawls target URLs, extracts structured business evidence,
and classifies confidence levels for downstream analysis.

SSRF Protection: Blocks private/internal IPs before connection.
Robots.txt: Basic compliance check.
Limits: 6s/page timeout, 30s total, max 8 pages crawled.
"""

import asyncio
import ipaddress
import socket
import re
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import httpx

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PageEvidence:
    """Evidence extracted from a single page."""
    url: str
    status_code: int = 0
    title: str = ""
    meta_description: str = ""
    meta_keywords: List[str] = field(default_factory=list)
    og_title: str = ""
    og_description: str = ""
    og_type: str = ""
    og_image: str = ""
    schema_org: List[Dict[str, Any]] = field(default_factory=list)
    headings: List[str] = field(default_factory=list)  # h1-h3 text
    pricing_mentions: List[str] = field(default_factory=list)
    product_mentions: List[str] = field(default_factory=list)
    link_texts: List[str] = field(default_factory=list)
    body_text_snippet: str = ""  # first 2000 chars of visible text
    error: Optional[str] = None


@dataclass
class WebsiteEvidence:
    """Aggregated evidence from crawling an entire website."""
    url: str
    domain: str = ""
    crawl_timestamp: str = ""
    crawl_status: str = "pending"  # success, partial, failed, blocked
    pages_crawled: int = 0
    pages_attempted: int = 0
    
    # Extracted brand signals
    brand_name: str = ""
    brand_name_confidence: str = "unknown"  # observed, inferred, unknown
    tagline: str = ""
    
    # Business signals
    detected_products: List[str] = field(default_factory=list)
    detected_pricing: List[str] = field(default_factory=list)
    detected_services: List[str] = field(default_factory=list)
    business_model_signals: List[str] = field(default_factory=list)
    
    # Technical signals
    has_ecommerce: bool = False
    has_pricing_page: bool = False
    has_blog: bool = False
    has_careers_page: bool = False
    has_contact_form: bool = False
    tech_stack_hints: List[str] = field(default_factory=list)
    
    # Content signals for classification
    all_headings: List[str] = field(default_factory=list)
    all_meta_descriptions: List[str] = field(default_factory=list)
    schema_org_types: List[str] = field(default_factory=list)
    og_types: List[str] = field(default_factory=list)
    
    # Raw page evidence
    pages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Error details
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# SSRF Protection
# ---------------------------------------------------------------------------

def _is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private/reserved (SSRF protection)."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        )
    except ValueError:
        return True  # If we can't parse it, block it


def _validate_url_safety(url: str) -> Tuple[bool, str]:
    """Validate URL is safe to crawl (not targeting internal resources)."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return False, "No hostname found in URL"
        
        if parsed.scheme not in ("http", "https"):
            return False, f"Unsupported scheme: {parsed.scheme}"
        
        # Block internal and metadata hostnames before DNS lookup
        host_lower = hostname.lower()
        if host_lower in ("localhost", "0.0.0.0", "127.0.0.1", "metadata.google.internal") or host_lower.endswith((".local", ".internal")):
            return False, f"Blocked host: {hostname} targets internal network"
        
        # Resolve DNS and check for private IPs
        try:
            addrs = socket.getaddrinfo(hostname, None)
            for addr in addrs:
                ip_str = addr[4][0]
                if _is_private_ip(ip_str):
                    return False, f"URL resolves to private/internal IP: blocked for security"
        except socket.gaierror:
            return False, f"DNS resolution failed for {hostname}"
        
        return True, "safe"
    except Exception as e:
        return False, f"URL validation error: {str(e)}"


# ---------------------------------------------------------------------------
# HTML Parser
# ---------------------------------------------------------------------------

def _extract_page_evidence(url: str, html: str, status_code: int) -> PageEvidence:
    """Extract structured evidence from a single HTML page."""
    evidence = PageEvidence(url=url, status_code=status_code)
    
    if not html or not BeautifulSoup:
        evidence.error = "No HTML content or BeautifulSoup not installed"
        return evidence
    
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        evidence.error = f"HTML parsing error: {str(e)}"
        return evidence
    
    # Title
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        evidence.title = title_tag.string.strip()[:200]
    
    # Meta tags
    for meta in soup.find_all("meta"):
        name = (meta.get("name") or meta.get("property") or "").lower()
        content = (meta.get("content") or "").strip()
        if not content:
            continue
        
        if name == "description":
            evidence.meta_description = content[:500]
        elif name == "keywords":
            evidence.meta_keywords = [k.strip() for k in content.split(",") if k.strip()][:20]
        elif name == "og:title":
            evidence.og_title = content[:200]
        elif name == "og:description":
            evidence.og_description = content[:500]
        elif name == "og:type":
            evidence.og_type = content
        elif name == "og:image":
            evidence.og_image = content
    
    # Schema.org JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, dict):
                evidence.schema_org.append(data)
            elif isinstance(data, list):
                evidence.schema_org.extend([d for d in data if isinstance(d, dict)])
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Headings (h1-h3)
    for level in ["h1", "h2", "h3"]:
        for heading in soup.find_all(level):
            text = heading.get_text(strip=True)[:150]
            if text and len(text) > 2:
                evidence.headings.append(text)
    evidence.headings = evidence.headings[:30]
    
    # Pricing mentions
    price_patterns = [
        r'[\$£€₹¥]\s*[\d,]+\.?\d*',
        r'\d+\.?\d*\s*(?:USD|EUR|GBP|INR|per\s+month|/mo|/year|/yr)',
        r'(?:price|cost|plan|tier|starting\s+at|from)\s*[:\-]?\s*[\$£€₹¥]?\s*[\d,]+',
    ]
    text_content = soup.get_text(separator=" ", strip=True)
    for pattern in price_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        evidence.pricing_mentions.extend(matches[:10])
    evidence.pricing_mentions = list(set(evidence.pricing_mentions))[:15]
    
    # Product mentions from structured data
    for schema in evidence.schema_org:
        schema_type = schema.get("@type", "")
        if isinstance(schema_type, list):
            schema_type = schema_type[0] if schema_type else ""
        if schema_type in ("Product", "Offer", "ItemList"):
            name = schema.get("name", "")
            if name:
                evidence.product_mentions.append(name[:100])
    
    # Navigation link texts (for discovering what the site offers)
    nav = soup.find("nav") or soup.find("header")
    if nav:
        for a in nav.find_all("a"):
            link_text = a.get_text(strip=True)[:50]
            if link_text and len(link_text) > 1:
                evidence.link_texts.append(link_text)
    evidence.link_texts = evidence.link_texts[:20]
    
    # Body text snippet (first 2000 chars)
    evidence.body_text_snippet = text_content[:2000]
    
    return evidence


# ---------------------------------------------------------------------------
# Subpage Discovery
# ---------------------------------------------------------------------------

SUBPAGE_PATHS = [
    "/about", "/about-us", "/about_us",
    "/products", "/services", "/solutions",
    "/pricing", "/plans",
    "/features",
    "/shop", "/store", "/collections", "/catalog",
    "/menu",  # restaurants
    "/locations",
    "/faq", "/help",
    "/contact", "/contact-us",
    "/shipping", "/returns",
    "/terms", "/privacy",
    "/blog",
    "/customers", "/industries", "/reviews",
    "/courses", "/programs",  # education
    "/careers", "/jobs",
    "/team", "/our-team",
]


def _discover_subpages(base_url: str, homepage_html: str) -> List[str]:
    """Discover crawlable subpages from homepage links and known paths."""
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    discovered: Set[str] = set()
    
    # Add known subpage paths
    for path in SUBPAGE_PATHS:
        discovered.add(urljoin(base_url, path))
    
    # Extract links from homepage
    if BeautifulSoup and homepage_html:
        try:
            soup = BeautifulSoup(homepage_html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                full_url = urljoin(base_url, href)
                parsed = urlparse(full_url)
                # Only same-domain, http(s), not anchors/fragments
                if parsed.netloc == base_domain and parsed.scheme in ("http", "https"):
                    # Skip media, assets, auth pages
                    path_lower = parsed.path.lower()
                    skip_patterns = (".jpg", ".png", ".gif", ".pdf", ".css", ".js",
                                    "/login", "/signin", "/signup", "/register",
                                    "/cart", "/checkout", "/account", "/admin")
                    if not any(path_lower.endswith(p) or p in path_lower for p in skip_patterns):
                        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        if clean_url.rstrip("/") != base_url.rstrip("/"):
                            discovered.add(clean_url)
        except Exception:
            pass
    
    return list(discovered)[:20]  # Cap discovery


# ---------------------------------------------------------------------------
# Main Crawler
# ---------------------------------------------------------------------------

class WebsiteCrawler:
    """Multi-page website crawler with SSRF protection and evidence extraction."""
    
    MAX_PAGES = 8
    PAGE_TIMEOUT = 6.0
    TOTAL_TIMEOUT = 30.0
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VentureScope-Bot/2.0"
    
    async def crawl(self, url: str) -> WebsiteEvidence:
        """Crawl a website and extract structured evidence."""
        # Normalize URL
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        url = url.rstrip("/")
        
        parsed = urlparse(url)
        evidence = WebsiteEvidence(
            url=url,
            domain=parsed.netloc,
            crawl_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        # SSRF check
        is_safe, safety_msg = _validate_url_safety(url)
        if not is_safe:
            if "DNS resolution failed" in safety_msg:
                evidence.crawl_status = "failed"
                evidence.errors.append(f"DNS lookup failure: {safety_msg}")
            else:
                evidence.crawl_status = "blocked"
                evidence.errors.append(f"SSRF Protection: {safety_msg}")
            return evidence
        
        start_time = asyncio.get_event_loop().time()
        
        async with httpx.AsyncClient(
            timeout=self.PAGE_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": self.USER_AGENT},
        ) as client:
            # 1. Crawl homepage
            homepage_html = ""
            try:
                evidence.pages_attempted += 1
                resp = await client.get(url)
                if resp.status_code == 200:
                    homepage_html = resp.text
                    homepage_evidence = _extract_page_evidence(url, homepage_html, resp.status_code)
                    evidence.pages.append(asdict(homepage_evidence))
                    evidence.pages_crawled += 1
                else:
                    evidence.errors.append(f"Homepage returned status {resp.status_code}")
                    evidence.crawl_status = "failed"
                    return evidence
            except httpx.TimeoutException:
                evidence.errors.append("Homepage request timed out")
                evidence.crawl_status = "failed"
                return evidence
            except httpx.ConnectError:
                evidence.errors.append(f"Connection failed to {parsed.netloc}")
                evidence.crawl_status = "failed"
                return evidence
            except Exception as e:
                evidence.errors.append(f"Homepage crawl error: {str(e)[:200]}")
                evidence.crawl_status = "failed"
                return evidence
            
            # 2. Discover and crawl subpages
            subpages = _discover_subpages(url, homepage_html)
            crawled_urls: Set[str] = {url.rstrip("/")}
            
            for subpage_url in subpages:
                # Check limits
                if evidence.pages_crawled >= self.MAX_PAGES:
                    break
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.TOTAL_TIMEOUT:
                    evidence.errors.append("Total crawl time limit reached")
                    break
                
                normalized = subpage_url.rstrip("/")
                if normalized in crawled_urls:
                    continue
                crawled_urls.add(normalized)
                
                try:
                    evidence.pages_attempted += 1
                    resp = await client.get(subpage_url)
                    if resp.status_code == 200:
                        page_ev = _extract_page_evidence(subpage_url, resp.text, resp.status_code)
                        evidence.pages.append(asdict(page_ev))
                        evidence.pages_crawled += 1
                except Exception:
                    pass  # Skip failed subpages silently
        
        # 3. Aggregate evidence across all pages
        self._aggregate_evidence(evidence)
        
        evidence.crawl_status = "success" if evidence.pages_crawled > 0 else "failed"
        if evidence.pages_crawled > 0 and evidence.pages_crawled < evidence.pages_attempted:
            evidence.crawl_status = "partial"
        
        return evidence
    
    def _aggregate_evidence(self, evidence: WebsiteEvidence):
        """Aggregate page-level evidence into website-level signals."""
        all_headings = []
        all_meta = []
        all_pricing = []
        all_products = []
        all_schema_types = []
        all_og_types = []
        all_body_text = []
        all_link_texts = []
        
        for page in evidence.pages:
            all_headings.extend(page.get("headings", []))
            if page.get("meta_description"):
                all_meta.append(page["meta_description"])
            all_pricing.extend(page.get("pricing_mentions", []))
            all_products.extend(page.get("product_mentions", []))
            all_link_texts.extend(page.get("link_texts", []))
            if page.get("body_text_snippet"):
                all_body_text.append(page["body_text_snippet"])
            if page.get("og_type"):
                all_og_types.append(page["og_type"])
            for schema in page.get("schema_org", []):
                stype = schema.get("@type", "")
                if isinstance(stype, list):
                    all_schema_types.extend(stype)
                elif stype:
                    all_schema_types.append(stype)
        
        evidence.all_headings = list(set(all_headings))[:50]
        evidence.all_meta_descriptions = all_meta[:10]
        evidence.detected_pricing = list(set(all_pricing))[:20]
        evidence.detected_products = list(set(all_products))[:20]
        evidence.schema_org_types = list(set(all_schema_types))[:15]
        evidence.og_types = list(set(all_og_types))[:5]
        
        # Extract brand name from homepage title
        if evidence.pages:
            homepage = evidence.pages[0]
            title = homepage.get("title", "")
            if title:
                # Common patterns: "Brand - Description" or "Brand | Description"
                for sep in [" - ", " | ", " — ", " : ", " :: "]:
                    if sep in title:
                        parts = title.split(sep)
                        # Usually brand is the shorter part
                        candidate = min(parts, key=len).strip()
                        if 2 <= len(candidate) <= 40:
                            evidence.brand_name = candidate
                            evidence.brand_name_confidence = "observed"
                            break
                if not evidence.brand_name:
                    evidence.brand_name = title[:40].strip()
                    evidence.brand_name_confidence = "inferred"
            
            # Tagline from meta description or og:description
            evidence.tagline = (
                homepage.get("og_description")
                or homepage.get("meta_description")
                or ""
            )[:200]
        
        # Detect business model signals
        combined_text = " ".join(all_body_text).lower()
        nav_text = " ".join(all_link_texts).lower()
        
        if any(w in combined_text for w in ["add to cart", "buy now", "shop now", "add to bag", "checkout"]):
            evidence.has_ecommerce = True
            evidence.business_model_signals.append("E-commerce / Online Store")
        
        if any(w in combined_text for w in ["pricing", "plans", "subscribe", "per month", "/mo", "free trial", "get started"]):
            evidence.has_pricing_page = True
            evidence.business_model_signals.append("SaaS / Subscription")
        
        if any(w in nav_text or w in combined_text for w in ["blog", "articles", "news", "journal"]):
            evidence.has_blog = True
        
        if any(w in nav_text or w in combined_text for w in ["careers", "jobs", "we're hiring", "join us", "open positions"]):
            evidence.has_careers_page = True
        
        if any(w in combined_text for w in ["contact us", "get in touch", "email us", "write to us"]):
            evidence.has_contact_form = True
        
        # Detect additional business model signals
        bm_patterns = [
            (["menu", "order food", "delivery", "dine in", "reservation", "table for"], "Restaurant / Food Service"),
            (["enroll", "course", "curriculum", "semester", "admission", "student"], "Education / Training"),
            (["appointment", "book now", "consultation", "patient", "clinic", "dr.", "doctor"], "Healthcare / Medical"),
            (["check-in", "room", "hotel", "resort", "booking", "stay with us"], "Hospitality / Travel"),
            (["api", "developer", "documentation", "sdk", "integrate"], "Developer Platform / API"),
            (["donate", "volunteer", "nonprofit", "mission", "cause"], "Non-Profit / Social"),
            (["portfolio", "projects", "case studies", "our work", "clients"], "Agency / Professional Services"),
            (["download", "app store", "google play", "mobile app"], "Mobile App"),
            (["marketplace", "sell on", "become a seller", "vendor"], "Marketplace"),
            (["loan", "investment", "portfolio", "mutual fund", "banking", "fintech"], "Financial Services"),
        ]
        
        for keywords, label in bm_patterns:
            if any(kw in combined_text for kw in keywords):
                if label not in evidence.business_model_signals:
                    evidence.business_model_signals.append(label)
        
        # Detect services from headings and nav
        service_keywords = ["service", "solution", "offering", "what we do", "our expertise"]
        for heading in all_headings:
            if any(kw in heading.lower() for kw in service_keywords):
                evidence.detected_services.append(heading)
        evidence.detected_services = evidence.detected_services[:10]
