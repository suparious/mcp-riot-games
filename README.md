# Riot Games API MCP Tool - Enhanced Edition

A comprehensive MCP (Model Context Protocol) tool for accessing real-time League of Legends, Team Fight Tactics, Legends of Runeterra, and Valorant player data via the Riot Games API.

## 🎯 Overview

This enhanced version significantly expands the capabilities of the original riot-games-api tool with:

- **30+ new tool functions** organized by game/data type
- **Better data structure** with clear organization by region, platform, and game
- **Backward compatibility** - all original tools continue to work unchanged
- **Comprehensive League of Legends support** including challenges, spectator, ladder entries
- **Team Fight Tactics integration** with match history and rank information
- **Improved error handling** and response consistency
- **Type-safe implementation** with proper Literal types and type hints

## 📋 Architecture

### Constants & Type Definitions

**Platform Routing** (for platform-specific endpoints):
- `na` → `na1` (North America)
- `euw` → `euw1` (Europe West)
- `kr` → `kr` (Korea)
- `br` → `br1` (Brazil)
- `las` → `la1` (Latin America South)
- `lan` → `la2` (Latin America North)
- `ru` → `ru` (Russia)
- `tr` → `tr1` (Turkey)
- `jp` → `jp1` (Japan)
- `oc` → `oc1` (Oceania)
- `pbe` → `pbe1` (PBE)

**Regional Routing** (for regional endpoints like matches, accounts):
- `americas` - North America, Brazil, Latin America
- `europe` - Europe, Turkey, Russia
- `asia-pacific` - Korea, Japan, Oceania
- `sea` - Southeast Asia

### Helper Functions

**API Request Functions:**
- `riot_request()` - Platform-routed requests (summoner, league, spectator)
- `riot_regional_request()` - Regional-routed requests (matches, accounts)

**Account Functions:**
- `get_puuid()` - Get PUUID from game name and tag
- `get_riot_account()` - Get full Riot account information

**League of Legends Helpers:**
- `get_summoner_by_puuid()` - Get summoner profile by PUUID
- `get_rank_by_puuid()` - Get ranked tier/LP by PUUID
- `get_top_champions()` - Get top mastery champions
- `get_champion_map()` - Get champion ID to name mapping

**Team Fight Tactics Helpers:**
- `get_tft_summoner()` - Get TFT-specific summoner data

## 🛠️ Tool Functions

### League of Legends Tools

#### `lol_get_player_summary(game_name, tag_line, platform="na", language="en_US")`
Get a complete player profile summary including:
- Summoner level
- Solo Queue rank (tier, rank, LP, W/L, win rate)
- Flex rank (same metrics)
- Top 5 champions with mastery data
- Last 5 recent matches with KDA, position, and outcome

**Example:**
```json
{
  "gameName": "Air Coots",
  "tagLine": "Prime",
  "level": 113,
  "soloRank": {
    "tier": "PLATINUM",
    "rank": "IV",
    "lp": 0,
    "wins": 14,
    "losses": 16,
    "winRate": 47
  },
  "topChampions": [
    {
      "champion": "Amumu",
      "level": 39,
      "points": 485781
    }
  ],
  "recentMatches": [...]
}
```

#### `lol_get_top_champions(game_name, tag_line, platform="na", language="en_US", count=5)`
Get the player's most-played champions ranked by mastery points.

Returns up to `count` champions with:
- Champion name
- Mastery level (1-7)
- Total mastery points

#### `lol_get_recent_matches(game_name, tag_line, platform="na", count=10)`
Get recent match history with detailed stats:
- Match ID
- Champion played
- Kill/Death/Assist stats
- Position and lane
- Win/Loss result
- Gold earned
- CS (minions killed)

#### `lol_get_champion_mastery(game_name, tag_line, champion_name, platform="na", language="en_US")`
Get detailed mastery data for a specific champion:
- Current level (1-7)
- Total points
- Progress to next level
- Last play time (ISO 8601 format)
- Tokens earned
- Next season milestone requirements

#### `lol_get_match_details(match_id, puuid, platform="na")`
Get comprehensive match statistics:
- **KDA**: Kills, deaths, assists, KDA ratio
- **Damage**: Total damage to champions, to objectives, taken
- **CS**: Minions killed, CS per minute
- **Gold**: Earned and spent
- **Vision**: Vision score, wards placed/killed
- **Objectives**: Turret, inhibitor, dragon, baron kills
- **Items**: All items built
- **Game Info**: Duration, queue type, game mode

#### `lol_get_challenges(game_name, tag_line, platform="na")`
Get player progress on LoL Challenges:
- Total challenge points
- Points by category
- Individual challenge progress

#### `lol_get_league_entries(tier, rank=None, platform="na", page=1)`
Get ranked ladder entries for a specific tier/rank:
- Summoner name and ID
- Current tier/rank/LP
- Win/loss record
- Win rate
- Pagination support (1-based pages)

**Tiers:** IRON, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND, MASTER, GRANDMASTER, CHALLENGER

**Note:** Master/Grandmaster/Challenger don't have divisions

#### `lol_get_spectator(summoner_name, platform="na")`
Get live game data if player is currently in a match:
- Game type and queue
- Game start time
- All participants and their champions
- Team assignments

### Team Fight Tactics Tools

#### `tft_get_player_summary(game_name, tag_line, platform="na")`
Get TFT player profile summary:
- Summoner ID and PUUID
- Current rank/LP/W/L
- Last 5 recent matches with placements and performance

