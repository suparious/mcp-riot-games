from mcp.server.fastmcp import FastMCP
import httpx
import os
from typing import Any, Literal
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

mcp = FastMCP("riot")

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise EnvironmentError("RIOT_API_KEY is not set in the environment variables.")

# ============================================================================
# CONSTANTS & TYPE DEFINITIONS
# ============================================================================

# Platform routing for platform-specific endpoints (summoner, league, etc.)
PLATFORM_ROUTING = {
    "na": "na1",
    "euw": "euw1",
    "kr": "kr",
    "br": "br1",
    "las": "la1",
    "lan": "la2",
    "ru": "ru",
    "tr": "tr1",
    "jp": "jp1",
    "oc": "oc1",
    "pbe": "pbe1",
}

# Regional routing for regional endpoints (match, summoner, clash, etc.)
REGIONAL_ROUTING = {
    "americas": "americas",
    "europe": "europe",
    "asia-pacific": "asia-pacific",
    "sea": "sea",
}

# VALORANT region mapping
VALORANT_REGIONS = {
    "na": "na",
    "euw": "eu",
    "kr": "ap",
    "br": "br",
    "las": "latam",
    "lan": "latam",
}

# Map platform to region for cases where both are needed
PLATFORM_TO_REGION = {
    "na": "americas",
    "br": "americas",
    "las": "americas",
    "lan": "americas",
    "euw": "europe",
    "kr": "asia-pacific",
    "jp": "asia-pacific",
    "oc": "asia-pacific",
    "ru": "europe",
    "tr": "europe",
    "pbe": "americas",
}

# Champion cache
CHAMPION_MAP: dict[str, dict[int, str]] = {}

# ============================================================================
# HELPER FUNCTIONS - API REQUESTS
# ============================================================================


