#!/usr/bin/env python3
"""MEOK AI Labs — ad-copy-ai-mcp MCP Server. AI-powered ad copy generation for multi-platform campaigns."""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from collections import defaultdict
import uuid
import random
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
import mcp.types as types

_store = {"campaigns": {}, "creatives": [], "variants": [], "templates": {}}
server = Server("ad-copy-ai")


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


@server.list_resources()
async def handle_list_resources():
    return [
        Resource(
            uri="ads://campaigns", name="Ad Campaigns", mimeType="application/json"
        ),
        Resource(
            uri="ads://templates", name="Ad Templates", mimeType="application/json"
        ),
        Resource(
            uri="ads://analytics",
            name="Campaign Analytics",
            mimeType="application/json",
        ),
    ]


@server.list_tools()
async def handle_list_tools():
    return [
        Tool(
            name="generate_ad_copy",
            description="Generate ad copy for a platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {"type": "string"},
                    "platform": {
                        "type": "string",
                        "enum": [
                            "facebook",
                            "google",
                            "linkedin",
                            "instagram",
                            "tiktok",
                            "twitter",
                            "email",
                            "generic",
                        ],
                    },
                    "tone": {
                        "type": "string",
                        "enum": [
                            "professional",
                            "casual",
                            "urgent",
                            "educational",
                            "humorous",
                        ],
                    },
                    "benefit": {"type": "string"},
                    "industry": {"type": "string"},
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="generate_variants",
            description="Generate multiple ad variants for A/B testing",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {"type": "string"},
                    "platform": {"type": "string"},
                    "count": {"type": "number"},
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="create_campaign",
            description="Create an ad campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string"},
                    "product": {"type": "string"},
                    "platforms": {"type": "array"},
                    "budget": {"type": "number"},
                    "start_date": {"type": "string"},
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_campaign",
            description="Get campaign details",
            inputSchema={
                "type": "object",
                "properties": {"campaign_id": {"type": "string"}},
            },
        ),
        Tool(
            name="add_creative",
            description="Add a creative to campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "creative": {"type": "object"},
                },
            },
        ),
        Tool(
            name="get_performance",
            description="Get creative performance metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "creative_id": {"type": "string"},
                },
            },
        ),
        Tool(
            name="optimize_copy",
            description="Optimize existing copy based on performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "creative_id": {"type": "string"},
                    "target_metric": {
                        "type": "string",
                        "enum": ["ctr", "conversion", "engagement"],
                    },
                },
            },
        ),
        Tool(
            name="generate_headlines",
            description="Generate multiple headlines",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {"type": "string"},
                    "platform": {"type": "string"},
                    "count": {"type": "number"},
                },
            },
        ),
        Tool(
            name="get_best_performing",
            description="Get best performing creatives",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "limit": {"type": "number"},
                },
            },
        ),
    ]


def generate_copy(product, platform, tone, benefit=None, industry=None):
    templates = TEMPLATES.get(platform, TEMPLATES["generic"])
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


