# Riot Games API MCP Tool - Migration Guide

## 🔄 Upgrading from v1.0 to v2.0

### ✅ Good News: Complete Backward Compatibility

Your existing code will continue to work **without any changes**. All original tools are preserved.

---

## 📋 Migration Strategy

### Phase 1: No Action Required (Immediate)
```python
# Your existing code works as-is
summary = await get_player_summary("Name", "Tag")
matches = await get_recent_matches_tool("Name", "Tag")
```

**Benefits of staying on v1.0 interface:**
- No code changes needed
- Familiar string output format
- Continue using existing patterns

---

### Phase 2: Gradual Migration (Optional - Over Time)

Consider migrating to new tools when:
- Adding new features
- Refactoring existing code
- Building new applications
- Needs JSON responses for better data access

#### Option A: Coexist (Mix Old and New)
```python
# Old tools for display
display_summary = await get_player_summary("Name", "Tag")
print(display_summary)  # Formatted string with emojis

# New tools for data processing
data_summary = await lol_get_player_summary("Name", "Tag")
tier = data_summary['soloRank']['tier']  # Direct access
```

#### Option B: Full Migration
Replace all old tool calls with new ones:

**Before:**
```python
summary = await get_player_summary("Name", "Tag")
champions = await get_top_champions_tool("Name", "Tag")
matches = await get_recent_matches_tool("Name", "Tag")
mastery = await get_champion_mastery_tool("Name", "Tag", "Amumu")
match_detail = await get_match_summary("NA1_123", "puuid-here")
```

**After:**
```python
summary = await lol_get_player_summary("Name", "Tag")
champions = await lol_get_top_champions("Name", "Tag")
matches = await lol_get_recent_matches("Name", "Tag")
mastery = await lol_get_champion_mastery("Name", "Tag", "Amumu")
match_detail = await lol_get_match_details("NA1_123", "puuid-here")
```

---

## 🎯 Migration Path by Use Case

### Use Case 1: Display Player Stats to User
**Old (v1.0):**
```python
summary = await get_player_summary("Air Coots", "Prime")
print(summary)
# Output: Pretty formatted string with emojis ✨
```

**New (v2.0) - Option A: Keep displaying strings**
```python
# No change needed! Keep using old tool
summary = await get_player_summary("Air Coots", "Prime")
print(summary)  # Still works perfectly
```

**New (v2.0) - Option B: Custom formatted display**
```python
summary = await lol_get_player_summary("Air Coots", "Prime")

# Build custom format
display = f"""
👤 {summary['gameName']} (Level {summary['level']})
🏅 Rank: {summary['soloRank']['tier']} {summary['soloRank']['rank']}
🔥 Main: {summary['topChampions'][0]['champion']}
"""
print(display)
```

---

### Use Case 2: Analyze Match Performance
**Old (v1.0):**
```python
matches = await get_recent_matches_tool("Name", "Tag", count=5)
# Parse string output manually 😞
lines = matches.split("\n")
# Complex string parsing...
```

**New (v2.0):**
```python
matches = await lol_get_recent_matches("Name", "Tag", count=5)

# Direct access to structured data 🎉
for match in matches['recentMatches']:
    print(f"{match['champion']}: {match['kda']} - {match['result']}")
    print(f"  CS: {match['cs']}, Gold: {match['gold']}")
```

---

### Use Case 3: Track Multiple Players
**Old (v1.0):**
```python
players = [("Player1", "Tag1"), ("Player2", "Tag2")]

for name, tag in players:
    summary = await get_player_summary(name, tag)
    # String parsing to extract rank
    rank_line = summary.split("\n")[2]  # Fragile!
    print(rank_line)
```

**New (v2.0):**
```python
players = [("Player1", "Tag1"), ("Player2", "Tag2")]

summaries = await asyncio.gather(
    *[lol_get_player_summary(name, tag) for name, tag in players]
)

for summary in summaries:
    rank = summary['soloRank']['tier']
    print(f"{summary['gameName']}: {rank}")
```

---

### Use Case 4: New Feature - TFT Support
**Old (v1.0):**
```python
# Not possible! TFT support didn't exist ❌
```

**New (v2.0):**
```python
# Now you can!
tft = await tft_get_player_summary("Name", "Tag")
print(f"TFT Rank: {tft['tftRank']['tier']}")

# Get recent matches with compositions
matches = await tft_get_recent_matches("Name", "Tag", count=10)
for match in matches['matches']:
    print(f"Placement #{match['placement']}")
    for trait in match['traits']:
        print(f"  {trait['name']}: {trait['numUnits']} units")
```