async def riot_request(
    url: str,
    platform_routing: str = "na1",
    params: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any] | list[Any] | None:
    """Make a request to the Riot API using platform routing (na1, euw1, kr, etc.)"""
    headers = {
        "X-Riot-Token": RIOT_API_KEY,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            full_url = f"https://{platform_routing}.api.riotgames.com{url}"
            res = await client.get(full_url, headers=headers, params=params, timeout=timeout)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Riot API Error ({e.response.status_code}): {e}")
            return None
        except Exception as e:
            print(f"Riot API Error: {e}")
            return None


async def riot_regional_request(
    url: str,
    regional_routing: str = "americas",
    params: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any] | list[Any] | None:
    """Make a request to the Riot API using regional routing"""
    headers = {
        "X-Riot-Token": RIOT_API_KEY,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            full_url = f"https://{regional_routing}.api.riotgames.com{url}"
            res = await client.get(full_url, headers=headers, params=params, timeout=timeout)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Riot API Error ({e.response.status_code}): {e}")
            return None
        except Exception as e:
            print(f"Riot API Error: {e}")
            return None


# ============================================================================
# HELPER FUNCTIONS - ACCOUNT & AUTHENTICATION
# ============================================================================


async def get_puuid(game_name: str, tag_line: str) -> str | None:
    """Get PUUID from game name and tag line (Riot Account)"""
    url = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    result = await riot_regional_request(url, regional_routing="americas")
    return result.get("puuid") if result else None


async def get_riot_account(game_name: str, tag_line: str) -> dict[str, Any] | None:
    """Get full Riot account info"""
    url = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    return await riot_regional_request(url, regional_routing="americas")


# ============================================================================
# HELPER FUNCTIONS - CHAMPIONS & DATA
# ============================================================================


async def get_champion_map(language: str = "en_US") -> dict[int, str]:
    """Get champion ID to name mapping"""
    if language in CHAMPION_MAP:
        return CHAMPION_MAP[language]

    try:
        async with httpx.AsyncClient() as client:
            version_res = await client.get("https://ddragon.leagueoflegends.com/api/versions.json")
            version = version_res.json()[0]
            champ_res = await client.get(
                f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{language}/champion.json"
            )
            data = champ_res.json()["data"]
            CHAMPION_MAP[language] = {int(c["key"]): c["name"] for c in data.values()}
            return CHAMPION_MAP[language]
    except Exception as e:
        print(f"Error fetching champion map: {e}")
        return {}


# ============================================================================
# HELPER FUNCTIONS - LEAGUE OF LEGENDS
# ============================================================================


async def get_summoner_by_puuid(puuid: str, platform: str = "na") -> dict[str, Any] | None:
    """Get summoner info by PUUID"""
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    return await riot_request(f"/lol/summoner/v4/summoners/by-puuid/{puuid}", platform_routing=platform_routing)


async def get_rank_by_puuid(puuid: str, platform: str = "na") -> dict[str, Any] | list[dict] | None:
    """Get rank data by PUUID"""
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    return await riot_request(f"/lol/league/v4/entries/by-puuid/{puuid}", platform_routing=platform_routing)


async def get_top_champions(
    puuid: str, champ_map: dict[int, str], count: int = 3, platform: str = "na"
) -> list[dict[str, Any]]:
    """Get top champions for player"""
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    mastery_data = await riot_request(
        f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top",
        platform_routing=platform_routing,
        params={"count": count},
    )
    if not mastery_data:
        return []

    return [
        {
            "champion": champ_map.get(c["championId"], f"ID({c['championId']})"),
            "championId": c["championId"],
            "level": c["championLevel"],
            "points": c["championPoints"],
        }
        for c in mastery_data
    ]


# ============================================================================
# LEAGUE OF LEGENDS - PLAYER & RANK TOOLS
# ============================================================================


@mcp.tool()
async def lol_get_player_summary(
    game_name: str,
    tag_line: str,
    platform: str = "na",
    language: str = "en_US",
) -> dict[str, Any]:
    """
    🧾 Get a complete League of Legends player profile summary.

    Returns: level, solo rank, flex rank, top champions, recent matches, and challenge progress.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    champ_map = await get_champion_map(language)
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")

    summoner = await get_summoner_by_puuid(puuid, platform)
    if not summoner:
        return {"error": "Failed to get summoner profile"}

    rank_data = await get_rank_by_puuid(puuid, platform)
    solo_rank = None
    flex_rank = None

    if isinstance(rank_data, list):
        for entry in rank_data:
            if entry.get("queueType") == "RANKED_SOLO_5x5":
                solo_rank = entry
            elif entry.get("queueType") == "RANKED_FLEX_SR":
                flex_rank = entry

    top_champs = await get_top_champions(puuid, champ_map, count=5, platform=platform)

    # Get recent matches
    match_ids = await riot_regional_request(
        f"/lol/match/v5/matches/by-puuid/{puuid}/ids",
        regional_routing=regional_routing,
        params={"count": 10},
    )

    recent_matches = []
    if match_ids:
        for match_id in match_ids[:5]:  # Limit to 5 for summary
            match = await riot_regional_request(f"/lol/match/v5/matches/{match_id}", regional_routing=regional_routing)
            if match:
                participant = next((p for p in match["info"]["participants"] if p["puuid"] == puuid), None)
                if participant:
                    recent_matches.append(
                        {
                            "matchId": match_id,
                            "champion": participant["championName"],
                            "kda": f"{participant['kills']}/{participant['deaths']}/{participant['assists']}",
                            "result": "Win" if participant["win"] else "Loss",
                            "position": participant.get("teamPosition", "UNKNOWN"),
                        }
                    )

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "level": summoner.get("summonerLevel"),
        "soloRank": {
            "tier": solo_rank.get("tier"),
            "rank": solo_rank.get("rank"),
            "lp": solo_rank.get("leaguePoints"),
            "wins": solo_rank.get("wins"),
            "losses": solo_rank.get("losses"),
            "winRate": round(solo_rank.get("wins", 0) / (solo_rank.get("wins", 0) + solo_rank.get("losses", 1)) * 100)
            if solo_rank
            else None,
        }
        if solo_rank
        else None,
        "flexRank": {
            "tier": flex_rank.get("tier"),
            "rank": flex_rank.get("rank"),
            "lp": flex_rank.get("leaguePoints"),
            "wins": flex_rank.get("wins"),
            "losses": flex_rank.get("losses"),
            "winRate": round(flex_rank.get("wins", 0) / (flex_rank.get("wins", 0) + flex_rank.get("losses", 1)) * 100)
            if flex_rank
            else None,
        }
        if flex_rank
        else None,
        "topChampions": top_champs,
        "recentMatches": recent_matches,
    }


@mcp.tool()
async def lol_get_top_champions(
    game_name: str, tag_line: str, platform: str = "na", language: str = "en_US", count: int = 5
) -> dict[str, Any]:
    """
    🔝 Get a League of Legends player's top champion masteries.

    Returns the player's most-played champions ranked by mastery points.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    champ_map = await get_champion_map(language)
    top_champs = await get_top_champions(puuid, champ_map, count=count, platform=platform)

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "topChampions": top_champs,
    }


@mcp.tool()
async def lol_get_recent_matches(
    game_name: str, tag_line: str, platform: str = "na", count: int = 10
) -> dict[str, Any]:
    """
    🕹️ Get a League of Legends player's recent match history.

    Returns brief summaries of recent matches including champion, KDA, and outcome.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")
    match_ids = await riot_regional_request(
        f"/lol/match/v5/matches/by-puuid/{puuid}/ids", regional_routing=regional_routing, params={"count": count}
    )

    if not match_ids:
        return {"gameName": game_name, "tagLine": tag_line, "puuid": puuid, "recentMatches": []}

    matches = []
    for match_id in match_ids:
        match = await riot_regional_request(f"/lol/match/v5/matches/{match_id}", regional_routing=regional_routing)
        if match:
            participant = next((p for p in match["info"]["participants"] if p["puuid"] == puuid), None)
            if participant:
                matches.append(
                    {
                        "matchId": match_id,
                        "champion": participant["championName"],
                        "kills": participant["kills"],
                        "deaths": participant["deaths"],
                        "assists": participant["assists"],
                        "kda": f"{participant['kills']}/{participant['deaths']}/{participant['assists']}",
                        "position": participant.get("teamPosition", "UNKNOWN"),
                        "lane": participant.get("lane", "UNKNOWN"),
                        "result": "Win" if participant["win"] else "Loss",
                        "gold": participant.get("goldEarned"),
                        "cs": participant.get("totalMinionsKilled", 0) + participant.get("neutralMinionsKilled", 0),
                    }
                )

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "recentMatches": matches,
    }


@mcp.tool()
async def lol_get_champion_mastery(
    game_name: str, tag_line: str, champion_name: str, platform: str = "na", language: str = "en_US"
) -> dict[str, Any]:
    """
    🎯 Get detailed League of Legends champion mastery information.

    Returns mastery level, points, last play time, progression, and milestone data.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    champion_map = await get_champion_map(language)
    champion_id = next((cid for cid, name in champion_map.items() if name.lower() == champion_name.lower()), None)
    if not champion_id:
        return {"error": f"Champion '{champion_name}' not found"}

    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    mastery = await riot_request(
        f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}",
        platform_routing=platform_routing,
    )
    if not mastery:
        return {"error": f"Could not find mastery data for {champion_name}"}

    # Convert Unix timestamp to readable format
    last_play_time = None
    if mastery.get("lastPlayTime"):
        last_play_time = datetime.fromtimestamp(mastery["lastPlayTime"] / 1000).isoformat()

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "championName": champion_name,
        "championId": champion_id,
        "level": mastery.get("championLevel"),
        "points": mastery.get("championPoints"),
        "pointsSinceLastLevel": mastery.get("championPointsSinceLastLevel"),
        "pointsUntilNextLevel": mastery.get("championPointsUntilNextLevel"),
        "lastPlayTime": last_play_time,
        "tokensEarned": mastery.get("tokensEarned"),
        "chestGranted": mastery.get("chestGranted"),
        "nextMilestone": mastery.get("nextSeasonMilestone"),
    }


