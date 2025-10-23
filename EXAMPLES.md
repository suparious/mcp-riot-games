# Riot Games API MCP Tool - Code Examples & Quick Reference

## 🚀 Quick Start (5 Minutes)

### Installation
```bash
# The tool is already configured in Claude Desktop
# Just restart Claude Desktop after the updates
```

### Simplest Example: Get Player Profile
```python
import asyncio
from src.server import lol_get_player_summary

async def main():
    profile = await lol_get_player_summary("Air Coots", "Prime", platform="na")
    print(f"Level: {profile['level']}")
    print(f"Rank: {profile['soloRank']['tier']} {profile['soloRank']['rank']}")
    print(f"Win Rate: {profile['soloRank']['winRate']}%")

asyncio.run(main())
```

---

## 📖 Common Scenarios

### Scenario 1: Check If Friend Is Online/Playing
```python
# Check live game
result = await lol_get_spectator("FriendName", platform="na")

if "error" not in result:
    print(f"✅ {result['gameName']} is in a game!")
    print(f"   Queue: {result['gameType']}")
    print(f"   Participants: {len(result['participants'])}")
else:
    print("❌ Not currently playing")
```

### Scenario 2: Pre-Game Research on Opponent
```python
# Get opponent's profile
opponent_data = await lol_get_player_summary("Opponent", "OpTag")

# Find their main champion
main_champ = opponent_data['topChampions'][0]
print(f"⚠️ Watch out! They main {main_champ['champion']} (Level {main_champ['level']})")

# Check their recent win rate
recent = opponent_data['recentMatches'][:10]
wins = sum(1 for m in recent if m['result'] == 'Win')
print(f"Recent form: {wins}/10 wins")

# Get mastery details
mastery = await lol_get_champion_mastery(
    "Opponent", "OpTag", 
    champion_name=main_champ['champion']
)
print(f"Mastery: Level {mastery['level']} with {mastery['points']:,} points")
```

### Scenario 3: Analyze Your Recent Games
```python
# Get your last 20 games
matches = await lol_get_recent_matches(
    "YourName", "YourTag", 
    count=20
)

# Calculate statistics
wins = sum(1 for m in matches['recentMatches'] if m['result'] == 'Win')
losses = len(matches['recentMatches']) - wins
win_rate = (wins / (wins + losses)) * 100

print(f"Recent Performance: {wins}W-{losses}L ({win_rate:.1f}% WR)")

# Most played champion
from collections import Counter
champs = Counter(m['champion'] for m in matches['recentMatches'])
print(f"Most Played: {champs.most_common(1)[0][0]}")

# Best role this patch
roles = Counter(m['position'] for m in matches['recentMatches'])
print(f"Preferred Role: {roles.most_common(1)[0][0]}")

# Analyze detailed performance
for i, match in enumerate(matches['recentMatches'][:5], 1):
    print(f"\nGame {i}: {match['champion']} - {match['kda']} {match['result']}")
```

### Scenario 4: Climb Tracking
```python
# Compare current and previous rank
current = await lol_get_player_summary("YourName", "YourTag")
current_lp = current['soloRank']['lp']
current_tier = current['soloRank']['tier']

print(f"Current: {current_tier} {current_lp} LP")

# Track recent match performance
matches = await lol_get_recent_matches("YourName", "YourTag", count=5)
recent_wins = sum(1 for m in matches['recentMatches'] if m['result'] == 'Win')
print(f"Last 5 games: {recent_wins} wins")

# Calculate projected LP gain
if recent_wins >= 3:
    print("✅ On a winning streak! Climb incoming!")
elif recent_wins == 1:
    print("😐 Mixed results. Keep grinding!")
else:
    print("❌ Losing streak. Take a break?")
```

### Scenario 5: Champion Mastery Progression
```python
# Track multiple champions
champs = ["Amumu", "Lee Sin", "Thresh"]

for champ in champs:
    mastery = await lol_get_champion_mastery(
        "YourName", "YourTag",
        champion_name=champ
    )
    
    current = mastery['points']
    until_next = mastery['pointsUntilNextLevel']
    level = mastery['level']
    
    if until_next > 0:
        progress = (current - mastery['pointsSinceLastLevel']) / (mastery['pointsUntilNextLevel'] + mastery['pointsSinceLastLevel']) * 100
        print(f"{champ}: Level {level} ({progress:.1f}% to next level)")
    else:
        print(f"{champ}: Level {level} (Maxed out!)")
```