---

### Use Case 5: New Feature - Ranked Ladder
**Old (v1.0):**
```python
# Not possible! ❌
```

**New (v2.0):**
```python
# Browse ranked ladder!
ladder = await lol_get_league_entries(
    tier="DIAMOND",
    rank="I",
    platform="na",
    page=1
)

print("Top Diamond I Players:")
for player in ladder['entries'][:10]:
    print(f"{player['summonerName']}: {player['lp']} LP ({player['winRate']}% WR)")
```

---

## 🔧 Refactoring Examples

### Example 1: Simple Player Summary
```python
# BEFORE (v1.0)
async def get_player_rank(name: str, tag: str) -> str:
    summary = await get_player_summary(name, tag)
    # Extract from formatted string (fragile)
    lines = summary.split("\n")
    rank_line = lines[2]  # "🏅 Rank: ..."
    return rank_line

# AFTER (v2.0)
async def get_player_rank(name: str, tag: str) -> str:
    summary = await lol_get_player_summary(name, tag)
    # Direct access (robust)
    tier = summary['soloRank']['tier']
    rank = summary['soloRank']['rank']
    return f"{tier} {rank}"
```

### Example 2: Champion Analysis
```python
# BEFORE (v1.0)
async def analyze_champions(name: str, tag: str):
    champs_str = await get_top_champions_tool(name, tag, count=5)
    # Manual parsing: "- Amumu: Level 39, 485781 pts"
    lines = champs_str.split("\n")
    for line in lines:
        parts = line.split(": ")
        champ_info = parts[1].split(", ")
        # Complex string manipulation...

# AFTER (v2.0)
async def analyze_champions(name: str, tag: str):
    result = await lol_get_top_champions(name, tag, count=5)
    # Direct access to structured data
    for champ in result['topChampions']:
        print(f"{champ['champion']}: Level {champ['level']}, {champ['points']} pts")
        # Simple and clear
```

### Example 3: Match Details
```python
# BEFORE (v1.0)
async def get_match_info(match_id: str, puuid: str):
    details = await get_match_summary(match_id, puuid)
    # Details already a dict, but limited fields
    return {
        "kda": details.get("kda"),
        "damage": details.get("totalDamageDealtToChampions"),
    }

# AFTER (v2.0)
async def get_match_info(match_id: str, puuid: str):
    details = await lol_get_match_details(match_id, puuid)
    # Enriched with calculated metrics
    return {
        "kda": details["kda"]["ratio"],
        "csPerMinute": details["cs"]["csPerMinute"],
        "visionScore": details["vision"]["visionScore"],
        "damageDealtChamps": details["damage"]["totalDamageDealtToChampions"],
        "damagePerMinute": (
            details["damage"]["totalDamageDealtToChampions"] / 
            (details["gameDuration"]["minutes"] or 1)
        ),
    }
```

---

## 📊 Migration Checklist

### Pre-Migration
- [ ] Read this entire guide
- [ ] Review TOOLS_REFERENCE.md for new tool signatures
- [ ] Check EXAMPLES.md for code patterns
- [ ] Backup your current code
- [ ] Make sure you understand your current usage

### During Migration
- [ ] Update one tool at a time
- [ ] Test each change thoroughly
- [ ] Run all existing tests
- [ ] Update comments/docstrings
- [ ] Verify output format changes

### Post-Migration
- [ ] All tests pass
- [ ] No performance regressions
- [ ] Documentation updated
- [ ] Team aware of changes
- [ ] Can roll back if needed

---

## ⚠️ Breaking Changes (None!)

**Important:** There are **NO breaking changes**. All existing code continues to work.

### What's NOT Changing
- `get_player_summary()` - Works identically
- `get_top_champions_tool()` - Works identically
- `get_recent_matches_tool()` - Works identically
- `get_champion_mastery_tool()` - Works identically
- `get_match_summary()` - Works identically

### What's Being Added
- 10 new `lol_get_*` tools (structured JSON responses)
- 2 new `tft_get_*` tools (TFT support)
- Additional capabilities (ladder, spectator, challenges)

---

## 🔄 Version Compatibility

