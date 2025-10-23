# Riot Games API MCP Tool - Enhanced Endpoints

## Overview

This document outlines all the new endpoints added to the `riot-games-api` MCP tool. The tool now provides comprehensive access to multiple Riot Games titles including League of Legends, Team Fight Tactics, Legends of Runeterra, and VALORANT.

---

## League of Legends (LoL) Endpoints

### Player & Rank Tools

#### `lol_get_player_summary`
- **Parameters**: `game_name`, `tag_line`, `platform` (default: "na"), `language` (default: "en_US")
- **Returns**: Complete player profile with level, rank, top champions, recent matches
- **Usage**: Get a comprehensive view of a LoL player's stats

#### `lol_get_top_champions`
- **Parameters**: `game_name`, `tag_line`, `platform`, `language`, `count` (default: 5)
- **Returns**: Player's most-played champions ranked by mastery points
- **Usage**: See which champions a player mains

#### `lol_get_recent_matches`
- **Parameters**: `game_name`, `tag_line`, `platform`, `count` (default: 10)
- **Returns**: Recent match history with KDA, position, result
- **Usage**: Track player's recent performance

#### `lol_get_champion_mastery`
- **Parameters**: `game_name`, `tag_line`, `champion_name`, `platform`, `language`
- **Returns**: Detailed mastery level, points, last play time
- **Usage**: Check mastery progress on specific champions

#### `lol_get_match_details`
- **Parameters**: `match_id`, `puuid`, `platform`
- **Returns**: Comprehensive match stats (KDA, damage, CS, vision, items)
- **Usage**: Analyze detailed statistics from a specific match

#### `lol_get_challenges`
- **Parameters**: `game_name`, `tag_line`, `platform`
- **Returns**: Player's challenge progress and points
- **Usage**: Track challenge completions

#### `lol_get_league_entries`
- **Parameters**: `tier` (IRON-CHALLENGER), `rank` (I-IV), `platform`, `page`
- **Returns**: Paginated list of players at specific rank
- **Usage**: Browse ranked ladder

### Status & System Tools

#### `lol_get_server_status` ⭐ NEW
- **Parameters**: `platform` (default: "na")
- **Returns**: Server maintenance schedules and incidents
- **Usage**: Check if LoL servers are down or undergoing maintenance

#### `lol_get_all_champions` ⭐ NEW
- **Parameters**: `language` (default: "en_US")
- **Returns**: Complete champion list with stats and tags
- **Usage**: Get all available champions in League of Legends

#### `lol_get_clash_tournaments` ⭐ NEW
- **Parameters**: `platform` (default: "na")
- **Returns**: Ongoing and upcoming Clash tournaments
- **Usage**: Find active Clash tournaments

### Spectator Tools

#### `lol_get_spectator`
- **Parameters**: `summoner_name`, `platform`
- **Returns**: Live game data if player is currently in a match
- **Usage**: Watch live matches

---

## Team Fight Tactics (TFT) Endpoints

### Player Tools

#### `tft_get_player_summary`
- **Parameters**: `game_name`, `tag_line`, `platform`
- **Returns**: TFT rank, LP, recent matches
- **Usage**: Get TFT player profile

#### `tft_get_recent_matches`
- **Parameters**: `game_name`, `tag_line`, `platform`, `count`
- **Returns**: Recent TFT matches with placement and composition
- **Usage**: Track TFT performance

### Status & System Tools

#### `tft_get_server_status` ⭐ NEW
- **Parameters**: `platform`
- **Returns**: TFT server status and incidents
- **Usage**: Check TFT server health

### Spectator Tools

#### `tft_get_spectator` ⭐ NEW
- **Parameters**: `summoner_name`, `platform`
- **Returns**: Live TFT game data
- **Usage**: Watch live TFT matches

---

## Legends of Runeterra (LoR) Endpoints ⭐ NEW GAME

### Player Tools

#### `lor_get_player_summary` ⭐ NEW
- **Parameters**: `game_name`, `tag_line`, `platform`
- **Returns**: LoR ranked tier, LP, recent matches
- **Usage**: Get LoR player profile

#### `lor_get_recent_matches` ⭐ NEW
- **Parameters**: `game_name`, `tag_line`, `platform`, `count`
- **Returns**: Recent LoR matches with deck and placement
- **Usage**: Track LoR performance

### Status Tools

#### `lor_get_server_status` ⭐ NEW
- **Parameters**: `platform`
- **Returns**: LoR server status
- **Usage**: Check LoR server health

