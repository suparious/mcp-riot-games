# Riot Games API MCP Tool - Quick Reference Card

## 🚀 Quick Start (Copy & Paste)

### Get Player Profile
```python
from src.server import lol_get_player_summary
import asyncio

async def main():
    profile = await lol_get_player_summary("Air Coots", "Prime")
    print(f"Rank: {profile['soloRank']['tier']}")

asyncio.run(main())
```

### Get Top Champions
```python
champs = await lol_get_top_champions("Name", "Tag", count=5)
for c in champs['topChampions']:
    print(f"{c['champion']}: Level {c['level']}")
```

### Get Recent Matches
```python
matches = await lol_get_recent_matches("Name", "Tag", count=10)
for m in matches['recentMatches']:
    print(f"{m['champion']}: {m['kda']} - {m['result']}")
```

### Get Match Details
```python
details = await lol_get_match_details("NA1_123456", "puuid-here")
print(f"KDA: {details['kda']['kills']}/{details['kda']['deaths']}/{details['kda']['assists']}")
print(f"CS/min: {details['cs']['csPerMinute']}")
```

---

## 📚 All Tools Cheat Sheet

### League of Legends Tools
```python
# Profile & Overview
lol_get_player_summary(name, tag, platform="na", language="en_US")
lol_get_top_champions(name, tag, platform="na", language="en_US", count=5)
lol_get_recent_matches(name, tag, platform="na", count=10)

# Champion Details
lol_get_champion_mastery(name, tag, champion, platform="na", language="en_US")

# Match Analysis
lol_get_match_details(match_id, puuid, platform="na")

# Rankings & Progress
lol_get_league_entries(tier="DIAMOND", rank="I", platform="na", page=1)
lol_get_challenges(name, tag, platform="na")

# Live Games
lol_get_spectator(name, platform="na")
```

### Team Fight Tactics Tools
```python
tft_get_player_summary(name, tag, platform="na")
tft_get_recent_matches(name, tag, platform="na", count=10)
```

### Legacy Tools (Still Work!)
```python
get_player_summary(name, tag, language="en_US")
get_top_champions_tool(name, tag, language="en_US", count=3)
get_recent_matches_tool(name, tag, count=3)
get_champion_mastery_tool(name, tag, champion, language="en_US")
get_match_summary(match_id, puuid)
```

---

## 🌍 Platforms
```
"na", "euw", "kr", "br", "las", "lan", "ru", "tr", "jp", "oc", "pbe"
```

## 🏆 Tiers
```
"CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND", "PLATINUM", 
"GOLD", "SILVER", "BRONZE", "IRON"
```

## 📊 Common Fields

### Player Response
```python
{
    "gameName": str,
    "tagLine": str,
    "puuid": str,
    "level": int,
    "soloRank": {"tier", "rank", "lp", "wins", "losses", "winRate"},
    "flexRank": {...} or None,
    "topChampions": [{"champion", "level", "points"}],
    "recentMatches": [{"matchId", "champion", "kda", "result", "cs", "gold"}]
}
```

### Match Details Response
```python
{
    "matchId": str,
    "champion": str,
    "result": "Win" or "Loss",
    "kda": {"kills", "deaths", "assists", "ratio"},
    "cs": {"totalCs", "csPerMinute"},
    "gold": {"goldEarned", "goldSpent"},
    "damage": {"totalDamageDealtToChampions", "totalDamageTaken"},
    "vision": {"visionScore", "wardsPlaced", "wardsKilled"},
    "gameDuration": {"seconds", "minutes"}
}
```

---

## ⚡ One-Liners

### Check if friend is playing
```python
result = await lol_get_spectator("FriendName"); print("Playing!" if "error" not in result else "Not playing")
```

### Get win rate
```python
m = await lol_get_recent_matches("Name", "Tag", 20); wr = sum(1 for x in m['recentMatches'] if x['result']=='Win')/len(m['recentMatches'])*100; print(f"{wr:.1f}%")
```

### Find main champion
```python
c = await lol_get_top_champions("Name", "Tag", 1); print(c['topChampions'][0]['champion'])
```

### Check TFT rank
```python
tft = await tft_get_player_summary("Name", "Tag"); print(f"{tft['tftRank']['tier']} {tft['tftRank']['lp']} LP")
```

---

## 🔧 Useful Patterns

### Loop through multiple players
```python
async def check_friends(friends: list[tuple[str, str]]):
    for name, tag in friends:
        profile = await lol_get_player_summary(name, tag)
        if "error" not in profile:
            print(f"{name}: {profile['level']}")
```

### Concurrent requests
```python
import asyncio

profiles = await asyncio.gather(*[
    lol_get_player_summary(name, tag) 
    for name, tag in [("P1", "T1"), ("P2", "T2"), ("P3", "T3")]
])
```

### Safe data access
```python
result = await lol_get_player_summary("Name", "Tag")
if "error" not in result and result.get("soloRank"):
    tier = result["soloRank"]["tier"]
```

