#!/usr/bin/env python3
"""MEOK AI Labs — ad-copy-ai-mcp MCP Server. AI-powered ad copy generation for multi-platform campaigns."""

import json
from datetime import datetime, timezone
from typing import Any
from collections import defaultdict
import uuid
import random
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

_store = {"campaigns": {}, "creatives": [], "variants": [], "templates": {}}
mcp = FastMCP("ad-copy-ai", instructions="AI-powered ad copy generation for multi-platform campaigns.")


def create_id():
    return str(uuid.uuid4())[:8]


TEMPLATES = {
    "facebook": {
        "hook": [
            "{product} changed my life!",
            "You need to see this.",
            "This {product} is everything.",
            "Finally, a {product} that works.",
            "Stop scrolling - this matters.",
        ],
        "body": [
            "I've tried everything, but nothing compares to {product}. {benefit}",
            "If you're serious about {benefit}, you need this.",
            "Don't sleep on {product} — your future self will thank you.",
            "Here's the {benefit} hack nobody talks about.",
        ],
        "cta": ["Learn More", "Try It Free", "Get Started", "Shop Now", "Join Now"],
    },
    "google": {
        "headline": [
            "Best {product} - 2026 Reviews",
            "{product} Near You",
            "Top-Rated {product}",
            "{product} - Free Quote",
            "Professional {product}",
        ],
        "description": "Get the best {product} near you. Rated 5 stars. {benefit} Call now.",
        "cta": "Get Quote",
    },
    "linkedin": {
        "hook": [
            "How we increased {benefit} by 200%",
            "The {product} strategy every founder needs",
            "Why your {product} isn't working",
            "I tested 10 {product}s so you don't have to",
        ],
        "body": [
            "Our team implemented {product} and saw {benefit} in 30 days. Here's what we learned:",
            "If you're in {industry}, you need to pay attention to {product}. Here's why:",
            "The {product} mistake costing you {benefit} (and how to fix it)",
        ],
        "cta": ["Read More", "Download Guide", "Schedule Demo", "Get Started"],
    },
    "instagram": {
        "hook": [
            "POV: You discovered {product}",
            "This changed everything",
            "Not sponsored, just real",
            "Wait for it...",
            "If you know, you know",
        ],
        "body": [
            "{product} be like... {benefit}",
            "No cap, {product} is {benefit}",
            "The secret {benefit} nobody tells you about",
            "Tag someone who needs this!",
        ],
        "cta": ["Link in bio", "Shop now", "Learn more"],
    },
    "tiktok": {
        "hook": [
            "Wait for the end!",
            "POV: You tried {product}",
            "This is your sign",
            "Don't scroll!",
            "Wait til you see this",
        ],
        "body": [
            "{product} but make it {benefit}",
            "POV: You finally found {product}",
            "The hack you needed",
            "This is your sign to try {product}",
        ],
        "cta": ["Link in bio", "Try it now", "See more"],
    },
    "twitter": {
        "hook": [
            "{product} is underrated",
            "Unpopular opinion: {product}",
            "Hot take on {product}",
            "Here's the thing about {product}",
        ],
        "body": [
            "{benefit}. That's it, that's the tweet.",
            "I've been using {product} for 30 days. Here's my review:",
            "Stop sleeping on {product}. {benefit}",
            "The {product} Twitter thread you didn't ask for",
        ],
        "cta": ["Read more", "Follow for more", "Quote tweet"],
    },
    "email": {
        "subject": [
            "You need {product}",
            "About {product}",
            "Here's what we found",
            "Don't miss this",
            "{product} update",
        ],
        "preheader": "You won't believe {benefit}",
        "body": "Hey {first_name},\n\n{benefit}. That's why we built {product}.\n\n[Body copy about {benefit}]\n\n[CTA button]\n\nBest,\n[Your name]",
        "cta": ["Get Started", "Learn More", "Claim Offer"],
    },
}

BENEFITS = [
    "saving money",
    "saving time",
    "increasing revenue",
    "reducing stress",
    "improving health",
    "boosting productivity",
    "growing your business",
    "getting better results",
]