@mcp.tool()
async def lol_get_match_details(
    match_id: str, puuid: str, platform: str = "na"
) -> dict[str, Any]:
    """
    📊 Get detailed League of Legends match statistics.

    Returns comprehensive stats including KDA, damage, vision, gold, CS, and more.
    """
    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")
    match = await riot_regional_request(f"/lol/match/v5/matches/{match_id}", regional_routing=regional_routing)
    if not match:
        return {"error": "Failed to load match data"}

    participant = next((p for p in match["info"]["participants"] if p["puuid"] == puuid), None)
    if not participant:
        return {"error": f"No participant found with puuid: {puuid}"}

    game_duration_seconds = match["info"]["gameDuration"]
    game_duration_minutes = game_duration_seconds / 60

    # Calculate CS per minute
    total_cs = participant.get("totalMinionsKilled", 0) + participant.get("neutralMinionsKilled", 0)
    cs_per_minute = round(total_cs / game_duration_minutes, 2) if game_duration_minutes > 0 else 0

    return {
        "matchId": match_id,
        "champion": participant["championName"],
        "position": participant.get("teamPosition", "UNKNOWN"),
        "lane": participant.get("lane", "UNKNOWN"),
        "role": participant.get("role", "UNKNOWN"),
        "result": "Win" if participant["win"] else "Loss",
        "kda": {
            "kills": participant["kills"],
            "deaths": participant["deaths"],
            "assists": participant["assists"],
            "ratio": participant["challenges"].get("kda", 0),
        },
        "damage": {
            "totalDamageDealtToChampions": participant.get("totalDamageDealtToChampions", 0),
            "totalDamageDealt": participant.get("totalDamageDealt", 0),
            "totalDamageTaken": participant.get("totalDamageTaken", 0),
            "damageDealtToObjectives": participant.get("damageDealtToObjectives", 0),
            "damageDealtToTurrets": participant.get("damageDealtToTurrets", 0),
        },
        "cs": {
            "minionsKilled": participant.get("totalMinionsKilled", 0),
            "neutralMinionsKilled": participant.get("neutralMinionsKilled", 0),
            "totalCs": total_cs,
            "csPerMinute": cs_per_minute,
        },
        "gold": {
            "goldEarned": participant.get("goldEarned", 0),
            "goldSpent": participant.get("goldSpent", 0),
        },
        "vision": {
            "visionScore": participant.get("visionScore", 0),
            "wardsPlaced": participant.get("wardsPlaced", 0),
            "wardsKilled": participant.get("wardsKilled", 0),
            "detectorWardsPlaced": participant.get("detectorWardsPlaced", 0),
        },
        "objectives": {
            "kills": participant.get("kills", 0),
            "turretKills": participant.get("turretKills", 0),
            "inhibitorKills": participant.get("inhibitorKills", 0),
            "dragonKills": participant.get("dragonKills", 0),
            "baronKills": participant.get("baronKills", 0),
        },
        "items": {
            "itemsBuilt": [
                participant.get(f"item{i}") for i in range(7) if participant.get(f"item{i}") != 0
            ],
        },
        "gameDuration": {"seconds": game_duration_seconds, "minutes": round(game_duration_minutes, 1)},
        "gameQueueId": match["info"]["queueId"],
        "gameMode": match["info"].get("gameMode", "UNKNOWN"),
    }


