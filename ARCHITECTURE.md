# Riot Games API MCP Tool - Architecture & Codebase Guide

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Claude Desktop                                │
│                    (MCP Client / Consumer)                           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                    MCP Protocol
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                   riot-games-api MCP Server                          │
│                    (src/server.py)                                   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │           CONSTANTS & TYPE DEFINITIONS                  │       │
│  │  ┌─────────────────┬──────────────────┬─────────────┐   │       │
│  │  │ Platform Routes │ Regional Routes  │ Mappings    │   │       │
│  │  │ (11 regions)    │ (4 regions)      │ (auto map)  │   │       │
│  │  └─────────────────┴──────────────────┴─────────────┘   │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │           HELPER FUNCTIONS                              │       │
│  │  ┌─────────────┬──────────────┬────────────────────────┐ │       │
│  │  │ API Request │ Account/Auth │ Data Retrieval         │ │       │
│  │  │             │              │                        │ │       │
│  │  │ •riot_req   │ •get_puuid   │ •get_champion_map     │ │       │
│  │  │ •regional   │ •get_account │ •get_summoner         │ │       │
│  │  │   _request  │              │ •get_rank             │ │       │
│  │  │             │              │ •get_top_champions    │ │       │
│  │  │             │              │ •get_tft_summoner     │ │       │
│  │  └─────────────┴──────────────┴────────────────────────┘ │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │              MCP TOOLS (PUBLIC API)                      │       │
│  │                                                          │       │
│  │  League of Legends (8 tools)  TFT (2 tools)            │       │
│  │  ────────────────────────     ─────────────────        │       │
│  │  • lol_get_player_summary     • tft_get_player_summary  │       │
│  │  • lol_get_top_champions      • tft_get_recent_matches  │       │
│  │  • lol_get_recent_matches                              │       │
│  │  • lol_get_champion_mastery   Legacy Tools (5)         │       │
│  │  • lol_get_match_details      ──────────────          │       │
│  │  • lol_get_challenges         • get_player_summary     │       │
│  │  • lol_get_league_entries     • get_top_champions_tool│       │
│  │  • lol_get_spectator          • get_recent_matches_tool│       │
│  │                               • get_champion_mastery_tool│       │
│  │                               • get_match_summary       │       │
│  └──────────────────────────────────────────────────────────┘       │
└─────────────────────────┬────────────────────────────────────────────┘
                          │
                    HTTPX Async Client
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Riot Games   │  │ Riot Games   │  │ DataDragon   │
│ Platform API │  │ Regional API │  │ (Champion)   │
│              │  │              │  │              │
│ - Summoner   │  │ - Matches    │  │ - Versions   │
│ - League     │  │ - Accounts   │  │ - Champions  │
│ - Champion   │  │ - Challenges │  │ - Localiz.   │
│   Mastery    │  │ - Spectator  │  │              │
│              │  │ - TFT        │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 📂 File Structure

```
/home/shaun/repos/mcp-riot/
│
├── src/
│   ├── __init__.py              (Empty module marker)
│   └── server.py                (MAIN FILE - 1000+ lines)
│       ├── Imports & Setup
│       ├── Constants (Platform/Regional routing)
│       ├── Helper: API Requests
│       ├── Helper: Account/Auth
│       ├── Helper: Data Retrieval
│       ├── Tools: League of Legends (8 tools)
│       ├── Tools: Team Fight Tactics (2 tools)
│       └── Tools: Backwards Compatibility (5 tools)
│
├── .env                         (API Key - keep secret!)
├── .env.example                 (Template for .env)
├── .gitignore                   (Exclude sensitive files)
├── pyproject.toml              (Project configuration)
├── uv.lock                      (Dependency lock file)
│
├── README.md                    (Overview & setup)
├── TOOLS_REFERENCE.md          (Complete tool reference)
├── ENHANCEMENTS.md             (What's new in v2.0)
├── EXAMPLES.md                 (Code examples & patterns)
├── ARCHITECTURE.md             (This file)
│
└── .git/                        (Version control)
```

---

## 🔄 Data Flow Examples