### Running Multiple Versions
**v1.0 and v2.0 can coexist:**
```python
# v1.0 compatibility layer (still works)
summary_string = await get_player_summary("Name", "Tag")

# v2.0 new tools (added in parallel)
summary_json = await lol_get_player_summary("Name", "Tag")

# Both work simultaneously!
```

---

## 📈 Performance Considerations

### v1.0 Performance
- Basic stats: ~500ms
- Recent matches: ~1-2 seconds

### v2.0 Performance
- **Identical** for existing tools (backward compatible)
- New tools: ~200-500ms (efficient implementation)
- TFT tools: ~500-1000ms (new feature)

### Optimization Tips
```python
# Use async/await for concurrent requests
summaries = await asyncio.gather(
    lol_get_player_summary("Player1", "Tag1"),
    lol_get_player_summary("Player2", "Tag2"),
    lol_get_player_summary("Player3", "Tag3"),
)
# Fetches all 3 concurrently, ~1 second total instead of 3 seconds
```

---

## 🎓 Learning Resources

### For Learning New Tools
1. Start with TOOLS_REFERENCE.md
2. Review relevant examples in EXAMPLES.md
3. Try one new tool at a time
4. Compare old vs new in your own code

### Recommended Reading Order
1. This file (migration guide) ← You are here
2. TOOLS_REFERENCE.md (quick reference)
3. EXAMPLES.md (copy-paste ready code)
4. ARCHITECTURE.md (how it works internally)

---

## ❓ FAQ

### Q: Will my existing code break?
**A:** No. All existing tools work identically.

### Q: Should I migrate to v2.0?
**A:** Not required, but recommended for new code. New tools provide better data access and new features.

### Q: Can I use both old and new tools together?
**A:** Yes! Mix and match as needed during migration.

### Q: What about error handling?
**A:** v2.0 has improved error handling, but old tools maintain same behavior.

### Q: Is there a performance difference?
**A:** No significant difference. Both are fast (~200-1000ms per request).

### Q: How do I roll back?
**A:** You can't accidentally break anything. Your old code still works.

### Q: What about the TFT tools?
**A:** Completely new - not in v1.0. No migration needed, just add new features.

---

## 🚀 Next Steps

### If You Want to Stay on v1.0
1. Continue using existing tools
2. Your code works unchanged
3. No action required

### If You Want to Gradually Adopt v2.0
1. Read EXAMPLES.md
2. Start with one new tool
3. Integrate into your workflow
4. Migrate at your own pace

### If You Want New Features (TFT, Ladder, etc.)
1. Use new `lol_get_*` and `tft_get_*` tools
2. These weren't available in v1.0
3. Add to existing codebase alongside old tools

---

## 📝 Example: Migration in Action

### Original Code (v1.0)
```python
async def report_player_stats(name: str, tag: str):
    summary = await get_player_summary(name, tag)
    champions = await get_top_champions_tool(name, tag, count=5)
    matches = await get_recent_matches_tool(name, tag, count=10)
    
    # Complex string parsing
    print(summary)
    print(champions)
    print(matches)
```

### Migrated Code (v2.0)
```python
async def report_player_stats(name: str, tag: str):
    summary = await lol_get_player_summary(name, tag)
    champions = await lol_get_top_champions(name, tag, count=5)
    matches = await lol_get_recent_matches(name, tag, count=10)
    
    # Clean structured data access
    print(f"Level: {summary['level']}")
    print(f"Rank: {summary['soloRank']['tier']}")
    print(f"Main: {champions['topChampions'][0]['champion']}")
    print(f"Recent WR: {sum(1 for m in matches['recentMatches'] if m['result'] == 'Win')} / 10")
    
    # NEW: Add TFT stats (wasn't possible before)
    tft = await tft_get_player_summary(name, tag)
    print(f"TFT Rank: {tft['tftRank']['tier']}")
```

---

## 🎯 Success Metrics

### Migration Complete When:
- ✅ All new tests pass
- ✅ Performance acceptable (~200-1000ms per request)
- ✅ Error handling robust
- ✅ Team familiar with new tools
- ✅ Documentation updated
- ✅ Future features easier to add

---

## 📞 Support

### Issues During Migration?
1. Check TROUBLESHOOTING.md (next document)
2. Review EXAMPLES.md for similar patterns
3. Check TOOLS_REFERENCE.md for tool signatures
4. Verify API key and region settings

---

**Last Updated:** 2025-01-02  
**Version:** 2.0.0  
**Migration Difficulty:** ⭐ Easy (optional, fully backward compatible)