### Calculate statistics
```python
matches = await lol_get_recent_matches("Name", "Tag", 50)
wins = sum(1 for m in matches['recentMatches'] if m['result'] == 'Win')
avg_cs = sum(m['cs'] for m in matches['recentMatches']) / len(matches['recentMatches'])
print(f"WR: {wins}/{len(matches['recentMatches'])}, Avg CS: {avg_cs:.0f}")
```

---

## ❌ Common Mistakes

```python
# ❌ WRONG - Missing platform parameter
await lol_get_player_summary("Name")

# ✅ CORRECT
await lol_get_player_summary("Name", "Tag")

# ❌ WRONG - Tag in wrong case
await lol_get_player_summary("Name", "tag")  # Should be "NA1"

# ✅ CORRECT
await lol_get_player_summary("Name", "NA1")

# ❌ WRONG - Incomplete champion name
await lol_get_champion_mastery("Name", "Tag", "Lee")  # Lee Sin is the name

# ✅ CORRECT
await lol_get_champion_mastery("Name", "Tag", "Lee Sin")

# ❌ WRONG - Accessing without checking for error
tier = result['soloRank']['tier']  # Could throw KeyError

# ✅ CORRECT
tier = result.get('soloRank', {}).get('tier', 'Unknown')
```

---

## 📱 Platform to Region Mapping

| Platform | Code | Region |
|----------|------|--------|
| North America | na | americas |
| Europe West | euw | europe |
| Korea | kr | asia-pacific |
| Brazil | br | americas |
| Latin America South | las | americas |
| Latin America North | lan | americas |
| Russia | ru | europe |
| Turkey | tr | europe |
| Japan | jp | asia-pacific |
| Oceania | oc | asia-pacific |
| PBE | pbe | americas |

---

## 🎯 Scenario Quick Solutions

### "Get someone's main champion"
```python
champs = await lol_get_top_champions("Name", "Tag", count=1)
main = champs['topChampions'][0]['champion']
```

### "Check recent performance"
```python
matches = await lol_get_recent_matches("Name", "Tag", count=10)
recent_wr = sum(1 for m in matches['recentMatches'] if m['result']=='Win') / 10
```

### "Get rank with formatting"
```python
prof = await lol_get_player_summary("Name", "Tag")
print(f"{prof['soloRank']['tier']} {prof['soloRank']['rank']} {prof['soloRank']['lp']}LP")
```

### "Find top Diamond players"
```python
ladder = await lol_get_league_entries("DIAMOND", "I", page=1)
for player in ladder['entries'][:10]:
    print(f"{player['summonerName']}: {player['winRate']}% WR")
```

### "Analyze last game"
```python
matches = await lol_get_recent_matches("Name", "Tag", count=1)
match_id = matches['recentMatches'][0]['matchId']
details = await lol_get_match_details(match_id, "puuid")
print(f"KDA: {details['kda']['kills']}/{details['kda']['deaths']}/{details['kda']['assists']}")
```

### "Check TFT performance"
```python
tft = await tft_get_player_summary("Name", "Tag")
matches = await tft_get_recent_matches("Name", "Tag", 10)
top_4 = sum(1 for m in matches['matches'] if m['placement'] <= 4)
print(f"Top 4 rate: {top_4}/10")
```

---

## 🔍 Error Checking

### Check for errors in response
```python
result = await lol_get_player_summary("Name", "Tag")

if isinstance(result, dict):
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Success: Level {result['level']}")
```

### Validate parameters
```python
# Check tier value
if tier not in ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]:
    print("Invalid tier")

# Check platform value
platforms = ["na", "euw", "kr", "br", "las", "lan", "ru", "tr", "jp", "oc", "pbe"]
if platform not in platforms:
    print("Invalid platform")
```

---

## 📞 Support Links

| Resource | Link |
|----------|------|
| API Docs | https://developer.riotgames.com/apis |
| API Status | https://developer.riotgames.com/apis#lol-status |
| Get API Key | https://developer.riotgames.com/ |
| Troubleshooting | See TROUBLESHOOTING.md |
| Full Examples | See EXAMPLES.md |
| All Tools | See TOOLS_REFERENCE.md |

---

## ⏱️ Response Times

| Operation | Typical Time |
|-----------|-------------|
| Player summary | 500-1000ms |
| Recent matches (5) | 1-2s |
| Champion mastery | 200-400ms |
| Match details | 200-500ms |
| League entries | 300-600ms |
| TFT summary | 500-1000ms |

---

## 🎓 Learning Path

1. **Start:** This quick reference
2. **Explore:** TOOLS_REFERENCE.md for all options
3. **Learn:** EXAMPLES.md for real code
4. **Master:** ARCHITECTURE.md for how it works
5. **Debug:** TROUBLESHOOTING.md when stuck
6. **Upgrade:** MIGRATION.md if upgrading

---

**Version:** 2.0.0  
**Last Updated:** 2025-01-02  
**Print This:** Yes! Keep nearby while coding 📋
