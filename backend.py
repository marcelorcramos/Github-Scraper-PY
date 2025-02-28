from fastapi import FastAPI, HTTPException, Query
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import httpx
import asyncio
import logging
import time

load_dotenv()

app = FastAPI()

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
api_call_count = 0
CACHE: Dict[str, dict] = {} 
CACHE_EXPIRY = 300  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepositoryInfo(BaseModel):
    name: str
    owner: str
    description: Optional[str]
    stars: int
    forks: int
    created_at: str
    updated_at: str
    last_commit: str
    link: str

async def make_graphql_request(query: str) -> dict:
    global api_call_count

    cache_key = f"graphql:{query}"
    if cache_key in CACHE:
        if time.time() - CACHE[cache_key]["timestamp"] < CACHE_EXPIRY:
            return CACHE[cache_key]["data"]

    github_token = os.getenv("GITHUB_TOKEN")
    logger.info("Making GraphQL API request")
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub token not found. Please check your .env file.")

    headers = {
        "Authorization": f"Bearer {github_token}"
    }
    api_call_count += 1

    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(GITHUB_GRAPHQL_URL, json={"query": query}, headers=headers)
            logger.info(f"GraphQL response status: {response.status_code}")
            logger.info(f"GraphQL response body: {response.text}") 

            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid or missing token. Please check your personal access token.")
            elif response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                remaining = int(response.headers['X-RateLimit-Remaining'])
                reset_time = int(response.headers['X-RateLimit-Reset'])
                if remaining == 0:
                    sleep_time = max(reset_time - time.time(), 0) + 10
                    logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                    await asyncio.sleep(sleep_time) 
                    return await make_graphql_request(query)
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"GraphQL request failed with status code {response.status_code}: {response.text}")

            CACHE[cache_key] = {
                "data": response.json(),
                "timestamp": time.time()
            }

            await asyncio.sleep(2)  

            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request failed: {str(e)}") 
            logger.error(f"Error type: {type(e)}") 
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

def is_within_date_range(date_str: str, years: Optional[int] = None, months: Optional[int] = None) -> bool:
    commit_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now(timezone.utc)
    if years:
        cutoff_date = current_date - timedelta(days=years * 365)
    elif months:
        cutoff_date = current_date - timedelta(days=months * 30)
    else:
        return True
    return commit_date >= cutoff_date.replace(tzinfo=None)

@app.get("/search/", response_model=List[RepositoryInfo])
async def search_github_repos(
    language: str = Query(..., description="Programming language to search for"),
    tools: Optional[List[str]] = Query(None, description="List of tools/technologies to filter by"),
    min_stars: Optional[int] = Query(None, description="Minimum number of stars"),
    max_stars: Optional[int] = Query(None, description="Maximum number of stars"),
    years: Optional[int] = Query(None, description="Filter by last commit within this many years"),
    months: Optional[int] = Query(None, description="Filter by last commit within this many months"),
    num_results: int = Query(10, description="Number of results to return")
):
    query = f"""
    query {{
        search(query: "language:{language.lower()}{' ' + ' '.join([f'topic:{tool}' for tool in tools]) if tools else ''}", type: REPOSITORY, first: {num_results}) {{
            edges {{
                node {{
                    ... on Repository {{
                        name
                        owner {{
                            login
                        }}
                        description
                        stargazers {{
                            totalCount
                        }}
                        forks {{
                            totalCount
                        }}
                        createdAt
                        updatedAt
                        defaultBranchRef {{
                            target {{
                                ... on Commit {{
                                    history(first: 1) {{
                                        edges {{
                                            node {{
                                                ... on Commit {{
                                                    committedDate
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        url
                    }}
                }}
            }}
        }}
    }}
    """

    response = await make_graphql_request(query)
    if not response or 'data' not in response:
        raise HTTPException(status_code=404, detail="No repositories found.")

    filtered_repos = []
    for edge in response['data']['search']['edges']:
        repo = edge['node']
        latest_commit_date = None

        if repo['defaultBranchRef'] and repo['defaultBranchRef']['target']:
            latest_commit_date = repo['defaultBranchRef']['target']['history']['edges'][0]['node']['committedDate']

        if not latest_commit_date:
            logger.warning(f"Skipping {repo['name']}: No latest commit date found.")
            continue
        if min_stars is not None and repo['stargazers']['totalCount'] < min_stars:
            logger.warning(f"Skipping {repo['name']}: Stars ({repo['stargazers']['totalCount']}) < min_stars ({min_stars}).")
            continue
        if max_stars is not None and repo['stargazers']['totalCount'] > max_stars:
            logger.warning(f"Skipping {repo['name']}: Stars ({repo['stargazers']['totalCount']}) > max_stars ({max_stars}).")
            continue
        if not is_within_date_range(latest_commit_date, years=years, months=months):
            logger.warning(f"Skipping {repo['name']}: Last commit date ({latest_commit_date}) is outside the specified range.")
            continue

        filtered_repos.append(RepositoryInfo(
            name=repo['name'],
            owner=repo['owner']['login'],
            description=repo.get('description'),
            stars=repo['stargazers']['totalCount'],
            forks=repo['forks']['totalCount'],
            created_at=repo['createdAt'],
            updated_at=repo['updatedAt'],
            last_commit=latest_commit_date,
            link=repo['url']
        ))

    return filtered_repos[:num_results]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)