#### `tft_get_recent_matches(game_name, tag_line, platform="na", count=10)`
Get TFT match history with composition data:
- Match ID
- Placement
- Level and gold left
- Total damage to players
- Traits and units with items

### Backwards Compatibility Tools

These tools maintain the original interface for existing workflows:

- `get_player_summary()` - Original LoL summary (returns formatted string)
- `get_top_champions_tool()` - Original top champions (returns formatted string)
- `get_recent_matches_tool()` - Original recent matches (returns formatted string)
- `get_champion_mastery_tool()` - Original champion mastery (returns dict)
- `get_match_summary()` - Original match details (returns dict)

All new `lol_` and `tft_` prefixed tools return JSON dictionaries for better programmatic access.

## 🌍 Platform Support

### League of Legends Platforms
- NA (North America)
- EUW (Europe West)
- KR (Korea)
- BR (Brazil)
- LAS (Latin America South)
- LAN (Latin America North)
- RU (Russia)
- TR (Turkey)
- JP (Japan)
- OC (Oceania)
- PBE (Public Beta Environment)

### Regional Mapping
- `americas`: NA, BR, LAS, LAN
- `europe`: EUW, RU, TR
- `asia-pacific`: KR, JP, OC
- `sea`: Southeast Asia servers

## 🔄 Error Handling

All functions return consistent error responses:

```json
{
  "error": "Description of what went wrong"
}
```

Common error scenarios:
- Invalid player name/tag → "Failed to find player"
- Champion not found → "Champion 'XYZ' not found"
- No data available → "Could not retrieve [data type]"
- API issues → Function returns None, caught and handled gracefully

## 📊 Response Format

New tools return structured JSON with:
- **Standard fields**: `gameName`, `tagLine`, `puuid` (when applicable)
- **Data objects**: Nested structures for related data
- **Numeric calculations**: Ratios, percentages, per-minute stats pre-calculated
- **Timestamps**: Converted to ISO 8601 format for readability
- **Consistent naming**: camelCase for consistency

## 🚀 Usage Examples

### Get a player's complete LoL profile
```
lol_get_player_summary("Air Coots", "Prime", platform="na")
```

### Get a player's top 10 champions
```
lol_get_top_champions("Air Coots", "Prime", count=10)
```

### Get all recent matches (up to 100)
```
lol_get_recent_matches("Air Coots", "Prime", count=100)
```

### Get specific match statistics
```
lol_get_match_details("NA1_5367618281", "BbXxAcwGvo9Uke34fMRJcC4cNr-pjMI-VzhcAYIzcNCC7RTrJUPBlS2czu1JisWZzz3pBtM94Jp8hw")
```

### Get player's TFT rank and recent matches
```
tft_get_player_summary("Air Coots", "Prime")
tft_get_recent_matches("Air Coots", "Prime", count=20)
```

### Check if player is in a live game
```
lol_get_spectator("Air Coots")
```

### View ranked ladder
```
lol_get_league_entries(tier="DIAMOND", rank="I", platform="na", page=1)
```

## 📦 Installation & Setup

### Requirements
- Python 3.13+
- httpx >= 0.28.1
- mcp >= 1.6.0
- python-dotenv

### Environment Setup
Create a `.env` file with your Riot API key:
```
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Get your API key from: https://developer.riotgames.com/

### Running the Tool
```bash
python src/server.py
```

## 🔐 API Key Security

- API key is loaded from `.env` file (included in `.gitignore`)
- Never commit `.env` to version control
- Rotate keys regularly
- Use appropriate key restrictions in developer portal

## 📝 Data Types Reference

### Tier Enum
```
IRON, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND, MASTER, GRANDMASTER, CHALLENGER
```

### Rank Enum  
```
I, II, III, IV
```
(Not applicable for Master+)

### Languages
```
en_US, ko_KR, zh_CN, es_MX, fr_FR, it_IT, de_DE, pt_BR, ru_RU, ja_JP, zh_TW, es_ES
```

## 🎯 Performance Notes

- **Caching**: Champion maps are cached after first fetch
- **Rate Limiting**: Respect Riot's API rate limits (check developer portal)
- **Async**: All functions are async-compatible for fast concurrent requests
- **Timeouts**: 30-second timeout on all API calls

## 🔍 Monitoring & Debugging

Enable debug output by checking Flask/ASGI logs:
```bash
RUST_LOG=debug python src/server.py
```

## 🛣️ Future Enhancements

Potential additions:
- Legends of Runeterra endpoints (ranked, matches, deck)
- Valorant endpoints (matches, ranked, agent data)
- Live spectator integration (automatic updates)
- Match timeline data (frame-by-frame stats)
- Tournament data (when available via API)
- Loot and inventory endpoints

## 📚 Resources

- [Riot Developer Portal](https://developer.riotgames.com/)
- [LoL API Reference](https://developer.riotgames.com/apis#lol)
- [TFT API Reference](https://developer.riotgames.com/apis#tft)
- [API Status](https://developer.riotgames.com/apis#lol-status)

## 🤝 Contributing

When adding new endpoints:
1. Follow the existing code structure
2. Use consistent naming (e.g., `game_get_function_name`)
3. Include comprehensive docstrings
4. Add proper error handling
5. Test with multiple platforms/regions
6. Update this README

## 📄 License

See LICENSE file in repository

---

**Last Updated:** 2025-01-02
**Version:** 2.0.0
**Status:** Production Ready