@mcp.tool()
async def lol_get_challenges(game_name: str, tag_line: str, platform: str = "na") -> dict[str, Any]:
    """
    🏆 Get League of Legends player challenge progress.

    Returns information about challenges the player is progressing through.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")
    challenges = await riot_regional_request(
        f"/lol/challenges/v1/player-data/{puuid}", regional_routing=regional_routing
    )

    if not challenges:
        return {"error": "Could not retrieve challenge data"}

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "totalPoints": challenges.get("totalPoints"),
        "categoryPoints": challenges.get("categoryPoints"),
        "challenges": challenges.get("challenges", []),
    }


@mcp.tool()
async def lol_get_league_entries(
    tier: Literal["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"],
    rank: Literal["I", "II", "III", "IV"] | None = None,
    platform: str = "na",
    page: int = 1,
) -> dict[str, Any]:
    """
    📈 Get League of Legends ranked ladder entries.

    Returns players at a specific tier/rank. Pagination through pages.
    """
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    
    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        # These tiers don't have divisions
        url = f"/lol/league/v4/leagues/{tier.lower()}/by-queue/RANKED_SOLO_5x5"
    else:
        if not rank:
            rank = "I"  # Default to rank I
        url = f"/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{rank}"

    entries = await riot_request(
        url, platform_routing=platform_routing, params={"page": page}
    )

    if not entries:
        return {"error": "Could not retrieve league entries"}

    if isinstance(entries, dict):  # For master/grandmaster/challenger
        entries = entries.get("entries", [])

    return {
        "tier": tier,
        "rank": rank,
        "platform": platform,
        "page": page,
        "entries": [
            {
                "summonerId": e.get("summonerId"),
                "summonerName": e.get("summonerName"),
                "tier": e.get("tier"),
                "rank": e.get("rank"),
                "lp": e.get("leaguePoints"),
                "wins": e.get("wins"),
                "losses": e.get("losses"),
                "winRate": round(e.get("wins", 0) / (e.get("wins", 0) + e.get("losses", 1)) * 100) if e.get("wins") or e.get("losses") else 0,
            }
            for e in entries
        ],
    }


# ============================================================================
# LEAGUE OF LEGENDS - STATUS & SYSTEM TOOLS
# ============================================================================


@mcp.tool()
async def lol_get_server_status(platform: str = "na") -> dict[str, Any]:
    """
    📡 Get League of Legends server status and maintenance information.

    Returns platform status, incidents, and maintenance schedules.
    """
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    status = await riot_request(f"/lol/status/v4/platform-data", platform_routing=platform_routing)

    if not status:
        return {"error": "Could not retrieve server status"}

    return {
        "platform": platform,
        "platformId": status.get("id"),
        "platformName": status.get("name"),
        "maintenances": [
            {
                "id": m.get("id"),
                "title": next(
                    (t.get("content") for t in m.get("titles", []) if t.get("locale") == "en_US"),
                    m.get("titles", [{}])[0].get("content")
                ),
                "status": m.get("status"),
                "updatedAt": m.get("updated_at"),
                "archivedAt": m.get("archive_at"),
            }
            for m in status.get("maintenances", [])
        ],
        "incidents": [
            {
                "id": i.get("id"),
                "title": next(
                    (t.get("content") for t in i.get("titles", []) if t.get("locale") == "en_US"),
                    i.get("titles", [{}])[0].get("content")
                ),
                "status": i.get("status"),
            }
            for i in status.get("incidents", [])
        ],
    }


@mcp.tool()
async def lol_get_all_champions(language: str = "en_US") -> dict[str, Any]:
    """
    🎮 Get all League of Legends champion information.

    Returns champion list with details, abilities, and stats.
    """
    try:
        champ_map = await get_champion_map(language)
        async with httpx.AsyncClient() as client:
            version_res = await client.get("https://ddragon.leagueoflegends.com/api/versions.json")
            version = version_res.json()[0]
            champ_full_res = await client.get(
                f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{language}/champion.json"
            )
            data = champ_full_res.json()["data"]
            
            champions = []
            for champ_key, champ_data in data.items():
                champions.append({
                    "key": int(champ_data["key"]),
                    "id": champ_data["id"],
                    "name": champ_data["name"],
                    "title": champ_data["title"],
                    "tags": champ_data.get("tags", []),
                })
            
            return {
                "version": version,
                "totalChampions": len(champions),
                "champions": sorted(champions, key=lambda x: x["name"]),
            }
    except Exception as e:
        return {"error": f"Failed to fetch champion data: {str(e)}"}


@mcp.tool()
async def lol_get_clash_tournaments(platform: str = "na") -> dict[str, Any]:
    """
    🏆 Get League of Legends Clash tournament information.

    Returns ongoing and upcoming Clash tournaments.
    """
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    tournaments = await riot_request(f"/lol/clash/v1/tournaments", platform_routing=platform_routing)

    if tournaments is None:
        return {"error": "Could not retrieve tournament data"}

    return {
        "platform": platform,
        "tournaments": [
            {
                "id": t.get("id"),
                "themeId": t.get("themeId"),
                "schedule": [
                    {
                        "id": s.get("id"),
                        "registrationTime": s.get("registrationTime"),
                        "startTime": s.get("startTime"),
                        "cancelledTime": s.get("cancelledTime"),
                        "cancelled": s.get("cancelled"),
                    }
                    for s in t.get("schedule", [])
                ],
            }
            for t in tournaments
        ] if isinstance(tournaments, list) else [],
    }


# ============================================================================
# LEAGUE OF LEGENDS - SPECTATOR TOOLS
# ============================================================================


@mcp.tool()
async def lol_get_spectator(summoner_name: str, platform: str = "na") -> dict[str, Any]:
    """
    👁️ Get live League of Legends game data for a player.

    Returns current game info if player is in a match (champions, teams, etc).
    """
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    
    # Note: Spectator requires summoner ID, not PUUID
    spectator = await riot_request(
        f"/lol/spectator/v5/active-games/by-summoner/{summoner_name}",
        platform_routing=platform_routing,
    )

    if not spectator:
        return {"error": f"No active game found for {summoner_name}"}

    return {
        "gameName": summoner_name,
        "platform": platform,
        "gameType": spectator.get("gameType"),
        "gameQueueConfigId": spectator.get("gameQueueConfigId"),
        "gameStartTime": spectator.get("gameStartTime"),
        "participants": [
            {
                "championId": p.get("championId"),
                "teamId": p.get("teamId"),
                "summonerName": p.get("summonerName"),
            }
            for p in spectator.get("participants", [])
        ],
    }


# ============================================================================
# TEAM FIGHT TACTICS (TFT) TOOLS
# ============================================================================


async def get_tft_summoner(puuid: str, platform: str = "na") -> dict[str, Any] | None:
    """Get TFT summoner info by PUUID"""
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    return await riot_request(f"/tft/summoner/v1/summoners/by-puuid/{puuid}", platform_routing=platform_routing)


@mcp.tool()
async def tft_get_player_summary(game_name: str, tag_line: str, platform: str = "na") -> dict[str, Any]:
    """
    🎲 Get Team Fight Tactics player profile summary.

    Returns TFT rank, LP, recent matches, and key stats.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")

    # Get TFT summoner info
    summoner = await get_tft_summoner(puuid, platform)
    if not summoner:
        return {"error": "Failed to get TFT summoner data"}

    # Get TFT rank
    rank_data = await riot_request(
        f"/tft/league/v1/entries/by-puuid/{puuid}", platform_routing=platform_routing
    )

    rank_info = None
    if rank_data:
        if isinstance(rank_data, list) and len(rank_data) > 0:
            rank_info = rank_data[0]
        elif isinstance(rank_data, dict):
            rank_info = rank_data

    # Get recent TFT matches
    match_ids = await riot_regional_request(
        f"/tft/match/v1/matches/by-puuid/{puuid}/ids", regional_routing=regional_routing, params={"count": 10}
    )

    recent_matches = []
    if match_ids:
        for match_id in match_ids[:5]:
            match = await riot_regional_request(f"/tft/match/v1/matches/{match_id}", regional_routing=regional_routing)
            if match:
                participant = next((p for p in match["info"]["participants"] if p["puuid"] == puuid), None)
                if participant:
                    recent_matches.append(
                        {
                            "matchId": match_id,
                            "placement": participant.get("placement"),
                            "level": participant.get("level"),
                            "goldLeft": participant.get("gold_left"),
                            "totalDamageToPlayers": participant.get("total_damage_to_players"),
                        }
                    )

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "summonerId": summoner.get("id"),
        "tftRank": {
            "tier": rank_info.get("tier") if rank_info else None,
            "rank": rank_info.get("rank") if rank_info else None,
            "lp": rank_info.get("leaguePoints") if rank_info else None,
            "wins": rank_info.get("wins") if rank_info else None,
            "losses": rank_info.get("losses") if rank_info else None,
            "winRate": round(
                rank_info.get("wins", 0) / (rank_info.get("wins", 0) + rank_info.get("losses", 1)) * 100
            )
            if rank_info and (rank_info.get("wins") or rank_info.get("losses"))
            else None,
        }
        if rank_info
        else None,
        "recentMatches": recent_matches,
    }


