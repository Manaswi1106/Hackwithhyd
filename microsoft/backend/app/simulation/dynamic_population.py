"""
Domain-Agnostic Dynamic Population Generator
Generates 500 calibrated synthetic participants based on the detected
venture domain. Replaces hardcoded Hyderabad footwear population with
dynamic segments and personas appropriate for any business domain.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
import random


@dataclass
class DomainSegmentTemplate:
    """Template for a customer segment within a domain."""
    id: str
    name: str
    label: str
    age_band: str
    spend_band: str  # upper, upper_middle, middle, value
    channel: str
    frequency: float  # base purchase frequency
    sensitivity: str  # Low, Medium, High
    motivation: str
    objections: List[str]
    personas: List[Dict[str, Any]]
    why_they_buy: List[str] = field(default_factory=list)
    why_they_dont_buy: List[str] = field(default_factory=list)
    what_would_change_decision: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Domain-Specific Segment Templates
# ---------------------------------------------------------------------------

ECOMMERCE_SEGMENTS: List[DomainSegmentTemplate] = [
    DomainSegmentTemplate(
        id="trend_shoppers",
        name="Trend-Conscious Online Shoppers",
        label="Trend Shoppers",
        age_band="22-34",
        spend_band="upper_middle",
        channel="Mobile App & Social Commerce",
        frequency=3.5,
        sensitivity="Medium",
        motivation="Latest trends, social validation, and curated style discovery",
        objections=["Fast fashion sustainability concerns", "Size consistency across brands"],
        personas=[
            {"name": "Priya S.", "age": 26, "title": "Marketing Manager", "locality": "Madhapur", "quote": "I follow trends on Instagram and want the exact looks I see styled by influencers."},
            {"name": "Ravi K.", "age": 30, "title": "Product Designer", "locality": "Gachibowli", "quote": "Willing to pay premium for unique pieces that stand out in the tech campus crowd."},
        ],
    ),
    DomainSegmentTemplate(
        id="value_seekers",
        name="Value-Conscious Comparison Shoppers",
        label="Value Seekers",
        age_band="25-45",
        spend_band="middle",
        channel="Marketplace & Price Comparison",
        frequency=2.0,
        sensitivity="High",
        motivation="Best value for money, deals, cashback, and free shipping",
        objections=["Premium pricing without visible quality difference", "No free returns"],
        personas=[
            {"name": "Meena R.", "age": 35, "title": "School Teacher", "locality": "Kukatpally", "quote": "I always compare prices on Amazon vs Flipkart before buying anything."},
        ],
    ),
    DomainSegmentTemplate(
        id="premium_buyers",
        name="Premium & Aspirational Buyers",
        label="Premium Buyers",
        age_band="30-50",
        spend_band="upper",
        channel="D2C Website & Flagship Stores",
        frequency=2.5,
        sensitivity="Low",
        motivation="Quality, brand prestige, exclusivity, and premium experience",
        objections=["Lack of brand heritage compared to established luxury labels"],
        personas=[
            {"name": "Vikram N.", "age": 42, "title": "VP Engineering", "locality": "Banjara Hills", "quote": "I look for quality craftsmanship and am willing to pay for brands that deliver."},
        ],
    ),
    DomainSegmentTemplate(
        id="impulse_buyers",
        name="Social Media Impulse Buyers",
        label="Impulse Buyers",
        age_band="18-28",
        spend_band="middle",
        channel="Instagram & Influencer Links",
        frequency=4.0,
        sensitivity="Medium",
        motivation="Viral products, influencer recommendations, limited drops",
        objections=["Buyer's remorse", "Waiting for payday or sale events"],
        personas=[
            {"name": "Aarav D.", "age": 22, "title": "College Student (Engineering)", "locality": "Gachibowli", "quote": "If my favorite creator recommends it, I'll buy it before the link expires."},
        ],
    ),
    DomainSegmentTemplate(
        id="practical_buyers",
        name="Practical Need-Based Purchasers",
        label="Practical Buyers",
        age_band="35-55",
        spend_band="value",
        channel="Marketplace & Local Retail",
        frequency=1.0,
        sensitivity="High",
        motivation="Functional replacement purchases, durability over aesthetics",
        objections=["Price premium without practical justification", "Online-only availability"],
        personas=[
            {"name": "Lakshmi P.", "age": 48, "title": "Government Employee", "locality": "Dilsukhnagar", "quote": "I only buy when my current one wears out. It needs to last at least 2 years."},
        ],
    ),
]

SAAS_SEGMENTS: List[DomainSegmentTemplate] = [
    DomainSegmentTemplate(
        id="tech_early_adopters",
        name="Tech Early Adopters & Power Users",
        label="Early Adopters",
        age_band="25-35",
        spend_band="upper_middle",
        channel="Product Hunt & Developer Communities",
        frequency=1.0,  # monthly subscription
        sensitivity="Low",
        motivation="Cutting-edge tools, productivity gains, competitive advantage",
        objections=["Vendor lock-in concerns", "Missing integrations with existing stack"],
        personas=[
            {"name": "Arjun M.", "age": 28, "title": "Staff Engineer", "locality": "Gachibowli", "quote": "I'll pay for any tool that saves me 2+ hours per week of repetitive work."},
            {"name": "Sarah L.", "age": 31, "title": "DevOps Lead", "locality": "HITEC City", "quote": "I need to see clear ROI in a 14-day trial before I can pitch this to my manager."},
        ],
    ),
    DomainSegmentTemplate(
        id="smb_decision_makers",
        name="SMB Decision Makers",
        label="SMB Leaders",
        age_band="30-45",
        spend_band="upper",
        channel="Sales Demo & LinkedIn",
        frequency=1.0,
        sensitivity="Medium",
        motivation="Team efficiency, compliance, cost reduction",
        objections=["Budget approval process", "Change management overhead"],
        personas=[
            {"name": "Deepak R.", "age": 38, "title": "CTO, Series A Startup", "locality": "Financial District", "quote": "We need something that works out of the box — no time for 6-month implementations."},
        ],
    ),
    DomainSegmentTemplate(
        id="enterprise_evaluators",
        name="Enterprise Evaluators",
        label="Enterprise",
        age_band="35-50",
        spend_band="upper",
        channel="Enterprise Sales & RFP",
        frequency=1.0,
        sensitivity="Low",
        motivation="Security, compliance, scale, SLAs, vendor reputation",
        objections=["SOC2/ISO compliance requirements", "Custom SSO/SAML needs", "Long procurement cycles"],
        personas=[
            {"name": "Meera S.", "age": 44, "title": "VP IT, Banking Corp", "locality": "Banjara Hills", "quote": "We can't consider any vendor without SOC2 Type II and on-premise deployment option."},
        ],
    ),
    DomainSegmentTemplate(
        id="freelancers_solopreneurs",
        name="Freelancers & Solopreneurs",
        label="Freelancers",
        age_band="22-35",
        spend_band="value",
        channel="Free Tier & Word of Mouth",
        frequency=1.0,
        sensitivity="High",
        motivation="Free/cheap tools that make them look professional",
        objections=["Can't justify subscription on thin margins", "Using free alternatives"],
        personas=[
            {"name": "Nisha T.", "age": 27, "title": "Freelance Designer", "locality": "Kondapur", "quote": "I love the product but $20/month cuts into my freelance margins significantly."},
        ],
    ),
    DomainSegmentTemplate(
        id="churned_competitors",
        name="Competitor Switchers",
        label="Switchers",
        age_band="28-40",
        spend_band="upper_middle",
        channel="Review Sites & Comparison Pages",
        frequency=1.0,
        sensitivity="Medium",
        motivation="Better UX, lower price, missing feature in current tool",
        objections=["Data migration complexity", "Team retraining effort"],
        personas=[
            {"name": "Karthik V.", "age": 33, "title": "Operations Manager", "locality": "Madhapur", "quote": "Our current tool is bloated and expensive. Looking for something simpler and faster."},
        ],
    ),
]

RESTAURANT_SEGMENTS: List[DomainSegmentTemplate] = [
    DomainSegmentTemplate(
        id="foodie_explorers",
        name="Foodie Explorers & Reviewers",
        label="Foodies",
        age_band="22-35",
        spend_band="upper_middle",
        channel="Instagram & Zomato/Swiggy",
        frequency=4.0,
        sensitivity="Medium",
        motivation="New cuisines, Instagrammable presentation, unique dining experiences",
        objections=["Inconsistent quality across visits", "Long wait times"],
        personas=[
            {"name": "Aisha M.", "age": 27, "title": "Content Creator", "locality": "Jubilee Hills", "quote": "I need dishes that taste amazing AND photograph well for my food blog."},
        ],
    ),
    DomainSegmentTemplate(
        id="family_diners",
        name="Family & Group Diners",
        label="Family Diners",
        age_band="30-50",
        spend_band="upper_middle",
        channel="Word of Mouth & Google Maps",
        frequency=2.0,
        sensitivity="Medium",
        motivation="Kid-friendly, reliable quality, large portions, weekend outings",
        objections=["Limited kids menu", "Noise levels", "Parking availability"],
        personas=[
            {"name": "Rajesh K.", "age": 40, "title": "Bank Manager", "locality": "Kukatpally", "quote": "Need a place where my kids enjoy the food and we don't have to wait 45 minutes."},
        ],
    ),
    DomainSegmentTemplate(
        id="office_lunch_crowd",
        name="Office Lunch Regulars",
        label="Office Crowd",
        age_band="24-40",
        spend_band="middle",
        channel="Delivery Apps & Walk-in",
        frequency=8.0,
        sensitivity="High",
        motivation="Quick, reliable lunch within budget, close to workplace",
        objections=["Delivery fees eating into budget", "Slow service during peak hours"],
        personas=[
            {"name": "Shreya V.", "age": 29, "title": "Data Analyst", "locality": "HITEC City", "quote": "I order lunch from the same 3 places every week. Speed and consistency matter most."},
        ],
    ),
    DomainSegmentTemplate(
        id="health_conscious",
        name="Health-Conscious Diners",
        label="Health Focus",
        age_band="25-40",
        spend_band="upper",
        channel="Health Apps & Organic Channels",
        frequency=5.0,
        sensitivity="Low",
        motivation="Calorie tracking, organic ingredients, clean eating, dietary restrictions",
        objections=["Limited healthy options on menu", "Calorie info not displayed"],
        personas=[
            {"name": "Ananya P.", "age": 32, "title": "Fitness Coach", "locality": "Madhapur", "quote": "I need exact calorie counts and prefer restaurants that source organic produce."},
        ],
    ),
    DomainSegmentTemplate(
        id="occasional_celebrators",
        name="Occasion & Celebration Diners",
        label="Celebrators",
        age_band="25-55",
        spend_band="upper",
        channel="Google Reviews & Social Recommendations",
        frequency=0.5,
        sensitivity="Low",
        motivation="Special occasions, ambiance, group bookings, impressive setting",
        objections=["High price for special menu items", "Reservation availability"],
        personas=[
            {"name": "Sunil G.", "age": 45, "title": "Real Estate Developer", "locality": "Banjara Hills", "quote": "When I'm hosting clients or celebrating, I need a place that impresses without trying too hard."},
        ],
    ),
]

HEALTHCARE_SEGMENTS: List[DomainSegmentTemplate] = [
    DomainSegmentTemplate(
        id="chronic_patients",
        name="Chronic Condition Patients",
        label="Chronic Care",
        age_band="35-65",
        spend_band="upper_middle",
        channel="Doctor Referral & Insurance",
        frequency=2.0,
        sensitivity="Low",
        motivation="Reliable ongoing care, medication management, specialist access",
        objections=["Long appointment wait times", "Insurance coverage gaps"],
        personas=[
            {"name": "Ramesh T.", "age": 52, "title": "Retired Professor", "locality": "Secunderabad", "quote": "I need a doctor who understands my diabetes history and adjusts medications carefully."},
        ],
    ),
    DomainSegmentTemplate(
        id="young_professionals",
        name="Young Health-Conscious Professionals",
        label="Young Professionals",
        age_band="22-35",
        spend_band="upper_middle",
        channel="Health Apps & Google Search",
        frequency=1.0,
        sensitivity="Medium",
        motivation="Preventive health, annual checkups, convenience, digital-first",
        objections=["Prefer telemedicine over clinic visits", "Cost of preventive care"],
        personas=[
            {"name": "Kavya S.", "age": 28, "title": "Software Engineer", "locality": "Gachibowli", "quote": "I want to book a health checkup online and get results on my phone, not wait in a queue."},
        ],
    ),
    DomainSegmentTemplate(
        id="parents",
        name="Parents Seeking Pediatric Care",
        label="Parents",
        age_band="28-42",
        spend_band="upper",
        channel="Parent Groups & Doctor Reviews",
        frequency=3.0,
        sensitivity="Low",
        motivation="Trusted pediatric care, vaccinations, quick access during emergencies",
        objections=["Limited weekend/evening hours", "Clinic cleanliness concerns"],
        personas=[
            {"name": "Priti M.", "age": 34, "title": "HR Manager", "locality": "Kondapur", "quote": "When my toddler is sick at 10pm, I need a doctor who responds, not an appointment system."},
        ],
    ),
    DomainSegmentTemplate(
        id="elderly_patients",
        name="Elderly Care & Home Visit Patients",
        label="Elderly Care",
        age_band="55-80",
        spend_band="middle",
        channel="Family Referral & Local Reputation",
        frequency=2.0,
        sensitivity="Medium",
        motivation="Home visits, gentle care, medication delivery, family updates",
        objections=["Technology barriers for booking", "Mobility limitations"],
        personas=[
            {"name": "Sunita D.", "age": 68, "title": "Retired Teacher", "locality": "Ameerpet", "quote": "I wish the doctor could visit me at home. Going to the clinic is exhausting."},
        ],
    ),
    DomainSegmentTemplate(
        id="insurance_patients",
        name="Insurance-Covered Patients",
        label="Insurance Patients",
        age_band="30-55",
        spend_band="upper_middle",
        channel="Insurance Network & HR Benefits",
        frequency=1.5,
        sensitivity="High",
        motivation="Maximize insurance coverage, cashless treatment, empanelled hospitals",
        objections=["Network restrictions", "Claim processing delays"],
        personas=[
            {"name": "Ajay R.", "age": 38, "title": "Corporate Manager", "locality": "Financial District", "quote": "I'll only visit clinics that accept my corporate insurance for cashless billing."},
        ],
    ),
]

EDUCATION_SEGMENTS: List[DomainSegmentTemplate] = [
    DomainSegmentTemplate(
        id="career_changers",
        name="Career Changers & Upskill Seekers",
        label="Career Changers",
        age_band="25-38",
        spend_band="upper_middle",
        channel="LinkedIn & Course Platforms",
        frequency=1.0,
        sensitivity="Medium",
        motivation="Career pivot, salary upgrade, industry-recognized certification",
        objections=["ROI uncertainty", "Time commitment alongside job"],
        personas=[
            {"name": "Mohit J.", "age": 30, "title": "Mechanical Engineer (pivoting to Data Science)", "locality": "Gachibowli", "quote": "I need a program with placement guarantee. Can't afford to invest ₹1.5L without job assurance."},
        ],
    ),
    DomainSegmentTemplate(
        id="college_students",
        name="College Students (Competitive Edge)",
        label="Students",
        age_band="18-24",
        spend_band="value",
        channel="College Networks & YouTube",
        frequency=1.0,
        sensitivity="High",
        motivation="Competitive edge, internship prep, peer pressure",
        objections=["Affordability", "Free alternatives on YouTube"],
        personas=[
            {"name": "Sneha K.", "age": 21, "title": "B.Tech Student (3rd year)", "locality": "HITEC City", "quote": "All my friends are doing certifications. I need one too, but my budget is really tight."},
        ],
    ),
    DomainSegmentTemplate(
        id="corporate_learners",
        name="Corporate L&D Sponsored Learners",
        label="Corporate L&D",
        age_band="28-45",
        spend_band="upper",
        channel="Enterprise Sales & HR Departments",
        frequency=1.0,
        sensitivity="Low",
        motivation="Company-sponsored skill development, compliance training",
        objections=["Content relevance to specific role", "Certification validity"],
        personas=[
            {"name": "Anand P.", "age": 36, "title": "L&D Head, IT Services", "locality": "Financial District", "quote": "We need to train 200 engineers on cloud in 3 months. Need enterprise pricing and tracking."},
        ],
    ),
    DomainSegmentTemplate(
        id="parents_k12",
        name="Parents (K-12 Enrichment)",
        label="K-12 Parents",
        age_band="30-45",
        spend_band="upper_middle",
        channel="Parent WhatsApp Groups & School Referrals",
        frequency=1.0,
        sensitivity="Medium",
        motivation="Child's academic excellence, competitive exam prep, holistic development",
        objections=["Screen time concerns", "Already too many extracurriculars"],
        personas=[
            {"name": "Kavitha R.", "age": 38, "title": "Doctor", "locality": "Jubilee Hills", "quote": "My son needs coding classes, but I don't want him staring at screens for another 2 hours."},
        ],
    ),
    DomainSegmentTemplate(
        id="hobby_learners",
        name="Lifelong & Hobby Learners",
        label="Hobby Learners",
        age_band="25-60",
        spend_band="middle",
        channel="Social Media & Community Forums",
        frequency=1.0,
        sensitivity="Medium",
        motivation="Personal enrichment, creative expression, social connection",
        objections=["Low urgency", "Competing with free content"],
        personas=[
            {"name": "Pradeep N.", "age": 50, "title": "Bank Officer", "locality": "Secunderabad", "quote": "I've always wanted to learn photography properly, not just YouTube tutorials."},
        ],
    ),
]

# Generic segments for unknown domains
GENERIC_SEGMENTS: List[DomainSegmentTemplate] = [
    DomainSegmentTemplate(
        id="early_adopters",
        name="Early Adopters & Enthusiasts",
        label="Early Adopters",
        age_band="22-35",
        spend_band="upper_middle",
        channel="Social Media & Direct Search",
        frequency=2.0,
        sensitivity="Low",
        motivation="Innovation, being first, social status from discovery",
        objections=["Product maturity concerns", "Limited social proof"],
        personas=[
            {"name": "Rahul T.", "age": 28, "title": "Product Manager", "locality": "Gachibowli", "quote": "I love discovering new brands before they go mainstream."},
        ],
    ),
    DomainSegmentTemplate(
        id="mainstream_consumers",
        name="Mainstream Consumers",
        label="Mainstream",
        age_band="25-45",
        spend_band="middle",
        channel="Google Search & Word of Mouth",
        frequency=1.5,
        sensitivity="Medium",
        motivation="Reliable quality, good reviews, reasonable price",
        objections=["No compelling reason to switch from current provider"],
        personas=[
            {"name": "Divya S.", "age": 34, "title": "Teacher", "locality": "Madhapur", "quote": "I go with whatever has good reviews and reasonable pricing."},
        ],
    ),
    DomainSegmentTemplate(
        id="premium_segment",
        name="Premium & Quality-Focused Customers",
        label="Premium",
        age_band="30-55",
        spend_band="upper",
        channel="Referrals & Premium Channels",
        frequency=1.0,
        sensitivity="Low",
        motivation="Superior quality, exclusive experience, prestige",
        objections=["Need to see clear value over alternatives"],
        personas=[
            {"name": "Arun K.", "age": 45, "title": "Director, IT", "locality": "Banjara Hills", "quote": "I'm willing to pay more for something that genuinely works better."},
        ],
    ),
    DomainSegmentTemplate(
        id="price_conscious",
        name="Price-Conscious Value Seekers",
        label="Value Seekers",
        age_band="20-50",
        spend_band="value",
        channel="Price Comparison & Deals",
        frequency=1.0,
        sensitivity="High",
        motivation="Lowest price, maximum value, deals and discounts",
        objections=["Any premium pricing is a dealbreaker"],
        personas=[
            {"name": "Suresh B.", "age": 42, "title": "Accountant", "locality": "Kukatpally", "quote": "Why would I pay more when there are cheaper alternatives available?"},
        ],
    ),
    DomainSegmentTemplate(
        id="loyal_repeaters",
        name="Loyal Repeat Customers",
        label="Loyalists",
        age_band="28-50",
        spend_band="upper_middle",
        channel="Direct & Referral",
        frequency=3.0,
        sensitivity="Low",
        motivation="Consistency, familiarity, trust, accumulated benefits",
        objections=["Would leave only if quality drops significantly"],
        personas=[
            {"name": "Padma L.", "age": 38, "title": "Marketing Lead", "locality": "Kondapur", "quote": "I've been a customer for 2 years. The consistent experience keeps me coming back."},
        ],
    ),
]

# Map domain IDs to segment templates
DOMAIN_SEGMENTS: Dict[str, List[DomainSegmentTemplate]] = {
    "ecommerce": ECOMMERCE_SEGMENTS,
    "technology": SAAS_SEGMENTS,
    "food_beverage": RESTAURANT_SEGMENTS,
    "healthcare": HEALTHCARE_SEGMENTS,
    "education": EDUCATION_SEGMENTS,
}

# Default locality weights (Hyderabad)
DEFAULT_LOCALITY_WEIGHTS: Dict[str, float] = {
    "Gachibowli": 0.22,
    "Madhapur": 0.18,
    "Kondapur": 0.14,
    "HITEC City": 0.12,
    "Financial District": 0.10,
    "Banjara Hills": 0.06,
    "Jubilee Hills": 0.05,
    "Kukatpally": 0.05,
    "Secunderabad": 0.04,
    "Manikonda": 0.02,
    "Ameerpet": 0.02,
}


class DynamicPopulationGenerator:
    """Generates 500 synthetic participants based on detected domain."""
    
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
    
    def generate(
        self,
        domain: str,
        sub_domain: str = "",
        venture_price: float = 1000.0,
        market_median_price: float = 800.0,
        marketing_budget: float = 150000.0,
    ) -> Dict[str, Any]:
        """Generate 500 calibrated participants for the given domain."""
        rng = random.Random(self.random_seed)
        segments = DOMAIN_SEGMENTS.get(domain, GENERIC_SEGMENTS)
        
        # Distribute 500 participants across segments
        n_segments = len(segments)
        # Weighted distribution: first segments get more weight
        base_weights = [0.30, 0.25, 0.20, 0.15, 0.10][:n_segments]
        # Normalize
        total_w = sum(base_weights)
        segment_sizes = []
        remaining = 500
        for i, w in enumerate(base_weights):
            if i == n_segments - 1:
                segment_sizes.append(remaining)
            else:
                size = round(500 * (w / total_w))
                segment_sizes.append(size)
                remaining -= size
        
        localities = list(DEFAULT_LOCALITY_WEIGHTS.keys())
        loc_weights = list(DEFAULT_LOCALITY_WEIGHTS.values())
        
        all_participants = []
        segment_results = []
        participant_idx = 0
        
        for seg_idx, segment_template in enumerate(segments):
            seg_size = segment_sizes[seg_idx] if seg_idx < len(segment_sizes) else 0
            seg_participants = []
            
            spend_band = segment_template.spend_band
            age_band = segment_template.age_band
            channel = segment_template.channel
            base_freq = segment_template.frequency
            
            for _ in range(seg_size):
                participant_idx += 1
                locality = rng.choices(localities, weights=loc_weights, k=1)[0]
                
                # Generate calibrated attributes
                cat_affinity = min(0.98, max(0.15, rng.gauss(
                    0.70 if spend_band != "value" else 0.35, 0.15
                )))
                price_sens = min(0.98, max(0.10, rng.gauss(
                    0.30 if spend_band == "upper" else
                    (0.45 if spend_band == "upper_middle" else
                     (0.60 if spend_band == "middle" else 0.80)),
                    0.14
                )))
                brand_aff = min(0.95, max(0.20, rng.gauss(
                    0.70 if spend_band in ("upper", "upper_middle") else 0.40, 0.16
                )))
                purch_freq = max(0.5, rng.gauss(base_freq, 0.6))
                
                # Behavior evaluation
                price_ratio = venture_price / max(market_median_price, 1.0)
                
                # Awareness
                geo_mult = 1.12 if locality in ("Gachibowli", "Madhapur", "HITEC City") else 0.92
                p_awareness = min(0.95, 0.78 * geo_mult)
                
                # Interest
                p_interest = min(0.92, cat_affinity * 1.05)
                
                # Consideration
                p_consideration = min(0.88, brand_aff * 0.95)
                
                # Intent (price-dependent)
                if price_ratio > 1.2:
                    price_resistance = (price_ratio - 1.0) * price_sens
                    p_intent = max(0.05, min(0.85, 0.80 - price_resistance * 0.65))
                else:
                    p_intent = min(0.90, 0.80 + (1.0 - price_ratio) * 0.3)
                
                # Purchase
                p_purchase = min(0.85, p_intent * 0.88)
                
                # Repeat
                p_repeat = 0.65 if spend_band in ("upper", "upper_middle") else 0.40
                
                # Stage-gate progression
                roll_a, roll_i, roll_c, roll_n, roll_p = (
                    rng.random(), rng.random(), rng.random(), rng.random(), rng.random()
                )
                
                converted = False
                drop_stage = None
                drop_reason = None
                
                if roll_a > p_awareness:
                    drop_stage = "awareness"
                    drop_reason = "Unreached by marketing impressions in this geographic area"
                elif roll_i > p_interest:
                    drop_stage = "interest"
                    drop_reason = "Low immediate category relevance or need"
                elif roll_c > p_consideration:
                    drop_stage = "consideration"
                    drop_reason = "Strong preference for existing provider or competitor"
                elif roll_n > p_intent:
                    drop_stage = "intent"
                    drop_reason = f"Price resistance (venture vs market median)"
                elif roll_p > p_purchase:
                    drop_stage = "purchase"
                    drop_reason = "Checkout hesitation or friction"
                else:
                    converted = True
                
                participant = {
                    "id": f"syn_{participant_idx:03d}",
                    "segment_id": segment_template.id,
                    "age_band": age_band,
                    "locality": locality,
                    "spending_band": spend_band,
                    "category_affinity": round(cat_affinity, 2),
                    "price_sensitivity": round(price_sens, 2),
                    "brand_affinity": round(brand_aff, 2),
                    "purchase_frequency": round(purch_freq, 1),
                    "channel_preference": channel,
                    "converted": converted,
                    "drop_stage": drop_stage,
                    "drop_reason": drop_reason,
                }
                seg_participants.append(participant)
                all_participants.append(participant)
            
            # Compute segment stats
            converts = sum(1 for p in seg_participants if p["converted"])
            count = len(seg_participants)
            avg_sens = round(sum(p["price_sensitivity"] for p in seg_participants) / max(count, 1), 2)
            
            why_buy = segment_template.why_they_buy or [
                segment_template.motivation,
                f"Preference for ordering via {segment_template.channel}",
            ]
            why_dont = segment_template.why_they_dont_buy or segment_template.objections or [
                f"Price sensitivity resistance ({segment_template.sensitivity}) vs budget",
                "Hesitation switching from entrenched category incumbents",
            ]
            what_change = segment_template.what_would_change_decision or [
                "Targeted intro discount or low-risk entry trial",
                "Evidence of superior reliability or quality guarantees",
            ]

            segment_results.append({
                "id": segment_template.id,
                "name": segment_template.name,
                "label": segment_template.label,
                "population": count,
                "population_pct": round((count / 500) * 100, 1),
                "simulated_conversions": converts,
                "conversion_rate_pct": round((converts / max(count, 1)) * 100, 1),
                "price_sensitivity": segment_template.sensitivity,
                "avg_price_sensitivity_score": avg_sens,
                "motivation": segment_template.motivation,
                "preferred_channel": segment_template.channel,
                "objections": segment_template.objections,
                "representative_personas": segment_template.personas,
                "why_they_buy": why_buy,
                "why_they_dont_buy": why_dont,
                "what_would_change_decision": what_change,
            })
        
        # Compute funnel
        total = len(all_participants)
        aware = sum(1 for p in all_participants if p["drop_stage"] != "awareness")
        interest = sum(1 for p in all_participants if p["drop_stage"] not in ("awareness", "interest"))
        consideration = sum(1 for p in all_participants if p["drop_stage"] not in ("awareness", "interest", "consideration"))
        intent = sum(1 for p in all_participants if p["drop_stage"] not in ("awareness", "interest", "consideration", "intent"))
        purchase = sum(1 for p in all_participants if p["converted"])
        repeat = round(purchase * 0.55)
        
        drop_reasons: Dict[str, int] = {}
        for p in all_participants:
            if p["drop_reason"]:
                drop_reasons[p["drop_reason"]] = drop_reasons.get(p["drop_reason"], 0) + 1
        top_dropouts = sorted(
            [{"reason": r, "count": c, "pct": round((c / total) * 100, 1)} for r, c in drop_reasons.items()],
            key=lambda x: x["count"],
            reverse=True,
        )
        
        funnel = {
            "total_cohort": total,
            "stages": [
                {"stage": "Total Synthetic Cohort", "count": total, "conversion_pct": 100.0, "drop": 0},
                {"stage": "Brand Awareness", "count": aware, "conversion_pct": round((aware / total) * 100, 1), "drop": total - aware},
                {"stage": "Category Interest", "count": interest, "conversion_pct": round((interest / total) * 100, 1), "drop": aware - interest},
                {"stage": "Product Consideration", "count": consideration, "conversion_pct": round((consideration / total) * 100, 1), "drop": interest - consideration},
                {"stage": "Purchase Intent", "count": intent, "conversion_pct": round((intent / total) * 100, 1), "drop": consideration - intent},
                {"stage": "Simulated Purchase", "count": purchase, "conversion_pct": round((purchase / total) * 100, 1), "drop": intent - purchase},
                {"stage": "Repeat Retention (180d)", "count": repeat, "conversion_pct": round((repeat / total) * 100, 1), "drop": purchase - repeat},
            ],
            "final_simulated_customers": purchase,
            "cohort_conversion_rate": round((purchase / total) * 100, 1),
            "primary_dropout_reasons": top_dropouts[:4],
        }
        
        # Geographic distribution
        geo_counts: Dict[str, Dict[str, int]] = {}
        for p in all_participants:
            loc = p["locality"]
            if loc not in geo_counts:
                geo_counts[loc] = {"total": 0, "converted": 0}
            geo_counts[loc]["total"] += 1
            if p["converted"]:
                geo_counts[loc]["converted"] += 1
        
        geo_dist = []
        for loc, data in geo_counts.items():
            tot = data["total"]
            conv = data["converted"]
            geo_dist.append({
                "locality": loc,
                "participant_count": tot,
                "participant_pct": round((tot / total) * 100, 1),
                "converted_customers": conv,
                "conversion_rate_pct": round((conv / max(tot, 1)) * 100, 1),
            })
        geo_dist.sort(key=lambda x: x["participant_count"], reverse=True)
        
        # Acquisition model (simplified)
        channels = [
            {"channel": "Paid Social (Meta & Instagram)", "budget_share": 0.40, "cpc": 20.0, "intent": 0.030},
            {"channel": "Paid Search (Google)", "budget_share": 0.30, "cpc": 30.0, "intent": 0.050},
            {"channel": "Content & Influencer Marketing", "budget_share": 0.20, "cpc": 25.0, "intent": 0.025},
            {"channel": "Organic & Word of Mouth", "budget_share": 0.10, "cpc": 0.0, "intent": 0.080},
        ]
        
        total_acquired = 0
        channel_breakdown = []
        for ch in channels:
            spend = marketing_budget * ch["budget_share"]
            visits = int(spend / ch["cpc"]) if ch["cpc"] > 0 else int(marketing_budget * 0.10 / 12.0)
            conversions = int(visits * ch["intent"])
            total_acquired += conversions
            channel_cac = round(spend / max(conversions, 1), 1) if spend > 0 else 0.0
            channel_breakdown.append({
                "channel": ch["channel"],
                "spend": round(spend, 0),
                "visits": visits,
                "simulated_conversions": conversions,
                "derived_cac": channel_cac,
            })
        
        derived_cac = round(marketing_budget / max(total_acquired, 1), 1)
        
        acquisition_model = {
            "monthly_marketing_budget": marketing_budget,
            "modeled_total_reach_visits": sum(ch["visits"] for ch in channel_breakdown),
            "modeled_monthly_acquired_customers": total_acquired,
            "derived_blended_cac": derived_cac,
            "channel_breakdown": channel_breakdown,
        }
        
        return {
            "domain": domain,
            "sub_domain": sub_domain,
            "total_synthetic_cohort": 500,
            "participants_sample": all_participants[:15],
            "funnel": funnel,
            "segments": segment_results,
            "geographic_distribution": geo_dist,
            "acquisition_model": acquisition_model,
            "methodology": {
                "population_model": f"Calibrated demographic distribution for {domain} domain",
                "evidence_classification": "Modeled Synthetic Micro-Population",
                "random_seed": self.random_seed,
                "domain_specific": domain in DOMAIN_SEGMENTS,
            },
        }