### Example 1: Getting Player Summary
```
User Request:
  lol_get_player_summary("Air Coots", "Prime")
                    ▼
      1. get_puuid("Air Coots", "Prime")
         └─ riot_regional_request()
            └─ https://americas.api.riotgames.com/riot/account/v1/...
               └─ Return: PUUID
                    ▼
      2. get_summoner_by_puuid(puuid, "na")
         └─ riot_request()
            └─ https://na1.api.riotgames.com/lol/summoner/v4/...
               └─ Return: {level, profileIcon, ...}
                    ▼
      3. get_rank_by_puuid(puuid, "na")
         └─ riot_request()
            └─ https://na1.api.riotgames.com/lol/league/v4/...
               └─ Return: [{queueType, tier, rank, lp, ...}]
                    ▼
      4. get_top_champions(puuid, champ_map, count=5)
         └─ riot_request()
            └─ https://na1.api.riotgames.com/lol/champion-mastery/v4/...
               └─ Return: [{championId, level, points}]
                    ▼
      5. get_recent_matches(puuid, count=5)
         └─ riot_regional_request()
            └─ https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/
               └─ Return: [match_id_1, match_id_2, ...]
                    ▼
      6. For each match_id, fetch match details
         └─ riot_regional_request(/lol/match/v5/matches/{match_id})
            └─ Return: {info: {participants: [...]}}
                    ▼
      7. Extract player participant data
                    ▼
      Return Combined: {gameName, level, soloRank, topChampions, recentMatches}
```

### Example 2: Platform Routing Logic
```
User specifies: platform="na"
                ▼
    PLATFORM_ROUTING["na"] = "na1"
                ▼
    Use in API call: https://na1.api.riotgames.com/...
                ▼
    
Also maps to regional: PLATFORM_TO_REGION["na"] = "americas"
                ▼
    For regional endpoints: https://americas.api.riotgames.com/...
```

---

## 🛠️ Code Organization

### Section 1: Imports & Constants
```python
Lines 1-50:
- Imports (mcp, httpx, os, typing, dotenv, datetime)
- MCP server initialization
- API key loading from .env
- Platform/Regional routing dictionaries
- Champion cache initialization
```

### Section 2: API Request Functions
```python
Lines 51-120:
- riot_request()
  * Platform-routed requests
  * Error handling (404, HTTP status codes)
  * Timeout management
  * Header setup
  
- riot_regional_request()
  * Regional-routed requests
  * Same error handling approach
  * Used for matches, accounts, challenges
```

### Section 3: Account & Authentication
```python
Lines 121-145:
- get_puuid()
  * Takes game_name, tag_line
  * Returns PUUID via Riot Account API
  
- get_riot_account()
  * Full account information
  * Used for future extensibility
```

### Section 4: Data Retrieval (Champions)
```python
Lines 146-165:
- get_champion_map()
  * Fetches from DataDragon
  * Caches results (key: language)
  * Maps champion_id → name
  * Called for champion name resolution
```

### Section 5: League of Legends Helpers
```python
Lines 166-230:
- get_summoner_by_puuid()
- get_rank_by_puuid()
- get_top_champions()
  
These are private helpers called by public tools
```

### Section 6: Team Fight Tactics Helpers
```python
Lines 231-240:
- get_tft_summoner()
  * TFT-specific summoner data
```

### Section 7: League of Legends Tools
```python
Lines 241-600:
@mcp.tool() decorated functions:
1. lol_get_player_summary()
2. lol_get_top_champions()
3. lol_get_recent_matches()
4. lol_get_champion_mastery()
5. lol_get_match_details()
6. lol_get_challenges()
7. lol_get_league_entries()
8. lol_get_spectator()
```

### Section 8: Team Fight Tactics Tools
```python
Lines 601-700:
@mcp.tool() decorated functions:
1. tft_get_player_summary()
2. tft_get_recent_matches()
```

### Section 9: Backwards Compatibility
```python
Lines 701-820:
Original tools that maintain interface compatibility:
1. get_player_summary()
2. get_top_champions_tool()
3. get_recent_matches_tool()
4. get_champion_mastery_tool()
5. get_match_summary()
```

### Section 10: Server Startup
```python
Lines 821-823:
if __name__ == "__main__":
    mcp.run()
```

---

## 🔑 Key Design Decisions

### 1. Routing Separation
**Why:** Riot's API uses two different routing strategies
- **Platform routing** (na1, euw1, kr) for player-specific data
- **Regional routing** (americas, europe) for match/account data

**Implementation:** Two separate request functions with clear naming

### 2. Helper-First Architecture
**Why:** Reduces code duplication and makes adding new tools easier

**Pattern:** Private helpers (`get_*`) → Public tools (`lol_get_*`)

### 3. Backwards Compatibility Layer
**Why:** Don't break existing code that uses the tool

**Solution:** Original 5 tools wrap new tools internally

### 4. Consistent Error Handling
**Why:** Predictable error responses make error handling easier

**Pattern:** Return `{"error": "description"}` on failures

### 5. Data Enrichment
**Why:** Calculate useful metrics from raw API data

**Examples:**
- CS per minute (from duration and CS)
- Win rate (from wins/losses)
- KDA ratio (from K/D/A)
- Damage efficiency (from damage dealt/taken)

### 6. Regional Mapping
**Why:** Hide complexity of platform↔region mapping from users

**Benefit:** Single `platform="na"` parameter handles both needs