### Scenario 6: Ranked Ladder Analysis
```python
# Browse top 200 Diamonds
ladder = await lol_get_league_entries(
    tier="DIAMOND",
    rank="I",
    platform="na",
    page=1
)

print("Top Diamond I Players:")
for entry in ladder['entries'][:10]:
    print(f"{entry['summonerName']:20} - {entry['lp']} LP ({entry['winRate']}% WR)")

# Find specific player on ladder
target_name = "PlayerName"
entry = next(
    (e for e in ladder['entries'] if e['summonerName'] == target_name),
    None
)

if entry:
    print(f"\nFound {target_name}!")
    print(f"Position: {entry['lp']} LP")
    print(f"Record: {entry['wins']}W-{entry['losses']}L")
else:
    print(f"{target_name} not in top 200 of this division")
```

### Scenario 7: Detailed Match Review
```python
# Get recent match
matches = await lol_get_recent_matches("YourName", "YourTag", count=1)
match_id = matches['recentMatches'][0]['matchId']

# Get full details
details = await lol_get_match_details(
    match_id, 
    puuid="your-puuid-here"
)

print(f"Match Result: {details['result']}")
print(f"Champion: {details['champion']}")
print(f"Duration: {details['gameDuration']['minutes']} minutes")
print()

# KDA Analysis
kda = details['kda']
print(f"KDA: {kda['kills']}/{kda['deaths']}/{kda['assists']} (Ratio: {kda['ratio']:.2f})")

# Damage Analysis
dmg = details['damage']
print(f"Damage to champs: {dmg['totalDamageDealtToChampions']:,}")
print(f"Damage taken: {dmg['totalDamageTaken']:,}")

# Economy Analysis
gold = details['gold']
print(f"Gold earned: {gold['goldEarned']:,}")
cs = details['cs']
print(f"CS: {cs['totalCs']} ({cs['csPerMinute']} per minute)")

# Vision Analysis
vision = details['vision']
print(f"Vision score: {vision['visionScore']}")
print(f"Wards: {vision['wardsPlaced']} placed, {vision['wardsKilled']} killed")

# Objectives
obj = details['objectives']
print(f"Objectives: {obj['turretKills']} turrets, {obj['dragonKills']} dragons")
```

### Scenario 8: Challenge Tracking
```python
# Get challenge data
challenges = await lol_get_challenges("YourName", "YourTag")

print(f"Total Challenge Points: {challenges['totalPoints']}")
print(f"Categories:")
for category, points in challenges['categoryPoints'].items():
    print(f"  {category}: {points} points")

# Find high-value challenges
high_value = [c for c in challenges['challenges'] 
              if c.get('level') in ['PLATINUM', 'DIAMOND', 'MASTER']]
print(f"\nYour best achievements: {len(high_value)}")
for challenge in high_value[:5]:
    level = challenge.get('level', 'UNKNOWN')
    value = challenge.get('value', 0)
    print(f"  {level}: {value}")
```

### Scenario 9: TFT Rank Tracking
```python
# Get current TFT rating
tft_profile = await tft_get_player_summary("YourName", "YourTag")

rank = tft_profile['tftRank']
print(f"TFT Rank: {rank['tier']} {rank['rank']} ({rank['lp']} LP)")
print(f"Record: {rank['wins']}W-{rank['losses']}L ({rank['winRate']}% WR)")

# Analyze recent placements
matches = await tft_get_recent_matches("YourName", "YourTag", count=10)
placements = [m['placement'] for m in matches['matches']]

top_4_rate = sum(1 for p in placements if p <= 4) / len(placements) * 100
print(f"Top 4 rate: {top_4_rate:.1f}%")
print(f"Avg placement: {sum(placements) / len(placements):.1f}")
```