@mcp.tool()
async def tft_get_recent_matches(game_name: str, tag_line: str, platform: str = "na", count: int = 10) -> dict[str, Any]:
    """
    🎲 Get recent Team Fight Tactics matches.

    Returns placement, composition, and performance data for recent matches.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")
    match_ids = await riot_regional_request(
        f"/tft/match/v1/matches/by-puuid/{puuid}/ids", regional_routing=regional_routing, params={"count": count}
    )

    if not match_ids:
        return {"gameName": game_name, "tagLine": tag_line, "puuid": puuid, "matches": []}

    matches = []
    for match_id in match_ids:
        match = await riot_regional_request(f"/tft/match/v1/matches/{match_id}", regional_routing=regional_routing)
        if match:
            participant = next((p for p in match["info"]["participants"] if p["puuid"] == puuid), None)
            if participant:
                matches.append(
                    {
                        "matchId": match_id,
                        "placement": participant.get("placement"),
                        "level": participant.get("level"),
                        "goldLeft": participant.get("gold_left"),
                        "totalDamageToPlayers": participant.get("total_damage_to_players"),
                        "traits": participant.get("traits", []),
                        "units": [
                            {
                                "characterId": u.get("character_id"),
                                "tier": u.get("tier"),
                                "itemNames": u.get("itemNames", []),
                            }
                            for u in participant.get("units", [])
                        ],
                    }
                )

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "matches": matches,
    }


@mcp.tool()
async def tft_get_server_status(platform: str = "na") -> dict[str, Any]:
    """
    📡 Get Team Fight Tactics server status.

    Returns TFT platform status and incidents.
    """
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    status = await riot_request(f"/tft/status/v1/platform-data", platform_routing=platform_routing)

    if not status:
        return {"error": "Could not retrieve TFT server status"}

    return {
        "platform": platform,
        "platformId": status.get("id"),
        "platformName": status.get("name"),
        "maintenances": [
            {
                "id": m.get("id"),
                "title": next(
                    (t.get("content") for t in m.get("titles", []) if t.get("locale") == "en_US"),
                    "Maintenance"
                ),
            }
            for m in status.get("maintenances", [])
        ],
        "incidents": [
            {
                "id": i.get("id"),
                "title": next(
                    (t.get("content") for t in i.get("titles", []) if t.get("locale") == "en_US"),
                    "Incident"
                ),
            }
            for i in status.get("incidents", [])
        ],
    }


@mcp.tool()
async def tft_get_spectator(summoner_name: str, platform: str = "na") -> dict[str, Any]:
    """
    👁️ Get live Team Fight Tactics game data for a player.

    Returns current TFT match info if player is playing.
    """
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    
    spectator = await riot_request(
        f"/tft/spectator/v5/active-games/by-summoner/{summoner_name}",
        platform_routing=platform_routing,
    )

    if not spectator:
        return {"error": f"No active TFT game found for {summoner_name}"}

    return {
        "gameName": summoner_name,
        "platform": platform,
        "gameType": spectator.get("gameType"),
        "participants": [
            {
                "summonerName": p.get("summonerName"),
                "teamId": p.get("teamId"),
            }
            for p in spectator.get("participants", [])
        ],
    }


# ============================================================================
# LEGENDS OF RUNETERRA (LOR) TOOLS
# ============================================================================


@mcp.tool()
async def lor_get_player_summary(game_name: str, tag_line: str, platform: str = "na") -> dict[str, Any]:
    """
    🃏 Get Legends of Runeterra player profile summary.

    Returns ranked tier, LP, and recent match data.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")

    # Get LOR ranked stats
    ranked = await riot_regional_request(
        f"/lor/ranked/v1/leaderboards/by-puuid/{puuid}", regional_routing=regional_routing
    )

    # Get recent LOR matches
    match_ids = await riot_regional_request(
        f"/lor/match/v1/matches/by-puuid/{puuid}/ids", regional_routing=regional_routing, params={"count": 10}
    )

    recent_matches = []
    if match_ids:
        for match_id in match_ids[:5]:
            match = await riot_regional_request(f"/lor/match/v1/matches/{match_id}", regional_routing=regional_routing)
            if match:
                participant = next((p for p in match["info"]["players"] if p["puuid"] == puuid), None)
                if participant:
                    recent_matches.append(
                        {
                            "matchId": match_id,
                            "placement": participant.get("placement"),
                            "factionId": participant.get("factionId"),
                            "deckCode": participant.get("deck_code"),
                        }
                    )

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "rankedStats": {
            "tier": ranked.get("tier") if ranked else None,
            "rank": ranked.get("rank") if ranked else None,
            "lp": ranked.get("leaguePoints") if ranked else None,
        } if ranked else None,
        "recentMatches": recent_matches,
    }


