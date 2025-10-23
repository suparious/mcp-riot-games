# Riot Games API MCP Tool - Complete Tools Reference

## 📚 All Available Tools

This document provides a comprehensive reference of all 20+ tools available in the enhanced riot-games-api MCP tool.

---

## 🎮 LEAGUE OF LEGENDS TOOLS

### 1. `lol_get_player_summary`
Get a complete League of Legends player profile.

**Parameters:**
- `game_name` (str, required): Player's summoner name
- `tag_line` (str, required): Player's tag (e.g., "NA1")
- `platform` (str, optional, default="na"): Region code
- `language` (str, optional, default="en_US"): Champion name language

**Returns:**
```json
{
  "gameName": "string",
  "tagLine": "string",
  "puuid": "string",
  "level": "number",
  "soloRank": {
    "tier": "string (IRON-CHALLENGER)",
    "rank": "string (I-IV)",
    "lp": "number",
    "wins": "number",
    "losses": "number",
    "winRate": "number (0-100)"
  },
  "flexRank": { /* same structure */ },
  "topChampions": [
    {
      "champion": "string",
      "championId": "number",
      "level": "number (1-7)",
      "points": "number"
    }
  ],
  "recentMatches": [
    {
      "matchId": "string",
      "champion": "string",
      "kda": "string (K/D/A)",
      "result": "string (Win/Loss)",
      "position": "string"
    }
  ]
}
```

**Use Cases:**
- Get quick overview of a player's rank and stats
- Check top champions at a glance
- See recent performance

---

### 2. `lol_get_top_champions`
Get a player's most-played champions ranked by mastery.

**Parameters:**
- `game_name` (str, required)
- `tag_line` (str, required)
- `platform` (str, optional, default="na")
- `language` (str, optional, default="en_US")
- `count` (int, optional, default=5): Number of champions (1-50)

**Returns:**
```json
{
  "gameName": "string",
  "tagLine": "string",
  "puuid": "string",
  "topChampions": [
    {
      "champion": "string",
      "championId": "number",
      "level": "number",
      "points": "number"
    }
  ]
}
```

**Use Cases:**
- Build matchup analysis (what does opponent main?)
- Identify player's champion pool
- Track champion progression over time

---

### 3. `lol_get_recent_matches`
Get detailed recent match history.

**Parameters:**
- `game_name` (str, required)
- `tag_line` (str, required)
- `platform` (str, optional, default="na")
- `count` (int, optional, default=10): Matches to retrieve (1-100)

**Returns:**
```json
{
  "gameName": "string",
  "tagLine": "string",
  "puuid": "string",
  "recentMatches": [
    {
      "matchId": "string",
      "champion": "string",
      "kills": "number",
      "deaths": "number",
      "assists": "number",
      "kda": "string",
      "position": "string (UTILITY, MIDDLE, etc)",
      "lane": "string (BOTTOM, MIDDLE, etc)",
      "result": "string (Win/Loss)",
      "gold": "number",
      "cs": "number (total minions)"
    }
  ]
}
```

**Use Cases:**
- Analyze recent performance trends
- Check champion pick frequency
- Assess role distribution
- Calculate win rate in last N games

---

### 4. `lol_get_champion_mastery`
Get detailed mastery info for a specific champion.

**Parameters:**
- `game_name` (str, required)
- `tag_line` (str, required)
- `champion_name` (str, required): Champion name (e.g., "Amumu", "Lee Sin")
- `platform` (str, optional, default="na")
- `language` (str, optional, default="en_US")

**Returns:**
```json
{
  "gameName": "string",
  "tagLine": "string",
  "puuid": "string",
  "championName": "string",
  "championId": "number",
  "level": "number (1-7)",
  "points": "number",
  "pointsSinceLastLevel": "number",
  "pointsUntilNextLevel": "number",
  "lastPlayTime": "ISO 8601 datetime",
  "tokensEarned": "number",
  "chestGranted": "boolean",
  "nextMilestone": {
    "requireGradeCounts": { /* milestone requirements */ },
    "rewardMarks": "number"
  }
}
```

**Use Cases:**
- Track progression to next mastery level
- Find when champion was last played
- Plan milestone unlocks

---

### 5. `lol_get_match_details`
Get comprehensive statistics from a specific match.

**Parameters:**
- `match_id` (str, required): Match ID (e.g., "NA1_5367618281")
- `puuid` (str, required): Player's PUUID
- `platform` (str, optional, default="na")