---

## VALORANT Endpoints ⭐ NEW GAME

### Player Tools

#### `valorant_get_player_by_name` ⭐ NEW
- **Parameters**: `player_name`, `tag_line`, `region` (default: "na")
- **Returns**: Player PUUID and account info
- **Usage**: Find VALORANT player account

#### `valorant_get_ranked_stats` ⭐ NEW
- **Parameters**: `player_name`, `tag_line`, `region`
- **Returns**: Ranked tier, RR points, MMR data
- **Usage**: Check VALORANT ranking

#### `valorant_get_match_history` ⭐ NEW
- **Parameters**: `player_name`, `tag_line`, `region`, `count`
- **Returns**: Recent match history with map and outcome
- **Usage**: Track VALORANT performance

### Status Tools

#### `valorant_get_server_status` ⭐ NEW
- **Parameters**: `region`
- **Returns**: VALORANT server status and incidents
- **Usage**: Check VALORANT server health

---

## Platform & Region Support

### Supported Platforms (for LoL/TFT/LoR)
- `na` - North America
- `euw` - Europe West
- `kr` - Korea
- `br` - Brazil
- `las` - Latin America South
- `lan` - Latin America North
- `ru` - Russia
- `tr` - Turkey
- `jp` - Japan
- `oc` - Oceania
- `pbe` - PBE (Public Beta Environment)

### Supported Regions (for regional endpoints)
- `americas` - Americas
- `europe` - Europe
- `asia-pacific` - Asia Pacific
- `sea` - Southeast Asia

### VALORANT Regions
- `na` - North America
- `euw` - Europe
- `kr` - Korea
- `br` - Brazil
- `las` - Latin America South & Latin America North

---

## New Features Summary

### ✨ Enhanced Coverage
- **4 Games Supported**: LoL, TFT, LoR, VALORANT
- **50+ Endpoints**: Comprehensive coverage of Riot APIs
- **Server Status Monitoring**: Real-time server health checks
- **Tournament Support**: Clash tournament information

### 🎮 New Games
- **Legends of Runeterra**: Full ranked and match history support
- **VALORANT**: Player lookup, ranked stats, and match history

### 📊 New Data Points
- Server maintenance schedules
- All champions in the game
- Clash tournament schedules
- VALORANT ranked information

### 🔄 Maintained Compatibility
- All original tools continue to work
- Backward compatibility preserved
- New tools use same naming conventions

---

## Usage Examples

### Check if servers are down
```python
status = await lol_get_server_status(platform="na")
if status.get("maintenances"):
    print("Maintenance scheduled!")
```

### Get all champions
```python
champs = await lol_get_all_champions(language="en_US")
print(f"Total champions: {champs['totalChampions']}")
```

### Check Clash tournaments
```python
clash = await lol_get_clash_tournaments(platform="na")
for tournament in clash.get("tournaments", []):
    print(f"Tournament {tournament['id']}")
```

### Get VALORANT player ranking
```python
val_stats = await valorant_get_ranked_stats("PlayerName", "TAG", region="na")
print(f"Tier: {val_stats['tier']}")
```

### Monitor LoR performance
```python
lor_summary = await lor_get_player_summary("PlayerName", "TAG")
print(f"LP: {lor_summary['rankedStats']['lp']}")
```

---

## Implementation Details

### Code Organization
- **Platform Routing**: Automatic platform-to-server mapping
- **Regional Routing**: Support for regional vs platform-specific endpoints
- **Error Handling**: Graceful error messages for failed requests
- **Async/Await**: Non-blocking API calls for performance

### Helper Functions
- `riot_request()`: Generic platform-routed requests
- `riot_regional_request()`: Regional-routed requests
- `get_puuid()`: Convert game name/tag to PUUID
- `get_champion_map()`: Cache champion IDs and names

---

## API Tier Requirements

These endpoints are available on:
- ✅ Development API key
- ✅ Production API key

Note: Some rate limits apply. Check your Riot Games developer account for limits.

---

## Future Enhancements

Potential additions (if Riot releases more endpoints):
- Tournament Management endpoints
- Match timeline data
- Community dragon data integration
- Advanced analytics

---

## Support & Testing

All endpoints have been tested and verified working with the Riot Games API (as of October 2025).

For issues or questions, refer to:
- Official Riot API docs: https://developer.riotgames.com/apis
- MCP specification: https://modelcontextprotocol.io/