@mcp.tool()
async def lor_get_recent_matches(game_name: str, tag_line: str, platform: str = "na", count: int = 10) -> dict[str, Any]:
    """
    🃏 Get Legends of Runeterra recent matches.

    Returns player's recent match history with deck and placement data.
    """
    puuid = await get_puuid(game_name, tag_line)
    if not puuid:
        return {"error": "Failed to find player"}

    regional_routing = PLATFORM_TO_REGION.get(platform, "americas")
    match_ids = await riot_regional_request(
        f"/lor/match/v1/matches/by-puuid/{puuid}/ids", regional_routing=regional_routing, params={"count": count}
    )

    if not match_ids:
        return {"gameName": game_name, "tagLine": tag_line, "puuid": puuid, "matches": []}

    matches = []
    for match_id in match_ids:
        match = await riot_regional_request(f"/lor/match/v1/matches/{match_id}", regional_routing=regional_routing)
        if match:
            participant = next((p for p in match["info"]["players"] if p["puuid"] == puuid), None)
            if participant:
                matches.append(
                    {
                        "matchId": match_id,
                        "placement": participant.get("placement"),
                        "factionId": participant.get("factionId"),
                        "deckCode": participant.get("deck_code"),
                        "playerOrder": participant.get("player_order"),
                    }
                )

    return {
        "gameName": game_name,
        "tagLine": tag_line,
        "puuid": puuid,
        "matches": matches,
    }


