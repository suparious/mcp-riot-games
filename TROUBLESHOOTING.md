# Riot Games API MCP Tool - Troubleshooting Guide

## 🔧 Common Issues & Solutions

---

## 🚀 Startup Issues

### Issue 1: "ModuleNotFoundError: No module named 'mcp'"
**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Activate virtual environment
cd /home/shaun/repos/mcp-riot
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
# or (if using uv)
uv sync
```

**Verify:**
```bash
python -c "import mcp; print(mcp.__version__)"
```

---

### Issue 2: "RIOT_API_KEY is not set in the environment variables"
**Cause:** .env file missing or API key not configured

**Solution:**
```bash
# Check if .env exists
ls -la /home/shaun/repos/mcp-riot/.env

# If not, create it
cp /home/shaun/repos/mcp-riot/.env.example /home/shaun/repos/mcp-riot/.env

# Edit .env and add your API key
nano /home/shaun/repos/mcp-riot/.env

# Should look like:
# RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Get API Key:**
1. Visit https://developer.riotgames.com/
2. Sign in / Create account
3. Create new API key
4. Copy the key
5. Paste into .env file

---

### Issue 3: "Connection refused" when starting server
**Cause:** Port already in use or firewall blocking

**Solution:**
```bash
# Check if port is in use
lsof -i :8000  # or whatever port is configured

# Kill existing process
kill -9 <PID>

# Try again
python src/server.py
```

---

## 🔍 API Request Issues

### Issue 4: "Failed to find player"
**Cause:** Player name/tag not found or typo in game name

**Solution:**
```python
# Check exact spelling in League client
# Format: "Game Name#Tag" (case-sensitive for tag)

# Correct format examples:
await lol_get_player_summary("Tyler1", "NA1")
await lol_get_player_summary("Doublelift", "NA1")
await lol_get_player_summary("Doinb", "CN2")  # Different regions use different tags

# Common mistakes:
❌ await lol_get_player_summary("tyler1", "na1")  # Should be "NA1" (uppercase)
❌ await lol_get_player_summary("Tyler1", "Tyler1")  # Tag ≠ name
✅ await lol_get_player_summary("Tyler1", "NA1")
```

**Find Correct Format:**
```python
# Check player profile on op.gg or league.gg
# The tag is shown after # in their name
```

---

### Issue 5: "Champion 'XYZ' not found"
**Cause:** Champion name misspelled or incorrect format

**Solution:**
```python
# Use EXACT champion name (case-insensitive matching)
# Check valid names:

Valid:
✅ "Amumu", "Lee Sin", "Ahri", "Yone", "K'Sante"

Invalid:
❌ "amumu" → ✅ Works (case-insensitive)
❌ "Amu" → ❌ Incomplete name
❌ "Lee" → ❌ Incomplete (use "Lee Sin")
❌ "Kassadin" → ❌ Check exact spelling

# Check champion list at:
# https://ddragon.leagueoflegends.com/en/latest/champion.json
```

---

### Issue 6: "Could not retrieve [data]"
**Cause:** API is returning data but in unexpected format, or player has no data

**Solution:**
```python
# Check if player exists first
result = await lol_get_player_summary("Name", "Tag")
if "error" in result:
    print(f"Player not found: {result['error']}")
    return

# Check if specific data is available
if result.get("soloRank") is None:
    print("Player hasn't played ranked solo yet")

# Try different platform
result = await lol_get_player_summary("Name", "Tag", platform="euw")
```

---

### Issue 7: {"error": "Forbidden"} or 403 response
**Cause:** API key invalid, expired, or rate limited

**Solution:**
```bash
# Check API key validity
echo $RIOT_API_KEY  # Should show your key

# Get new API key from developer portal
# https://developer.riotgames.com/

# Check rate limits
# Riot's rate limiting: 20 requests per 1 second, 100 requests per 2 minutes
# If you hit limits, add delay:

import asyncio
await asyncio.sleep(1)  # Wait 1 second between requests

# Verify the key is correct
# Copy from developer portal
# Paste into .env
# Restart the server
```

---

### Issue 8: Timeout errors (30 second timeout)
**Cause:** API is slow or network is slow

**Solution:**
```python
# API was slow, retry automatically happens

# If persistent, try different endpoint
# Some endpoints are slower than others

# For batch requests, use concurrent async:
import asyncio

async def get_multiple(players):
    # Concurrent (fast)
    return await asyncio.gather(*[
        lol_get_player_summary(name, tag) 
        for name, tag in players
    ])
    
# vs

async def get_multiple_slow(players):
    # Sequential (slow)
    results = []
    for name, tag in players:
        results.append(await lol_get_player_summary(name, tag))
    return results
```