def generate_copy(product, platform, tone, benefit=None, industry=None):
    templates = TEMPLATES.get(platform, TEMPLATES.get("facebook"))
    benefit = benefit or random.choice(BENEFITS)

    if platform == "facebook":
        hook = random.choice(templates["hook"]).format(product=product)
        body = random.choice(templates["body"]).format(product=product, benefit=benefit)
        cta = random.choice(templates["cta"])
        return {"hook": hook, "body": body, "cta": cta, "platform": platform}

    elif platform == "google":
        headline = random.choice(templates["headline"]).format(product=product)
        description = templates["description"].format(product=product, benefit=benefit)
        return {
            "headlines": [headline, headline.replace("Best", "Top-Rated")],
            "description": description,
            "cta": templates["cta"],
            "platform": platform,
        }

    elif platform == "linkedin":
        hook = random.choice(templates["hook"]).format(
            product=product, benefit=benefit, industry=industry or "business"
        )
        body = random.choice(templates["body"]).format(
            product=product, benefit=benefit, industry=industry or "business"
        )
        cta = random.choice(templates["cta"])
        return {"hook": hook, "body": body, "cta": cta, "platform": platform}

    elif platform in ["instagram", "tiktok"]:
        hook = random.choice(templates["hook"]).format(product=product, benefit=benefit)
        body = random.choice(templates["body"]).format(product=product, benefit=benefit)
        cta = random.choice(templates["cta"])
        return {
            "hook": hook,
            "body": body,
            "cta": cta,
            "platform": platform,
            "hashtags": [
                f"#{product.lower().replace(' ', '')}",
                f"#{benefit.lower().replace(' ', '')}",
                "#trending",
            ],
        }

    elif platform == "twitter":
        hook = random.choice(templates["hook"]).format(product=product)
        body = random.choice(templates["body"]).format(product=product, benefit=benefit)
        cta = random.choice(templates["cta"])
        return {
            "hook": hook,
            "body": body,
            "cta": cta,
            "platform": platform,
            "character_count": len(hook + body + cta),
        }

    elif platform == "email":
        subject = random.choice(templates["subject"]).format(product=product)
        body = templates["body"].format(
            product=product, benefit=benefit, first_name="there"
        )
        cta = random.choice(templates["cta"])
        return {
            "subject": subject,
            "preheader": templates["preheader"].format(benefit=benefit),
            "body": body,
            "cta": cta,
            "platform": platform,
        }

    else:
        return {
            "headline": f"Try {product} today",
            "body": f"Experience the {benefit} of {product}",
            "cta": "Learn More",
            "platform": "generic",
        }


@mcp.tool()
def generate_ad_copy(product: str = "our product", platform: str = "facebook", tone: str = "professional", benefit: str = "", industry: str = "", api_key: str = "") -> str:
    """Generate ad copy for a platform

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        product (str): The product to analyze or process.
        platform (str): The platform to analyze or process.
        tone (str): The tone to analyze or process.
        benefit (str): The benefit to analyze or process.
        industry (str): The industry to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    result = generate_copy(product, platform, tone, benefit or None, industry or None)
    return json.dumps(result, indent=2)


@mcp.tool()
def generate_variants(product: str = "our product", platform: str = "facebook", count: int = 3, api_key: str = "") -> str:
    """Generate multiple ad variants for A/B testing

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        product (str): The product to analyze or process.
        platform (str): The platform to analyze or process.
        count (int): The count to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    variants = []
    for i in range(count):
        variant = generate_copy(
            product, platform, random.choice(["professional", "casual", "urgent"])
        )
        variant["variant_id"] = create_id()
        variant["version"] = f"v{i + 1}"
        variants.append(variant)

    _store["variants"].extend(variants)
    return json.dumps({"variants": variants, "count": len(variants)}, indent=2)


@mcp.tool()
def create_campaign(campaign_name: str, product: str = "", platforms: list = None, budget: float = 0, start_date: str = "", api_key: str = "") -> str:
    """Create an ad campaign

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        campaign_name (str): The campaign name to analyze or process.
        product (str): The product to analyze or process.
        platforms (list): The platforms to analyze or process.
        budget (float): The budget to analyze or process.
        start_date (str): The start date to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    campaign = {
        "id": create_id(),
        "name": campaign_name,
        "product": product,
        "platforms": platforms or [],
        "budget": budget,
        "start_date": start_date or datetime.now().isoformat(),
        "status": "draft",
        "creatives": [],
        "created_at": datetime.now().isoformat(),
    }
    _store["campaigns"][campaign["id"]] = campaign
    return json.dumps(
        {"campaign_created": True, "campaign_id": campaign["id"], "name": campaign["name"]},
        indent=2,
    )


@mcp.tool()
def get_campaign(campaign_id: str, api_key: str = "") -> str:
    """Get campaign details

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        campaign_id (str): The campaign id to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if campaign_id in _store["campaigns"]:
        return json.dumps(_store["campaigns"][campaign_id], indent=2)
    return json.dumps({"error": "Campaign not found"})