### Scenario 10: TFT Composition Analysis
```python
# Get recent matches with full composition
matches = await tft_get_recent_matches(
    "YourName", "YourTag",
    count=10
)

# Find your best placement
best_match = min(matches['matches'], key=lambda m: m['placement'])
print(f"Best placement: #{best_match['placement']}")
print(f"Level: {best_match['level']}")

# Analyze traits
print("Traits:")
for trait in best_match['traits']:
    print(f"  {trait.get('name', 'Unknown')}: {trait.get('numUnits')} units")

# List units
print("Units:")
for unit in best_match['units']:
    stars = "⭐" * unit['tier']
    items = ", ".join(unit['itemNames']) if unit['itemNames'] else "No items"
    print(f"  {unit['characterId']} {stars}")
    print(f"    Items: {items}")
```

---

## 🛠️ Utility Functions

### Get Formatted Output
```python
def format_match(match: dict) -> str:
    """Format a match in readable way"""
    return (
        f"{match['matchId']}\n"
        f"  {match['champion']} - {match['kda']}\n"
        f"  {match['position']} ({match['lane']})\n"
        f"  Result: {match['result']}\n"
        f"  Gold: {match['gold']:,} | CS: {match['cs']}"
    )

# Usage
matches = await lol_get_recent_matches("Name", "Tag", count=5)
for match in matches['recentMatches'][:3]:
    print(format_match(match))
```

### Calculate Win Rate
```python
def calculate_win_rate(matches: list[dict]) -> float:
    """Calculate win rate from match list"""
    if not matches:
        return 0.0
    wins = sum(1 for m in matches if m['result'] == 'Win')
    return (wins / len(matches)) * 100

# Usage
matches = await lol_get_recent_matches("Name", "Tag", count=100)
wr = calculate_win_rate(matches['recentMatches'])
print(f"Overall WR: {wr:.1f}%")
```

### Group Matches By Champion
```python
from collections import defaultdict

def group_by_champion(matches: list[dict]) -> dict[str, list]:
    """Group matches by champion played"""
    by_champ = defaultdict(list)
    for match in matches:
        by_champ[match['champion']].append(match)
    return dict(by_champ)

# Usage
matches = await lol_get_recent_matches("Name", "Tag", count=50)
by_champion = group_by_champion(matches['recentMatches'])

for champ, champ_matches in sorted(by_champion.items()):
    wr = calculate_win_rate(champ_matches)
    print(f"{champ}: {len(champ_matches)} games, {wr:.1f}% WR")
```

### Get Average Stats
```python
def get_average_stats(matches: list[dict]) -> dict:
    """Calculate average stats across matches"""
    if not matches:
        return {}
    
    total_kills = sum(m['kills'] for m in matches)
    total_deaths = sum(m['deaths'] for m in matches)
    total_assists = sum(m['assists'] for m in matches)
    total_cs = sum(m['cs'] for m in matches)
    total_gold = sum(m['gold'] for m in matches)
    
    count = len(matches)
    return {
        'avgKills': total_kills / count,
        'avgDeaths': total_deaths / count,
        'avgAssists': total_assists / count,
        'avgCS': total_cs / count,
        'avgGold': total_gold / count,
        'avgKDA': (total_kills + total_assists) / (total_deaths if total_deaths > 0 else 1) / count,
    }

# Usage
matches = await lol_get_recent_matches("Name", "Tag", count=30)
stats = get_average_stats(matches['recentMatches'])
print(f"Average: {stats['avgKills']:.1f}K / {stats['avgDeaths']:.1f}D / {stats['avgAssists']:.1f}A")
```

---

## 📊 Data Schemas

### Player Summary Response
```python
{
    "gameName": "Air Coots",
    "tagLine": "Prime",
    "puuid": "BbXx...",
    "level": 113,
    
    # Solo Queue Rank
    "soloRank": {
        "tier": "PLATINUM",
        "rank": "IV",
        "lp": 0,
        "wins": 14,
        "losses": 16,
        "winRate": 47
    },
    
    # Flex Rank (can be null)
    "flexRank": None,
    
    # Top Champions
    "topChampions": [
        {
            "champion": "Amumu",
            "championId": 32,
            "level": 7,
            "points": 485781
        }
    ],
    
    # Recent Matches
    "recentMatches": [
        {
            "matchId": "NA1_5367618281",
            "champion": "Fiddlesticks",
            "kills": 3,
            "deaths": 14,
            "assists": 21,
            "kda": "3/14/21",
            "position": "UTILITY",
            "lane": "BOTTOM",
            "result": "Win",
            "gold": 8500,
            "cs": 42
        }
    ]
}
```