---

## 📊 Data Issues

### Issue 9: Match history shows no matches
**Cause:** Player is new or plays rarely

**Solution:**
```python
# Check if player has played any matches
result = await lol_get_recent_matches("Name", "Tag", count=100)

if len(result['recentMatches']) == 0:
    print("No matches found - player might be new")

# Try requesting more matches
result = await lol_get_recent_matches("Name", "Tag", count=50)

# Check if they play in different region
result = await lol_get_recent_matches("Name", "Tag", platform="euw", count=50)
```

---

### Issue 10: Rank shows as None or missing
**Cause:** Player hasn't played ranked this season

**Solution:**
```python
result = await lol_get_player_summary("Name", "Tag")

if result.get("soloRank") is None:
    print("Player hasn't played Solo Queue ranked")

if result.get("flexRank") is None:
    print("Player hasn't played Flex ranked")

# They might have played Clash or Tournaments instead
# Check challenges instead
challenges = await lol_get_challenges("Name", "Tag")
```

---

### Issue 11: Match details show zero damage
**Cause:** Player might have AFK'd or left game early

**Solution:**
```python
details = await lol_get_match_details(match_id, puuid)

# Check game duration - if very short, they probably left
duration = details['gameDuration']['minutes']
if duration < 5:
    print("Game ended very early - likely early FF")

# Check damage - 0 damage means they didn't play
damage = details['damage']['totalDamageDealtToChampions']
if damage == 0:
    print("Player was likely AFK")
```

---

### Issue 12: TFT data unavailable for player
**Cause:** Player hasn't played TFT or new account

**Solution:**
```python
result = await tft_get_player_summary("Name", "Tag")

if "error" in result:
    print("TFT data not available")
    # Try different region
    result = await tft_get_player_summary("Name", "Tag", platform="euw")

if result.get("tftRank") is None:
    print("Player hasn't played TFT ranked yet")
```

---

## 🌍 Region Issues

### Issue 13: "Account not found" error
**Cause:** Using wrong platform code or player on different region

**Solution:**
```python
# Supported platforms
platforms = ["na", "euw", "kr", "br", "las", "lan", "ru", "tr", "jp", "oc", "pbe"]

# Try each until one works
for platform in platforms:
    result = await lol_get_player_summary("Name", "Tag", platform=platform)
    if "error" not in result:
        print(f"Found player on {platform}")
        break

# Or check player's actual region first
# Look on op.gg or leagueofgraphs.com
```

---

### Issue 14: Getting different data for same player in different regions
**Cause:** Same account name on multiple regions (not linked)

**Solution:**
```python
# Each region is separate
# "Faker" on KR is different from "Faker" on NA

result_kr = await lol_get_player_summary("Faker", "NA", platform="kr")
result_na = await lol_get_player_summary("Faker", "NA", platform="na")

# Different PUUIDs = different accounts
if result_kr['puuid'] != result_na['puuid']:
    print("These are different accounts")
```

---

## 💾 Data Format Issues

### Issue 15: Can't parse JSON response
**Cause:** Response format different than expected

**Solution:**
```python
import json

result = await lol_get_player_summary("Name", "Tag")

# Check what you actually got
print(type(result))  # Should be dict
print(json.dumps(result, indent=2))  # Pretty print

# Check for errors first
if isinstance(result, dict) and "error" in result:
    print(f"Error: {result['error']}")
    return

# Now safe to access
if isinstance(result, dict):
    level = result.get('level')
```

---

### Issue 16: KeyError when accessing nested data
**Cause:** Data might be None or missing

**Solution:**
```python
result = await lol_get_player_summary("Name", "Tag")

# Safe access using .get()
❌ tier = result['soloRank']['tier']  # KeyError if soloRank is None

✅ tier = result.get('soloRank', {}).get('tier')  # Returns None safely

# Or check first
if result.get('soloRank'):
    tier = result['soloRank']['tier']
else:
    print("No rank data")
```

---

### Issue 17: Inconsistent field names
**Cause:** Using wrong field name from docs

**Solution:**
```python
# Check TOOLS_REFERENCE.md for exact field names
# camelCase is used consistently

result = await lol_get_player_summary("Name", "Tag")

# Correct names:
✅ result['gameName']      # Not 'name' or 'game_name'
✅ result['tagLine']       # Not 'tag' or 'tag_line'
✅ result['soloRank']      # Not 'rank' or 'solo_rank'
✅ result['topChampions']  # Not 'champions' or 'top_champs'

# Print available keys to verify
print(result.keys())
```

---