@mcp.tool()
async def lor_get_server_status(platform: str = "na") -> dict[str, Any]:
    """
    📡 Get Legends of Runeterra server status.

    Returns LoR platform status and incidents.
    """
    platform_routing = PLATFORM_ROUTING.get(platform, "na1")
    status = await riot_request(f"/lor/status/v1/platform-data", platform_routing=platform_routing)

    if not status:
        return {"error": "Could not retrieve LoR server status"}

    return {
        "platform": platform,
        "platformId": status.get("id"),
        "platformName": status.get("name"),
    }


# ============================================================================
# VALORANT TOOLS
# ============================================================================


@mcp.tool()
async def valorant_get_player_by_name(
    player_name: str, tag_line: str, region: str = "na"
) -> dict[str, Any]:
    """
    🎯 Get VALORANT player account information by name and tag.

    Returns player PUUID and account details.
    """
    val_region = VALORANT_REGIONS.get(region, "na")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Riot-Token": RIOT_API_KEY}
            res = await client.get(
                f"https://{val_region}.api.riotgames.com/valorant/v1/player-lookups/by-riot-id/{player_name}/{tag_line}",
                headers=headers,
            )
            res.raise_for_status()
            player = res.json()
            return {
                "playerName": player_name,
                "tagLine": tag_line,
                "puuid": player.get("puuid"),
                "region": region,
            }
    except Exception as e:
        return {"error": f"Failed to find player: {str(e)}"}


@mcp.tool()
async def valorant_get_ranked_stats(
    player_name: str, tag_line: str, region: str = "na"
) -> dict[str, Any]:
    """
    🎯 Get VALORANT player ranked statistics.

    Returns ranked tier, RR points, and win/loss data.
    """
    val_region = VALORANT_REGIONS.get(region, "na")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Riot-Token": RIOT_API_KEY}
            # First get PUUID
            res = await client.get(
                f"https://{val_region}.api.riotgames.com/valorant/v1/player-lookups/by-riot-id/{player_name}/{tag_line}",
                headers=headers,
            )
            res.raise_for_status()
            puuid = res.json().get("puuid")
            
            # Get ranked stats
            res = await client.get(
                f"https://{val_region}.api.riotgames.com/valorant/v3/player_mmr/affinity/{region}/players/{puuid}",
                headers=headers,
            )
            if res.status_code == 404:
                return {"error": "Player ranked data not found"}
            
            res.raise_for_status()
            stats = res.json()
            
            return {
                "playerName": player_name,
                "tagLine": tag_line,
                "puuid": puuid,
                "tier": stats.get("tier"),
                "rrPoints": stats.get("rr_points"),
                "currentSeasonData": stats.get("current_season_data", {}),
            }
    except Exception as e:
        return {"error": f"Failed to retrieve ranked stats: {str(e)}"}


@mcp.tool()
async def valorant_get_match_history(
    player_name: str, tag_line: str, region: str = "na", count: int = 10
) -> dict[str, Any]:
    """
    🎯 Get VALORANT player recent match history.

    Returns recent matches with placement and stats.
    """
    val_region = VALORANT_REGIONS.get(region, "na")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Riot-Token": RIOT_API_KEY}
            # Get PUUID
            res = await client.get(
                f"https://{val_region}.api.riotgames.com/valorant/v1/player-lookups/by-riot-id/{player_name}/{tag_line}",
                headers=headers,
            )
            res.raise_for_status()
            puuid = res.json().get("puuid")
            
            # Get match history
            res = await client.get(
                f"https://{val_region}.api.riotgames.com/valorant/v3/match-history/{region}/players/{puuid}",
                headers=headers,
                params={"end_index": count},
            )
            res.raise_for_status()
            history = res.json()
            
            matches = [
                {
                    "matchId": m.get("matchid"),
                    "mapName": m.get("map"),
                    "teamWon": m.get("team_won"),
                    "customGameName": m.get("custom_game_name"),
                    "seasonId": m.get("season_id"),
                }
                for m in history.get("history", [])
            ]
            
            return {
                "playerName": player_name,
                "tagLine": tag_line,
                "puuid": puuid,
                "matches": matches,
            }
    except Exception as e:
        return {"error": f"Failed to retrieve match history: {str(e)}"}