---

## 📊 Type System

### Input Types
```python
platform: Literal["na", "euw", "kr", "br", "las", "lan", "ru", "tr", "jp", "oc", "pbe"]
language: str  # e.g., "en_US", "ko_KR"
tier: Literal["IRON", "BRONZE", ..., "CHALLENGER"]
rank: Literal["I", "II", "III", "IV"]
count: int  # Usually 1-100
page: int  # For pagination
```

### Return Types
```python
dict[str, Any]              # Structured response
list[Any]                   # Multiple items
dict[str, Any] | None       # Can be None on error
str                         # Formatted string (legacy tools)
```

### Response Structure Pattern
```python
{
    "gameName": str,
    "tagLine": str,
    "puuid": str,           # Usually included
    
    # Main data field(s)
    "rank": {...},
    "champions": [...],
    "matches": [...],
    
    # OR error case
    "error": str
}
```

---

## 🔍 Adding a New Tool

### Step-by-Step Guide

#### 1. Create Helper Function
```python
async def get_new_data(puuid: str, param: str) -> dict | None:
    """Fetch new data type from API"""
    routing = PLATFORM_ROUTING.get("na", "na1")
    return await riot_request(
        f"/lol/new-endpoint/v1/endpoint/{puuid}",
        platform_routing=routing,
        params={"param": param}
    )
```

#### 2. Create Tool Function
```python
@mcp.tool()
async def lol_get_new_feature(
    game_name: str,
    tag_line: str,
    param: str = "default",
    platform: str = "na"
) -> dict[str, Any]:
    """
    📊 Get new feature data from League of Legends.
    
    Returns: [description of return value]
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}
    
    data = await get_new_data(puuid, param)
    if not data:
        return {"error": "Could not retrieve new data"}
    
    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "newData": data
    }
```

#### 3. Test the Tool
```bash
# Tool automatically available via MCP after restart
```

#### 4. Document in TOOLS_REFERENCE.md
```markdown
### `lol_get_new_feature`
Description...
Parameters...
Returns...
Use Cases...
```

---

## 🐛 Debugging

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Calls
Add print statements in helper functions:
```python
async def riot_request(...):
    full_url = f"https://{platform_routing}.api.riotgames.com{url}"
    print(f"DEBUG: Requesting {full_url}")  # Add this
    ...
```

### Verify API Key
```bash
echo $RIOT_API_KEY  # Check if set
```

### Test Individual Tools
```python
# In interactive Python
import asyncio
from src.server import lol_get_player_summary

result = asyncio.run(lol_get_player_summary("Name", "Tag"))
print(result)
```

---

## 📈 Performance Characteristics

### API Call Efficiency
| Operation | API Calls | Time Est. |
|-----------|-----------|-----------|
| Player Summary | 5-7 | 500-1000ms |
| Recent Matches (10) | 11 | 1-2 seconds |
| Match Details (1) | 1 | 200-400ms |
| Top 100 Games Analysis | 102 | 10-20 seconds |

### Memory Usage
- Champion map cache: ~2MB (per language)
- Typical response: 5-50KB
- No significant memory accumulation

### Caching Benefits
- Champion map: Cached per language (100% hit rate after first call)
- No aggressive caching (always get fresh data)

---

## 🚀 Future Extensibility

### Ready for Implementation
1. **Legends of Runeterra**
   - Mirrors LoL structure
   - Change endpoints to `/lor/`
   - Add `lor_get_*` tools

2. **Valorant**
   - Similar pattern
   - Use `/val/` endpoints
   - Add `val_get_*` tools

3. **Match Timeline**
   - Already have match_id
   - Fetch from `/lol/match/v5/matches/{id}/timeline`
   - Parse frame-by-frame data

4. **Live Spectator Streaming**
   - Implement polling
   - Call `lol_get_spectator()` repeatedly
   - Push updates via WebSocket

### Extensibility Points
1. Helper functions easily wrap new endpoints
2. Consistent routing logic for new games
3. Error handling patterns established
4. Tool registration is automatic via `@mcp.tool()` decorator

---

## 📚 Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| README.md | Overview & setup | Everyone |
| TOOLS_REFERENCE.md | Complete API reference | Developers |
| EXAMPLES.md | Code examples | Developers |
| ENHANCEMENTS.md | What's new | Users upgrading |
| ARCHITECTURE.md | System design | Contributors |

---

## 🤝 Contributing Guidelines

1. Follow existing code style
2. Add docstrings to all functions
3. Use type hints throughout
4. Update TOOLS_REFERENCE.md for new tools
5. Add examples to EXAMPLES.md
6. Test with multiple regions
7. Handle errors gracefully

---

**Last Updated:** 2025-01-02  
**Version:** 2.0.0  
**Status:** Production Ready