### Match Details Response
```python
{
    "matchId": "NA1_5367618281",
    "champion": "Fiddlesticks",
    "position": "UTILITY",
    "lane": "BOTTOM",
    "role": "SOLO",
    "result": "Win",
    
    # KDA
    "kda": {
        "kills": 3,
        "deaths": 14,
        "assists": 21,
        "ratio": 1.71
    },
    
    # Damage
    "damage": {
        "totalDamageDealtToChampions": 18717,
        "totalDamageDealt": 25000,
        "totalDamageTaken": 30000,
        "damageDealtToObjectives": 5000,
        "damageDealtToTurrets": 3000
    },
    
    # CS
    "cs": {
        "minionsKilled": 25,
        "neutralMinionsKilled": 17,
        "totalCs": 42,
        "csPerMinute": 1.19
    },
    
    # Gold
    "gold": {
        "goldEarned": 8500,
        "goldSpent": 8200
    },
    
    # Vision
    "vision": {
        "visionScore": 88,
        "wardsPlaced": 18,
        "wardsKilled": 3,
        "detectorWardsPlaced": 5
    },
    
    # Objectives
    "objectives": {
        "kills": 3,
        "turretKills": 2,
        "inhibitorKills": 0,
        "dragonKills": 1,
        "baronKills": 0
    },
    
    # Items
    "items": {
        "itemsBuilt": [3157, 3050, 3123, 3116]
    },
    
    # Game Info
    "gameDuration": {
        "seconds": 2162,
        "minutes": 36.0
    },
    "gameQueueId": 440,
    "gameMode": "CLASSIC"
}
```

---

## ⚡ Performance Tips

### Batch Requests
```python
# Efficient: Get all data for multiple players
async def get_multiple_profiles(players: list[tuple[str, str]]):
    tasks = [
        lol_get_player_summary(name, tag)
        for name, tag in players
    ]
    return await asyncio.gather(*tasks)

# Usage
profiles = await get_multiple_profiles([
    ("Player1", "NA1"),
    ("Player2", "NA2"),
    ("Player3", "NA3"),
])
```

### Cache Results
```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_player_summary(game_name: str, tag_line: str):
    return await lol_get_player_summary(game_name, tag_line)

# Subsequent calls return cached results
```

### Limit API Calls
```python
# Only get recent 10 matches instead of 100
matches = await lol_get_recent_matches(
    "Name", "Tag",
    count=10  # Keep this reasonable
)

# Filter locally instead of multiple API calls
champions = [m['champion'] for m in matches['recentMatches']]
```

---

## 🔍 Error Handling

### Check for Errors
```python
result = await lol_get_player_summary("Name", "Tag")

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Level: {result['level']}")
```

### Graceful Degradation
```python
async def safe_get_profile(game_name: str, tag_line: str):
    try:
        result = await lol_get_player_summary(game_name, tag_line)
        if "error" in result:
            print(f"API returned error: {result['error']}")
            return None
        return result
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

profile = await safe_get_profile("Name", "Tag")
if profile:
    print(f"Rank: {profile['soloRank']['tier']}")
```

---

## 🌐 Platform Examples

### Check Players Across Regions
```python
async def compare_across_regions(name: str, tag: str):
    regions = ["na", "euw", "kr", "br"]
    results = {}
    
    for region in regions:
        try:
            data = await lol_get_player_summary(name, tag, platform=region)
            if "error" not in data:
                results[region] = data['soloRank']
        except:
            pass
    
    return results

rankings = await compare_across_regions("PlayerName", "Tag")
for region, rank_info in rankings.items():
    if rank_info:
        print(f"{region}: {rank_info['tier']} {rank_info['rank']}")
```

---

**Last Updated:** 2025-01-02  
**Version:** 2.0.0
