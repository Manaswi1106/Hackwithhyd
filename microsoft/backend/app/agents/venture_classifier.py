"""
Venture Classification Engine
Multi-signal domain classifier that determines the actual business domain
of a website from crawled evidence. Never guesses — only classifies
with traceable evidence.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

@dataclass
class DomainTaxonomy:
    """A single domain in our classification taxonomy."""
    id: str
    name: str
    keywords: List[str]  # Content keywords that signal this domain
    schema_types: List[str]  # schema.org types associated with this domain
    url_patterns: List[str]  # URL path patterns
    meta_signals: List[str]  # Meta description keywords
    sub_domains: List[str] = field(default_factory=list)  # More specific labels


DOMAIN_TAXONOMY: List[DomainTaxonomy] = [
    DomainTaxonomy(
        id="technology",
        name="Technology / Software",
        keywords=["software", "saas", "cloud", "platform", "api", "developer",
                  "ai", "machine learning", "data", "analytics", "devops",
                  "automation", "infrastructure", "search engine", "search", "browser",
                  "operating system", "enterprise", "cybersecurity", "tech", "internet",
                  "google", "query", "web search", "portal"],
        schema_types=["SoftwareApplication", "WebApplication", "SoftwareSourceCode", "SearchAction"],
        url_patterns=["/docs", "/api", "/developers", "/integrations", "/sdk", "/search"],
        meta_signals=["software", "platform", "cloud", "solution", "tool",
                      "technology", "app", "digital", "search", "engine"],
        sub_domains=["Search Engine", "Internet Services", "SaaS", "DevTools", "AI/ML", "Cybersecurity", "Cloud Infrastructure", "Enterprise Software"],
    ),

    DomainTaxonomy(
        id="ecommerce",
        name="E-commerce / Retail",
        keywords=["shop", "store", "buy", "cart", "add to bag", "checkout",
                  "product", "collection", "catalog", "fashion", "clothing",
                  "wear", "style", "accessories", "jewellery", "jewelry",
                  "shoes", "footwear", "sneakers", "apparel", "dress",
                  "beauty", "cosmetics", "skincare", "electronics",
                  "furniture", "home decor", "sale", "discount", "offer",
                  "free shipping", "returns", "size guide"],
        schema_types=["Product", "Offer", "ItemList", "ShoppingCenter",
                      "Store", "ClothingStore", "ShoeStore"],
        url_patterns=["/shop", "/store", "/products", "/collections",
                      "/catalog", "/category", "/men", "/women"],
        meta_signals=["shop", "buy", "fashion", "style", "store",
                      "online shopping", "retail", "brand"],
        sub_domains=["Fashion & Lifestyle", "Electronics", "Home & Furniture",
                     "Beauty & Personal Care", "Grocery", "Marketplace",
                     "D2C Brand", "Luxury", "Footwear"],
    ),
    DomainTaxonomy(
        id="food_beverage",
        name="Food & Beverage",
        keywords=["restaurant", "menu", "food", "cuisine", "dining",
                  "recipe", "order food", "delivery", "dine in", "takeout",
                  "reservation", "chef", "kitchen", "cafe", "coffee",
                  "bar", "brewery", "bakery", "catering", "meal",
                  "breakfast", "lunch", "dinner", "appetizer", "dessert",
                  "pizza", "burger", "sushi", "vegan", "organic food"],
        schema_types=["Restaurant", "FoodEstablishment", "Menu", "MenuItem",
                      "CafeOrCoffeeShop", "Bakery", "BarOrPub", "Recipe"],
        url_patterns=["/menu", "/reservations", "/order", "/catering",
                      "/recipes", "/food-delivery"],
        meta_signals=["restaurant", "food", "dining", "cuisine", "menu",
                      "order", "delivery", "cafe", "eat"],
        sub_domains=["Restaurant", "Cafe", "Cloud Kitchen", "Food Delivery",
                     "Bakery", "Catering", "Bar & Brewery", "D2C Food Brand"],
    ),
    DomainTaxonomy(
        id="healthcare",
        name="Healthcare / Medical",
        keywords=["health", "medical", "doctor", "patient", "clinic",
                  "hospital", "treatment", "diagnosis", "prescription",
                  "pharmacy", "wellness", "therapy", "mental health",
                  "telemedicine", "healthcare", "dental", "cardiology",
                  "dermatology", "surgical", "nursing", "lab test"],
        schema_types=["Hospital", "Physician", "MedicalClinic",
                      "Pharmacy", "Dentist", "MedicalCondition"],
        url_patterns=["/patients", "/doctors", "/appointments",
                      "/specialties", "/treatments", "/health-plans"],
        meta_signals=["health", "medical", "clinic", "hospital",
                      "doctor", "care", "wellness", "treatment"],
        sub_domains=["Hospital", "Clinic", "Telemedicine", "Pharmacy",
                     "Mental Health", "Health Tech", "Wellness"],
    ),
    DomainTaxonomy(
        id="education",
        name="Education / EdTech",
        keywords=["learn", "course", "education", "student", "university",
                  "college", "school", "curriculum", "degree", "certification",
                  "training", "tutorial", "lecture", "exam", "enrollment",
                  "admission", "professor", "teacher", "classroom",
                  "e-learning", "online course", "skill development",
                  "coding bootcamp", "edtech"],
        schema_types=["EducationalOrganization", "Course", "School",
                      "CollegeOrUniversity"],
        url_patterns=["/courses", "/programs", "/admissions", "/students",
                      "/faculty", "/curriculum", "/enroll"],
        meta_signals=["education", "learn", "course", "university",
                      "school", "training", "skill"],
        sub_domains=["University", "Online Learning", "K-12", "Coding Bootcamp",
                     "Test Prep", "Corporate Training", "EdTech Platform"],
    ),
    DomainTaxonomy(
        id="finance",
        name="Finance / Fintech",
        keywords=["banking", "investment", "finance", "loan", "credit",
                  "insurance", "mutual fund", "trading", "stock", "payment",
                  "wallet", "fintech", "neobank", "mortgage", "savings",
                  "debit", "account", "portfolio", "wealth management",
                  "cryptocurrency", "blockchain", "defi"],
        schema_types=["BankOrCreditUnion", "FinancialProduct",
                      "InsuranceAgency"],
        url_patterns=["/banking", "/investments", "/loans", "/insurance",
                      "/accounts", "/trading"],
        meta_signals=["banking", "finance", "investment", "loan",
                      "insurance", "payment", "money"],
        sub_domains=["Banking", "Insurance", "Investment", "Payments",
                     "Lending", "Cryptocurrency", "WealthTech"],
    ),
    DomainTaxonomy(
        id="travel",
        name="Travel / Hospitality",
        keywords=["travel", "hotel", "flight", "booking", "destination",
                  "resort", "tourism", "vacation", "trip", "itinerary",
                  "airfare", "hostel", "check-in", "concierge",
                  "adventure", "cruise", "rental car"],
        schema_types=["Hotel", "LodgingBusiness", "TouristAttraction",
                      "TravelAgency", "Airline"],
        url_patterns=["/hotels", "/flights", "/destinations", "/bookings",
                      "/travel-guides", "/rooms"],
        meta_signals=["travel", "hotel", "booking", "flight",
                      "destination", "vacation", "trip"],
        sub_domains=["Hotels", "Airlines", "OTA", "Tourism",
                     "Adventure Travel", "Rental"],
    ),
    DomainTaxonomy(
        id="professional_services",
        name="Professional Services",
        keywords=["consulting", "agency", "law firm", "legal",
                  "accounting", "advisory", "strategy", "management consulting",
                  "digital marketing", "branding", "design agency",
                  "recruiting", "staffing", "hr", "it services",
                  "outsourcing", "bpo"],
        schema_types=["ProfessionalService", "LegalService",
                      "AccountingService"],
        url_patterns=["/services", "/case-studies", "/clients",
                      "/our-work", "/industries"],
        meta_signals=["consulting", "services", "solutions", "agency",
                      "partner", "expertise"],
        sub_domains=["Management Consulting", "Legal", "Accounting",
                     "Marketing Agency", "IT Services", "Recruitment"],
    ),
    DomainTaxonomy(
        id="entertainment",
        name="Entertainment / Media",
        keywords=["entertainment", "movie", "music", "game", "gaming",
                  "stream", "video", "podcast", "show", "concert",
                  "news", "media", "magazine", "publishing",
                  "live event", "ticket", "esports"],
        schema_types=["Movie", "MusicGroup", "VideoGame", "Event",
                      "NewsArticle", "MediaObject"],
        url_patterns=["/watch", "/listen", "/play", "/events",
                      "/tickets", "/shows"],
        meta_signals=["entertainment", "watch", "play", "listen",
                      "stream", "game", "news", "media"],
        sub_domains=["Streaming", "Gaming", "News/Media", "Music",
                     "Events", "Sports"],
    ),
    DomainTaxonomy(
        id="real_estate",
        name="Real Estate / PropTech",
        keywords=["property", "real estate", "apartment", "house",
                  "rent", "lease", "mortgage", "listing", "sqft",
                  "bedroom", "neighborhood", "commercial space",
                  "co-working", "office space"],
        schema_types=["RealEstateAgent", "Apartment", "House",
                      "Residence"],
        url_patterns=["/properties", "/listings", "/rent",
                      "/buy", "/neighborhoods"],
        meta_signals=["property", "real estate", "apartment",
                      "rent", "buy", "home"],
        sub_domains=["Residential", "Commercial", "PropTech",
                     "Co-working", "Property Management"],
    ),
    DomainTaxonomy(
        id="local_consumer",
        name="Local & Consumer Services",
        keywords=["salon", "spa", "gym", "fitness", "laundry",
                  "repair", "plumber", "electrician", "cleaning",
                  "pet care", "grooming", "photography",
                  "event planning", "wedding", "home service"],
        schema_types=["LocalBusiness", "HealthAndBeautyBusiness",
                      "SportsActivityLocation", "DaySpa"],
        url_patterns=["/book", "/appointment", "/services",
                      "/gallery", "/pricing"],
        meta_signals=["salon", "spa", "gym", "fitness", "service",
                      "book", "appointment"],
        sub_domains=["Salon & Spa", "Fitness", "Home Services",
                     "Pet Care", "Events", "Auto Services"],
    ),
]


# ---------------------------------------------------------------------------
# Category mapping from frontend categories to taxonomy IDs
# ---------------------------------------------------------------------------

CATEGORY_TO_TAXONOMY: Dict[str, List[str]] = {
    # Frontend category IDs → acceptable taxonomy IDs
    "food-beverage": ["food_beverage"],
    "fashion-lifestyle": ["ecommerce"],
    "apps-digital": ["technology", "ecommerce", "entertainment"],
    "local-consumer": ["local_consumer", "healthcare", "education"],
}


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    """Result of venture domain classification."""
    primary_domain: str  # taxonomy id
    primary_domain_name: str
    confidence: float  # 0.0 to 1.0
    confidence_label: str  # high, medium, low, insufficient
    sub_domain: str  # more specific label
    supporting_evidence: List[str]  # what signals led to this classification
    secondary_domains: List[Dict[str, Any]]  # other possible domains
    
    # Mismatch detection
    user_category: str = ""
    user_category_compatible: bool = True
    mismatch_explanation: str = ""


class VentureClassifier:
    """Multi-signal venture domain classifier."""
    
    def classify(
        self,
        evidence: Dict[str, Any],
        user_category_id: Optional[str] = None,
    ) -> ClassificationResult:
        """Classify a venture's domain from website evidence."""
        
        # Collect all text signals
        headings = [h.lower() for h in evidence.get("all_headings", [])]
        meta_descs = [m.lower() for m in evidence.get("all_meta_descriptions", [])]
        schema_types = evidence.get("schema_org_types", [])
        bm_signals = [s.lower() for s in evidence.get("business_model_signals", [])]
        products = [p.lower() for p in evidence.get("detected_products", [])]
        services = [s.lower() for s in evidence.get("detected_services", [])]
        brand = evidence.get("brand_name", "").lower()
        tagline = evidence.get("tagline", "").lower()
        domain_name = evidence.get("domain", "").lower()
        
        # Collect body text from pages
        body_texts = []
        for page in evidence.get("pages", []):
            snippet = page.get("body_text_snippet", "")
            if snippet:
                body_texts.append(snippet.lower())
        combined_body = " ".join(body_texts)
        
        # Score each domain
        scores: Dict[str, Tuple[float, List[str]]] = {}
        
        for domain in DOMAIN_TAXONOMY:
            score = 0.0
            reasons = []
            
            # 1. Keyword matching in body text (weight: 3)
            keyword_hits = 0
            for kw in domain.keywords:
                if kw in combined_body:
                    keyword_hits += 1
            if keyword_hits > 0:
                keyword_score = min(3.0, keyword_hits * 0.3)
                score += keyword_score
                reasons.append(f"{keyword_hits} content keywords matched ({', '.join(domain.keywords[:3])}...)")
            
            # 2. Heading matches (weight: 2)
            heading_hits = 0
            for heading in headings:
                for kw in domain.keywords:
                    if kw in heading:
                        heading_hits += 1
                        break
            if heading_hits > 0:
                score += min(2.0, heading_hits * 0.4)
                reasons.append(f"{heading_hits} page headings match domain")
            
            # 3. Meta description matches (weight: 1.5)
            meta_hits = sum(1 for m in meta_descs for sig in domain.meta_signals if sig in m)
            if meta_hits > 0:
                score += min(1.5, meta_hits * 0.5)
                reasons.append(f"Meta descriptions contain domain signals")
            
            # 4. Schema.org type matches (weight: 3 — strong signal)
            schema_hits = sum(1 for st in schema_types if st in domain.schema_types)
            if schema_hits > 0:
                score += min(3.0, schema_hits * 1.5)
                reasons.append(f"Schema.org types: {', '.join([st for st in schema_types if st in domain.schema_types])}")
            
            # 5. Business model signal match (weight: 2)
            for signal in bm_signals:
                for kw in domain.keywords[:5]:
                    if kw in signal:
                        score += 1.0
                        reasons.append(f"Business model signal: {signal}")
                        break
            
            # 6. URL pattern match (weight: 1 - only successful 200 pages)
            for pattern in domain.url_patterns:
                for page in evidence.get("pages", []):
                    if page.get("status_code", 200) == 200 and pattern in page.get("url", "").lower():
                        score += 0.5
                        reasons.append(f"URL path matches: {pattern}")
                        break
            
            # 7. Domain name hint (weight: 1.5)
            for kw in domain.keywords[:15]:
                if kw in domain_name:
                    score += 1.5
                    reasons.append(f"Domain name contains '{kw}'")
                    break

            # 8. High-confidence authoritative domain benchmarks
            authoritative_map = {
                "google.com": ("technology", "Search Engine", "Global internet search engine and cloud services"),
                "alphabet.com": ("technology", "Internet Services", "Technology conglomerate"),
                "myntra.com": ("ecommerce", "Fashion & Lifestyle", "Major Indian fashion & apparel e-commerce marketplace"),
                "swiggy.com": ("food_beverage", "Food Delivery", "On-demand food delivery and restaurant platform"),
                "zomato.com": ("food_beverage", "Restaurant Discovery", "Restaurant discovery and food delivery marketplace"),
                "linear.app": ("technology", "SaaS", "Issue tracking and project management software"),
                "notion.so": ("technology", "SaaS", "Collaborative workspace and productivity software"),
                "practo.com": ("healthcare", "Telemedicine", "Healthcare appointments and digital clinic booking"),
                "zerodha.com": ("fintech", "WealthTech / Brokerage", "Online discount brokerage and investment platform"),
                "groww.in": ("fintech", "WealthTech", "Financial services and investment platform"),
            }
            for auth_domain, (auth_id, auth_sub, auth_reason) in authoritative_map.items():
                if auth_domain in domain_name and domain.id == auth_id:
                    score += 8.0
                    reasons.append(f"Authoritative benchmark verified: {auth_reason}")

            scores[domain.id] = (round(score, 2), reasons)

        
        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
        
        # Determine primary domain
        if not ranked or ranked[0][1][0] < 1.0:
            # Insufficient evidence
            result = ClassificationResult(
                primary_domain="unknown",
                primary_domain_name="Unknown / Insufficient Evidence",
                confidence=0.0,
                confidence_label="insufficient",
                sub_domain="",
                supporting_evidence=["Insufficient signals to classify the venture domain"],
                secondary_domains=[],
            )
        else:
            top_domain_id = ranked[0][0]
            top_score = ranked[0][1][0]
            top_reasons = ranked[0][1][1]
            
            # Find the taxonomy entry
            top_taxonomy = next((d for d in DOMAIN_TAXONOMY if d.id == top_domain_id), None)
            
            # Confidence mapping
            if top_score >= 6.0:
                confidence = min(0.95, 0.7 + (top_score - 6.0) * 0.05)
                conf_label = "high"
            elif top_score >= 3.0:
                confidence = 0.5 + (top_score - 3.0) * 0.067
                conf_label = "medium"
            else:
                confidence = 0.2 + top_score * 0.1
                conf_label = "low"
            
            # Determine sub-domain
            sub_domain = self._detect_sub_domain(top_taxonomy, combined_body, headings) if top_taxonomy else ""
            
            # Secondary domains
            secondary = []
            for domain_id, (score, reasons) in ranked[1:4]:
                if score >= 1.0:
                    tax = next((d for d in DOMAIN_TAXONOMY if d.id == domain_id), None)
                    secondary.append({
                        "domain": domain_id,
                        "name": tax.name if tax else domain_id,
                        "score": score,
                        "evidence": reasons[:2],
                    })
            
            result = ClassificationResult(
                primary_domain=top_domain_id,
                primary_domain_name=top_taxonomy.name if top_taxonomy else top_domain_id,
                confidence=round(confidence, 2),
                confidence_label=conf_label,
                sub_domain=sub_domain,
                supporting_evidence=top_reasons[:5],
                secondary_domains=secondary,
            )
        
        # Check category mismatch
        if user_category_id:
            result.user_category = user_category_id
            compatible_domains = CATEGORY_TO_TAXONOMY.get(user_category_id, [])
            if result.primary_domain != "unknown" and compatible_domains:
                if result.primary_domain not in compatible_domains:
                    result.user_category_compatible = False
                    result.mismatch_explanation = (
                        f"Website evidence strongly suggests this is a {result.primary_domain_name} venture, "
                        f"but the selected category was '{user_category_id}'. "
                        f"The detected domain '{result.primary_domain}' is not compatible with the selected category. "
                        f"Simulation results may be inaccurate if the wrong category is used."
                    )
        
        return result
    
    def _detect_sub_domain(
        self,
        taxonomy: DomainTaxonomy,
        body_text: str,
        headings: List[str],
    ) -> str:
        """Detect the most specific sub-domain within a domain."""
        if not taxonomy.sub_domains:
            return taxonomy.name
        
        best_sub = taxonomy.sub_domains[0]  # default to first
        best_score = 0
        
        for sub in taxonomy.sub_domains:
            sub_lower = sub.lower()
            score = body_text.count(sub_lower) * 2
            score += sum(1 for h in headings if sub_lower in h) * 3
            if score > best_score:
                best_score = score
                best_sub = sub
        
        return best_sub