## 🔄 Integration Issues

### Issue 18: Tool not available in Claude Desktop
**Cause:** Server not running or MCP not registered

**Solution:**
```bash
# Make sure server is running
ps aux | grep "python.*server.py"

# If not running, start it
cd /home/shaun/repos/mcp-riot
python src/server.py

# Restart Claude Desktop
# Cmd+Q on Mac, or close on Windows

# Reopen Claude Desktop

# Check settings → MCP Server
# Should show "riot" as connected
```

---

### Issue 19: MCP shows "riot" tool but functions don't work
**Cause:** Server crashed after starting or code has errors

**Solution:**
```bash
# Check for syntax errors
python -m py_compile src/server.py

# If it compiles OK, check for runtime errors
python src/server.py

# Watch console output for errors
# Try calling a tool and check console

# If error, fix in src/server.py
# Save file
# Restart Claude Desktop
```

---

### Issue 20: Old tools still show in Claude but new tools don't
**Cause:** Cache not refreshed or server not reloaded

**Solution:**
```bash
# Restart Claude Desktop completely
# This refreshes the MCP connection

# Or manually restart the MCP server:
# 1. Stop the running server (Ctrl+C)
# 2. Wait 5 seconds
# 3. Start it again: python src/server.py
# 4. Restart Claude
```

---

## 🐛 Performance Issues

### Issue 21: Requests are very slow (>5 seconds)
**Cause:** Network latency or API overload

**Solution:**
```python
import time

start = time.time()
result = await lol_get_player_summary("Name", "Tag")
end = time.time()

print(f"Request took {end - start:.2f} seconds")

# Normal times:
# Player summary: 0.5-1.0s
# Recent matches: 1-2s
# Match details: 0.2-0.5s

# If slower, check:
# 1. Internet connection
# 2. API status: https://developer.riotgames.com/apis#lol-status
# 3. Retry after a few seconds
```

---

### Issue 22: Getting rate limited
**Cause:** Too many requests too fast

**Solution:**
```python
import asyncio

# Add delays between requests
async def get_players_slowly(players):
    results = []
    for name, tag in players:
        result = await lol_get_player_summary(name, tag)
        results.append(result)
        await asyncio.sleep(0.5)  # Wait 500ms between requests
    return results

# Or use concurrent with fewer workers
async def get_players_batched(players, batch_size=3):
    results = []
    for i in range(0, len(players), batch_size):
        batch = players[i:i+batch_size]
        batch_results = await asyncio.gather(*[
            lol_get_player_summary(name, tag)
            for name, tag in batch
        ])
        results.extend(batch_results)
        await asyncio.sleep(1)  # Wait 1s between batches
    return results
```

---

## 📋 Diagnostic Checklist

Use this to troubleshoot any issue:

- [ ] API key is valid (check at developer.riotgames.com)
- [ ] .env file exists and is readable
- [ ] Virtual environment is activated
- [ ] All dependencies are installed (pip list)
- [ ] Server is running (no errors in console)
- [ ] Player name/tag is spelled correctly
- [ ] Region code is correct (na, euw, kr, etc.)
- [ ] Network connection is working
- [ ] Firewall allows outgoing HTTPS
- [ ] API status is OK (https://developer.riotgames.com/apis#lol-status)

---

## 🆘 Getting More Help

### Check Documentation
1. TOOLS_REFERENCE.md - Tool parameters
2. EXAMPLES.md - Working examples
3. ARCHITECTURE.md - How it works
4. MIGRATION.md - Upgrading guide

### Debug Output
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed request logs
```

### Contact Riot Support
- Report API issues: https://developer.riotgames.com/apis#lol-status
- Check status page for incidents

### Check Your Setup
```bash
# Verify everything
python -c "
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('RIOT_API_KEY')
print(f'API Key set: {bool(api_key)}')
print(f'Key format: {api_key[:20] if api_key else None}...')
"
```

---

## 📞 Quick Reference Errors

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| ModuleNotFoundError | Virtual env not active | `source .venv/bin/activate` |
| "API_KEY not set" | .env missing | Create .env with API key |
| "Failed to find player" | Wrong name/tag | Check spelling, use correct format |
| "Champion not found" | Wrong champ name | Check exact champion name |
| 403 Forbidden | Invalid API key | Get new key from developer portal |
| Timeout | API slow | Retry, check network |
| No data | Player new | Try different region |
| Tool not showing | Server not running | Start server, restart Claude |
| Slow requests | Rate limited | Add delays between requests |

---

**Last Updated:** 2025-01-02  
**Version:** 2.0.0  
**Last Reviewed:** 2025-01-02