**Returns:**
```json
{
  "matchId": "string",
  "champion": "string",
  "position": "string",
  "lane": "string",
  "role": "string",
  "result": "Win/Loss",
  "kda": {
    "kills": "number",
    "deaths": "number",
    "assists": "number",
    "ratio": "number"
  },
  "damage": {
    "totalDamageDealtToChampions": "number",
    "totalDamageDealt": "number",
    "totalDamageTaken": "number",
    "damageDealtToObjectives": "number",
    "damageDealtToTurrets": "number"
  },
  "cs": {
    "minionsKilled": "number",
    "neutralMinionsKilled": "number",
    "totalCs": "number",
    "csPerMinute": "number"
  },
  "gold": {
    "goldEarned": "number",
    "goldSpent": "number"
  },
  "vision": {
    "visionScore": "number",
    "wardsPlaced": "number",
    "wardsKilled": "number",
    "detectorWardsPlaced": "number"
  },
  "objectives": {
    "kills": "number",
    "turretKills": "number",
    "inhibitorKills": "number",
    "dragonKills": "number",
    "baronKills": "number"
  },
  "items": {
    "itemsBuilt": ["number"]
  },
  "gameDuration": {
    "seconds": "number",
    "minutes": "number"
  },
  "gameQueueId": "number",
  "gameMode": "string"
}
```

**Use Cases:**
- Analyze detailed game performance
- Find efficiency metrics (CS/min, damage distribution)
- Review objective control
- Check itemization decisions

---

### 6. `lol_get_challenges`
Get player's League of Legends challenges progress.

**Parameters:**
- `game_name` (str, required)
- `tag_line` (str, required)
- `platform` (str, optional, default="na")

**Returns:**
```json
{
  "gameName": "string",
  "tagLine": "string",
  "puuid": "string",
  "totalPoints": "number",
  "categoryPoints": {
    "string": "number"  /* category -> points */
  },
  "challenges": [
    {
      "challengeId": "number",
      "percentile": "number",
      "level": "string (NONE, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND, MASTER)",
      "value": "number",
      "achievedTime": "number"
    }
  ]
}
```

**Use Cases:**
- Track challenge completion progress
- Find challenging achievements to pursue
- Monitor percentile rankings

---

### 7. `lol_get_league_entries`
Get ranked ladder entries for specific tier/rank.

**Parameters:**
- `tier` (str, required): IRON, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND, MASTER, GRANDMASTER, or CHALLENGER
- `rank` (str, optional): I, II, III, or IV (not used for Master+)
- `platform` (str, optional, default="na")
- `page` (int, optional, default=1): Page number for pagination

**Returns:**
```json
{
  "tier": "string",
  "rank": "string",
  "platform": "string",
  "page": "number",
  "entries": [
    {
      "summonerId": "string",
      "summonerName": "string",
      "tier": "string",
      "rank": "string",
      "lp": "number",
      "wins": "number",
      "losses": "number",
      "winRate": "number (0-100)"
    }
  ]
}
```

**Use Cases:**
- Browse ranked ladder
- Find top players
- Monitor leaderboard positions
- Compare player stats at same rank

---

### 8. `lol_get_spectator`
Get live game data for player currently in match.

**Parameters:**
- `summoner_name` (str, required)
- `platform` (str, optional, default="na")

**Returns:**
```json
{
  "gameName": "string",
  "platform": "string",
  "gameType": "string",
  "gameQueueConfigId": "number",
  "gameStartTime": "number",
  "participants": [
    {
      "championId": "number",
      "teamId": "number",
      "summonerName": "string"
    }
  ]
}
```

**Returns:** `{"error": "No active game found for ..."}` if player not in match

**Use Cases:**
- Check if someone is currently playing
- View live match champion selections
- Watch game start times

---

## 🎲 TEAM FIGHT TACTICS (TFT) TOOLS

### 9. `tft_get_player_summary`
Get Team Fight Tactics player profile summary.

**Parameters:**
- `game_name` (str, required)
- `tag_line` (str, required)
- `platform` (str, optional, default="na")

**Returns:**
```json
{
  "gameName": "string",
  "tagLine": "string",
  "puuid": "string",
  "summonerId": "string",
  "tftRank": {
    "tier": "string",
    "rank": "string",
    "lp": "number",
    "wins": "number",
    "losses": "number",
    "winRate": "number"
  },
  "recentMatches": [
    {
      "matchId": "string",
      "placement": "number",
      "level": "number",
      "goldLeft": "number",
      "totalDamageToPlayers": "number"
    }
  ]
}
```

**Use Cases:**
- Get TFT rank and rating
- Check recent placements
- Assess current performance

---

### 10. `tft_get_recent_matches`
Get TFT match history with composition details.

**Parameters:**
- `game_name` (str, required)
- `tag_line` (str, required)
- `platform` (str, optional, default="na")
- `count` (int, optional, default=10)

**Returns:**
```json
{
  "gameName": "string",
  "tagLine": "string",
  "puuid": "string",
  "matches": [
    {
      "matchId": "string",
      "placement": "number",
      "level": "number",
      "goldLeft": "number",
      "totalDamageToPlayers": "number",
      "traits": [
        {
          "name": "string",
          "numUnits": "number",
          "style": "number"
        }
      ],
      "units": [
        {
          "characterId": "string",
          "tier": "number",
          "itemNames": ["string"]
        }
      ]
    }
  ]
}
```