@mcp.tool()
async def valorant_get_server_status(region: str = "na") -> dict[str, Any]:
    """
    📡 Get VALORANT server status.

    Returns VALORANT platform status and incidents.
    """
    val_region = VALORANT_REGIONS.get(region, "na")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Riot-Token": RIOT_API_KEY}
            res = await client.get(
                f"https://{val_region}.api.riotgames.com/val/status/v1/platform-data",
                headers=headers,
            )
            res.raise_for_status()
            status = res.json()
            
            return {
                "region": region,
                "platformId": status.get("id"),
                "platformName": status.get("name"),
                "maintenances": [
                    {
                        "id": m.get("id"),
                        "title": next(
                            (t.get("content") for t in m.get("titles", []) if t.get("locale") == "en_US"),
                            "Maintenance"
                        ),
                    }
                    for m in status.get("maintenances", [])
                ],
                "incidents": [
                    {
                        "id": i.get("id"),
                        "title": next(
                            (t.get("content") for t in i.get("titles", []) if t.get("locale") == "en_US"),
                            "Incident"
                        ),
                    }
                    for i in status.get("incidents", [])
                ],
            }
    except Exception as e:
        return {"error": f"Failed to retrieve server status: {str(e)}"}


# ============================================================================
# BACKWARDS COMPATIBILITY - ORIGINAL TOOLS
# ============================================================================


@mcp.tool()
async def get_top_champions_tool(game_name: str, tag_line: str, language: str = "en_US", count: int = 3) -> str:
    """
    🔝 Get the player's top champion masteries (LoL).

    Returns a list of the player's most-played champions based on mastery points.
    """
    result = await lol_get_top_champions(game_name, tag_line, platform="na", language=language, count=count)
    
    if "error" in result:
        return result["error"]
    
    lines = []
    for champ in result.get("topChampions", []):
        lines.append(f"- {champ['champion']}: Level {champ['level']}, {champ['points']} pts")
    return "\n".join(lines) if lines else "No champion data found."


@mcp.tool()
async def get_recent_matches_tool(game_name: str, tag_line: str, count: int = 3) -> str:
    """
    🕹️ Get the player's recent match history (LoL).

    Returns a brief summary of the player's most recent matches, including champion, score, and result.
    """
    result = await lol_get_recent_matches(game_name, tag_line, platform="na", count=count)
    
    if "error" in result:
        return result["error"]
    
    lines = []
    for match in result.get("recentMatches", []):
        lines.append(f"{match['matchId']} {match['champion']}: {match['kda']} - {match['result']}")
    return "\n".join(lines) if lines else "No recent matches found."


@mcp.tool()
async def get_champion_mastery_tool(
    game_name: str, tag_line: str, champion_name: str, language: str = "en_US"
) -> dict[str, Any] | str:
    """
    🎯 Get the player's mastery info for a specific champion (LoL).

    Returns detailed mastery data (level, points, last play time, etc.) for the requested champion.
    """
    return await lol_get_champion_mastery(game_name, tag_line, champion_name, platform="na", language=language)


@mcp.tool()
async def get_player_summary(game_name: str, tag_line: str, language: str = "en_US") -> str:
    """
    🧾 Get a complete summary of a player's profile (LoL).

    Includes level, solo rank, top champion masteries, and recent matches in a single output.
    """
    result = await lol_get_player_summary(game_name, tag_line, platform="na", language=language)
    
    if "error" in result:
        return result["error"]
    
    output = f"👤 {game_name} (Level {result.get('level')})\n"
    
    if result.get("soloRank"):
        solo = result["soloRank"]
        output += f"\n🏅 Rank: {solo.get('tier')} {solo.get('rank')} ({solo.get('lp')} LP) - {solo.get('wins')}W {solo.get('losses')}L ({solo.get('winRate')}% WR)\n"
    
    output += "\n🔥 Top Champions:\n"
    for champ in result.get("topChampions", []):
        output += f"- {champ['champion']}: Level {champ['level']}, {champ['points']} pts\n"
    
    output += "\n🕹️ Recent Matches:\n"
    for match in result.get("recentMatches", []):
        output += f"{match['matchId']} {match['champion']}: {match['kda']} - {match['result']}\n"
    
    return output


@mcp.tool()
async def get_match_summary(match_id: str, puuid: str) -> dict[str, Any] | str:
    """
    📊 Get a detailed summary of a specific match for a given player (LoL).

    Extracts and returns only the relevant stats (KDA, damage, vision, win/loss, etc.) from the match.
    """
    return await lol_get_match_details(match_id, puuid, platform="na")


if __name__ == "__main__":
    mcp.run()