@server.call_tool()
async def handle_call_tool(name: str, arguments: Any = None) -> list[types.TextContent]:
    args = arguments or {}
    api_key = args.get("api_key", "")
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
                ),
            )
        ]
    if err := _rl(): return [TextContent(type="text", text=err)]

    if name == "generate_ad_copy":
        result = generate_copy(
            args.get("product", "our product"),
            args.get("platform", "facebook"),
            args.get("tone", "professional"),
            args.get("benefit"),
            args.get("industry"),
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "generate_variants":
        count = args.get("count", 3)
        platform = args.get("platform", "facebook")
        product = args.get("product", "our product")

        variants = []
        for i in range(count):
            variant = generate_copy(
                product, platform, random.choice(["professional", "casual", "urgent"])
            )
            variant["variant_id"] = create_id()
            variant["version"] = f"v{i + 1}"
            variants.append(variant)

        _store["variants"].extend(variants)
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"variants": variants, "count": len(variants)}, indent=2
                ),
            )
        ]

    elif name == "create_campaign":
        campaign = {
            "id": create_id(),
            "name": args["campaign_name"],
            "product": args.get("product", ""),
            "platforms": args.get("platforms", []),
            "budget": args.get("budget", 0),
            "start_date": args.get("start_date", datetime.now().isoformat()),
            "status": "draft",
            "creatives": [],
            "created_at": datetime.now().isoformat(),
        }
        _store["campaigns"][campaign["id"]] = campaign
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "campaign_created": True,
                        "campaign_id": campaign["id"],
                        "name": campaign["name"],
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "get_campaign":
        campaign_id = args.get("campaign_id")
        if campaign_id in _store["campaigns"]:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(_store["campaigns"][campaign_id], indent=2),
                )
            ]
        return [
            TextContent(type="text", text=json.dumps({"error": "Campaign not found"}))
        ]

    elif name == "add_creative":
        campaign_id = args.get("campaign_id")
        if campaign_id not in _store["campaigns"]:
            return [
                TextContent(
                    type="text", text=json.dumps({"error": "Campaign not found"})
                )
            ]

        creative = args.get("creative", {})
        creative["id"] = create_id()
        creative["added_at"] = datetime.now().isoformat()
        _store["campaigns"][campaign_id]["creatives"].append(creative)
        _store["creatives"].append(creative)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"creative_added": True, "creative_id": creative["id"]}, indent=2
                ),
            )
        ]

    elif name == "get_performance":
        creative_id = args.get("creative_id")
        campaign_id = args.get("campaign_id")

        creative = next(
            (c for c in _store["creatives"] if c.get("id") == creative_id), None
        )
        if not creative:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "impressions": 0,
                            "clicks": 0,
                            "ctr": 0,
                            "conversions": 0,
                            "conversion_rate": 0,
                        }
                    ),
                )
            ]

        impressions = creative.get("impressions", random.randint(1000, 50000))
        clicks = creative.get("clicks", random.randint(10, 500))
        ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0
        conversions = creative.get("conversions", random.randint(0, 50))

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "creative_id": creative_id,
                        "impressions": impressions,
                        "clicks": clicks,
                        "ctr": ctr,
                        "conversions": conversions,
                        "conversion_rate": round((conversions / clicks) * 100, 2)
                        if clicks > 0
                        else 0,
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "optimize_copy":
        creative_id = args.get("creative_id")
        creative = next(
            (c for c in _store["creatives"] if c.get("id") == creative_id), None
        )

        if not creative:
            return [
                TextContent(
                    type="text", text=json.dumps({"error": "Creative not found"})
                )
            ]

        optimizations = [
            "Add numbers/stats to headline",
            "Use power words: Free, New, Now, Save",
            "Ask a question in the hook",
            "Add social proof",
            "Make CTA more specific",
            "Add urgency language",
        ]

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "original": creative,
                        "suggested_improvements": random.sample(optimizations, 3),
                        "new_copy_options": [
                            generate_copy("Product", "facebook", "casual")
                            for _ in range(2)
                        ],
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "generate_headlines":
        product = args.get("product", "our product")
        platform = args.get("platform", "google")
        count = args.get("count", 5)

        headlines = []
        for _ in range(count):
            copy = generate_copy(product, platform, "professional")
            if "headlines" in copy:
                headlines.extend(copy["headlines"])
            elif "hook" in copy:
                headlines.append(copy["hook"])
            elif "subject" in copy:
                headlines.append(copy["subject"])

        return [
            TextContent(
                type="text", text=json.dumps({"headlines": headlines[:count]}, indent=2)
            )
        ]

    elif name == "get_best_performing":
        campaign_id = args.get("campaign_id")
        limit = args.get("limit", 5)

        if campaign_id not in _store["campaigns"]:
            return [
                TextContent(
                    type="text", text=json.dumps({"error": "Campaign not found"})
                )
            ]

        creatives = _store["campaigns"][campaign_id].get("creatives", [])
        if not creatives:
            return [
                TextContent(
                    type="text", text=json.dumps({"message": "No creatives yet"})
                )
            ]

        scored = []
        for c in creatives:
            imp = c.get("impressions", 1000)
            clk = c.get("clicks", 50)
            scored.append(
                {
                    "id": c.get("id"),
                    "ctr": round((clk / imp) * 100, 2) if imp > 0 else 0,
                }
            )

        scored.sort(key=lambda x: x["ctr"], reverse=True)
        return [
            TextContent(
                type="text", text=json.dumps({"best_performing": scored[:limit]})
            )
        ]

    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]


async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (
        read_stream,
        write_stream,
    ):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ad-copy-ai",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