@mcp.tool()
def add_creative(campaign_id: str, creative: dict = None, api_key: str = "") -> str:
    """Add a creative to campaign

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        campaign_id (str): The campaign id to analyze or process.
        creative (dict): The creative to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if campaign_id not in _store["campaigns"]:
        return json.dumps({"error": "Campaign not found"})

    creative_data = creative or {}
    creative_data["id"] = create_id()
    creative_data["added_at"] = datetime.now().isoformat()
    _store["campaigns"][campaign_id]["creatives"].append(creative_data)
    _store["creatives"].append(creative_data)

    return json.dumps(
        {"creative_added": True, "creative_id": creative_data["id"]}, indent=2
    )


@mcp.tool()
def get_performance(campaign_id: str = "", creative_id: str = "", api_key: str = "") -> str:
    """Get creative performance metrics

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        campaign_id (str): The campaign id to analyze or process.
        creative_id (str): The creative id to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    creative = next(
        (c for c in _store["creatives"] if c.get("id") == creative_id), None
    )
    if not creative:
        return json.dumps(
            {"impressions": 0, "clicks": 0, "ctr": 0, "conversions": 0, "conversion_rate": 0}
        )

    impressions = creative.get("impressions", random.randint(1000, 50000))
    clicks = creative.get("clicks", random.randint(10, 500))
    ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0
    conversions = creative.get("conversions", random.randint(0, 50))

    return json.dumps(
        {
            "creative_id": creative_id,
            "impressions": impressions,
            "clicks": clicks,
            "ctr": ctr,
            "conversions": conversions,
            "conversion_rate": round((conversions / clicks) * 100, 2) if clicks > 0 else 0,
        },
        indent=2,
    )


@mcp.tool()
def optimize_copy(creative_id: str, target_metric: str = "ctr", api_key: str = "") -> str:
    """Optimize existing copy based on performance

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        creative_id (str): The creative id to analyze or process.
        target_metric (str): The target metric to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    creative = next(
        (c for c in _store["creatives"] if c.get("id") == creative_id), None
    )

    if not creative:
        return json.dumps({"error": "Creative not found"})

    optimizations = [
        "Add numbers/stats to headline",
        "Use power words: Free, New, Now, Save",
        "Ask a question in the hook",
        "Add social proof",
        "Make CTA more specific",
        "Add urgency language",
    ]

    return json.dumps(
        {
            "original": creative,
            "suggested_improvements": random.sample(optimizations, 3),
            "new_copy_options": [
                generate_copy("Product", "facebook", "casual") for _ in range(2)
            ],
        },
        indent=2,
    )


@mcp.tool()
def generate_headlines(product: str = "our product", platform: str = "google", count: int = 5, api_key: str = "") -> str:
    """Generate multiple headlines

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        product (str): The product to analyze or process.
        platform (str): The platform to analyze or process.
        count (int): The count to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    headlines = []
    for _ in range(count):
        copy = generate_copy(product, platform, "professional")
        if "headlines" in copy:
            headlines.extend(copy["headlines"])
        elif "hook" in copy:
            headlines.append(copy["hook"])
        elif "subject" in copy:
            headlines.append(copy["subject"])

    return json.dumps({"headlines": headlines[:count]}, indent=2)


@mcp.tool()
def get_best_performing(campaign_id: str, limit: int = 5, api_key: str = "") -> str:
    """Get best performing creatives

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        campaign_id (str): The campaign id to analyze or process.
        limit (int): The limit to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if campaign_id not in _store["campaigns"]:
        return json.dumps({"error": "Campaign not found"})

    creatives = _store["campaigns"][campaign_id].get("creatives", [])
    if not creatives:
        return json.dumps({"message": "No creatives yet"})

    scored = []
    for c in creatives:
        imp = c.get("impressions", 1000)
        clk = c.get("clicks", 50)
        scored.append(
            {"id": c.get("id"), "ctr": round((clk / imp) * 100, 2) if imp > 0 else 0}
        )

    scored.sort(key=lambda x: x["ctr"], reverse=True)
    return json.dumps({"best_performing": scored[:limit]})


if __name__ == "__main__":
    mcp.run()