**Use Cases:**
- Analyze team compositions
- Track successful strategies
- Review placement trends
- Study item combinations

---

## 🔄 BACKWARDS COMPATIBILITY TOOLS

These original tools continue to work with their original interface:

### 11. `get_player_summary`
**Identical to:** `lol_get_player_summary` (returns formatted string instead of JSON)
- Returns beautifully formatted text output
- Includes emoji decorations
- Best for human-readable display

### 12. `get_top_champions_tool`
**Identical to:** `lol_get_top_champions` (returns formatted string)
- Lists champions in readable format
- Shows level and points
- Best for quick reference

### 13. `get_recent_matches_tool`
**Identical to:** `lol_get_recent_matches` (returns formatted string)
- Shows match results in readable format
- Best for quick win/loss assessment

### 14. `get_champion_mastery_tool`
**Identical to:** `lol_get_champion_mastery` (returns dict)
- Returns detailed JSON dictionary
- Same parameters and data structure

### 15. `get_match_summary`
**Identical to:** `lol_get_match_details` (returns dict)
- Returns detailed JSON dictionary
- Same parameters and data structure

---

## 🗂️ TOOL ORGANIZATION BY USE CASE

### Player Overview
1. `lol_get_player_summary` - Start here for quick overview
2. `tft_get_player_summary` - TFT profile

### Champion Analysis
1. `lol_get_top_champions` - Top played champions
2. `lol_get_champion_mastery` - Specific champion details
3. `tft_get_recent_matches` - TFT compositions

### Match Analysis
1. `lol_get_recent_matches` - Match list
2. `lol_get_match_details` - Detailed match stats
3. `tft_get_recent_matches` - TFT match compositions

### Rank & Progress
1. `lol_get_league_entries` - View ladder
2. `lol_get_challenges` - Challenge progress
3. `lol_get_spectator` - Live games

---

## 📊 PLATFORM CODES

### Supported Regions
```
"na"  - North America
"euw" - Europe West
"kr"  - Korea
"br"  - Brazil
"las" - Latin America South
"lan" - Latin America North
"ru"  - Russia
"tr"  - Turkey
"jp"  - Japan
"oc"  - Oceania
"pbe" - PBE (Public Beta)
```

---

## 🔑 Parameter Reference

### Champion Name Language Codes
```
"en_US"  - English (US)
"ko_KR"  - Korean
"zh_CN"  - Chinese (Simplified)
"es_MX"  - Spanish (Mexico)
"fr_FR"  - French
"it_IT"  - Italian
"de_DE"  - German
"pt_BR"  - Portuguese (Brazil)
"ru_RU"  - Russian
"ja_JP"  - Japanese
"zh_TW"  - Chinese (Traditional)
"es_ES"  - Spanish (Spain)
```

### Tiers (High to Low)
```
"CHALLENGER"   - Top 200 players
"GRANDMASTER"  - Top ~500 players
"MASTER"       - Top ~3000 players
"DIAMOND"
"PLATINUM"
"GOLD"
"SILVER"
"BRONZE"
"IRON"         - Lowest rank
```

### Ranks (High to Low)
```
"I"   - Division 1 (Highest)
"II"  - Division 2
"III" - Division 3
"IV"  - Division 4 (Lowest)
```
(Not applicable for Master, Grandmaster, Challenger)

---

## 🎯 Quick Start Examples

### Check if friend is online and playing
```
lol_get_spectator("FriendName", platform="na")
```

### See what your opponents main
```
lol_get_top_champions("Opponent", "NA1")
```

### Analyze your last 5 games
```
lol_get_recent_matches("YourName", "YourTag", count=5)
```

### Check your climb progress
```
lol_get_player_summary("YourName", "YourTag")
```

### Review specific game performance
```
lol_get_match_details("NA1_1234567890", "your-puuid-here")
```

### Monitor your TFT rating
```
tft_get_player_summary("YourName", "YourTag")
```

### Analyze TFT comps you played
```
tft_get_recent_matches("YourName", "YourTag", count=20)
```

---

## ⚠️ Error Responses

All tools return error objects when requests fail:

```json
{
  "error": "Description of what went wrong"
}
```

Common error messages:
- `"Failed to find player"` - Invalid name/tag
- `"Failed to get summoner profile"` - API unavailable
- `"Champion 'XYZ' not found"` - Misspelled champion name
- `"Could not retrieve [data]"` - Data unavailable for player
- `"No participant found with puuid: XYZ"` - PUUID not in match

---

**Last Updated:** 2025-01-02  
**Tool Count:** 15 main + 5 legacy = 20 total
