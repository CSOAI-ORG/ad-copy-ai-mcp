# Ad Copy AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — AI-powered ad copy generation for multi-platform campaigns

## Installation

```bash
pip install ad-copy-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install ad-copy-ai-mcp
```

## Tools

### `generate_ad_copy`
Generate ad copy for a specific platform with hooks, body text, and CTAs.

**Parameters:**
- `product` (str): Product or service name
- `platform` (str): Target platform (facebook, google, linkedin, instagram, tiktok, twitter, email)
- `tone` (str): Tone of voice (professional, casual, urgent)
- `benefit` (str): Key benefit to highlight
- `industry` (str): Industry context

### `generate_variants`
Generate multiple ad variants for A/B testing.

**Parameters:**
- `product` (str): Product or service name
- `platform` (str): Target platform
- `count` (int): Number of variants to generate (default 3)

### `create_campaign`
Create an ad campaign with product, platforms, and budget.

**Parameters:**
- `campaign_name` (str): Campaign name
- `product` (str): Product or service
- `platforms` (list): Target platforms
- `budget` (float): Campaign budget
- `start_date` (str): Campaign start date

### `get_campaign`
Get campaign details by ID.

**Parameters:**
- `campaign_id` (str): Campaign identifier

### `add_creative`
Add a creative asset to an existing campaign.

**Parameters:**
- `campaign_id` (str): Campaign identifier
- `creative` (dict): Creative data

### `get_performance`
Get creative performance metrics (impressions, clicks, CTR, conversions).

**Parameters:**
- `campaign_id` (str): Campaign identifier
- `creative_id` (str): Creative identifier

### `optimize_copy`
Optimize existing copy based on performance with improvement suggestions.

**Parameters:**
- `creative_id` (str): Creative identifier
- `target_metric` (str): Metric to optimize for (default 'ctr')

### `generate_headlines`
Generate multiple headlines for a platform.

**Parameters:**
- `product` (str): Product or service name
- `platform` (str): Target platform
- `count` (int): Number of headlines (default 5)

### `get_best_performing`
Get best performing creatives in a campaign ranked by CTR.

**Parameters:**
- `campaign_id` (str): Campaign identifier
- `limit` (int): Max results (default 5)

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
