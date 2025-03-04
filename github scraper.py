import pandas as pd
import requests
import time
from datetime import datetime, timedelta, timezone
from retrying import retry
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

GITHUB_API_URL = "INTRODUCE YOUT TOKEN"
# Global variable to track API call count
api_call_count = 0


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def make_api_request(url, params=None):
    global api_call_count
    headers = {
        "Authorization": f"INSERT YOUR TOKEN"
    }
    api_call_count += 1
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 401:
        raise Exception("Invalid or missing token. Please check your personal access token.")
    elif response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
        remaining = int(response.headers['X-RateLimit-Remaining'])
        reset_time = int(response.headers['X-RateLimit-Reset'])
        print(f"{Fore.YELLOW}Rate limit remaining: {remaining}, Reset time: {reset_time}")
        if remaining == 0:
            sleep_time = max(reset_time - time.time(), 0) + 1
            print(f"{Fore.RED}Rate limit exceeded. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
            return make_api_request(url, params)
    elif response.status_code != 200:
        raise Exception(f"{Fore.RED}API request failed with status code {response.status_code}: {response.text}")
    # Add a small delay between API calls to avoid hitting the rate limit
    time.sleep(1)
    return response.json()


def check_rate_limit():
    url = f"{GITHUB_API_URL}/rate_limit"
    headers = {
        "Authorization": f"token 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"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            rate_limit_data = response.json()
            print(f"{Fore.CYAN}Rate Limit Status:", rate_limit_data)
        else:
            print(f"{Fore.RED}Failed to fetch rate limit status. Status code: {response.status_code}")
    except Exception as e:
        print(f"{Fore.RED}Error fetching rate limit: {e}")


def search_repositories(query, per_page=100, page=1):
    url = f"{GITHUB_API_URL}/search/repositories"
    params = {
        'q': query,
        'per_page': per_page,
        'page': page
    }
    return make_api_request(url, params)


def get_repository_metadata(owner, repo):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"
    return make_api_request(url)


def get_latest_commit_date(owner, repo):
    """Fetch the latest commit date for a repository."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
    commits = make_api_request(url, params={'per_page': 1})  # Fetch only the latest commit
    if commits:
        return commits[0]['commit']['author']['date']
    return None


def is_within_date_range(date_str, years=None, months=None):
    """Check if the given date is within the specified time range."""
    commit_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now(timezone.utc)  # Use timezone-aware datetime (compatible with Python < 3.11)

    if years:
        cutoff_date = current_date - timedelta(days=years * 365)
    elif months:
        cutoff_date = current_date - timedelta(days=months * 30)
    else:
        return True  # No date filter applied

    return commit_date >= cutoff_date.replace(tzinfo=None)  # Remove timezone info for comparison


def main():
    # ASCII Art for GitHub Scraper
    print(f"""{Fore.CYAN}
 ██████  ██ ████████ ██   ██ ██    ██ ██████      ███████  ██████ ██████   █████  ██████  ███████ ██████  
██       ██    ██    ██   ██ ██    ██ ██   ██     ██      ██      ██   ██ ██   ██ ██   ██ ██      ██   ██ 
██   ███ ██    ██    ███████ ██    ██ ██████      ███████ ██      ██████  ███████ ██████  █████   ██████  
██    ██ ██    ██    ██   ██ ██    ██ ██   ██          ██ ██      ██   ██ ██   ██ ██      ██      ██   ██ 
 ██████  ██    ██    ██   ██  ██████  ██████      ███████  ██████ ██   ██ ██   ██ ██      ███████ ██   ██ 
    """)
    print(f"{Fore.CYAN}{'-' * 50}")
    print(f"{Fore.YELLOW}Welcome to the GitHub Scraper!")
    print(f"{Fore.CYAN}{'-' * 50}")

    # Check rate limit at the start
    print(f"\n{Fore.CYAN}Checking rate limit...")
    check_rate_limit()

    # Display available languages menu
    available_languages = [
        "Python", "C", "C++", "C#", "Go", "Java", "JavaScript",
        "Kotlin", "PHP", "Ruby", "Rust", "Scala", "TypeScript"
    ]
    print(f"\n{Fore.CYAN}Available languages to search for:")
    for i, lang in enumerate(available_languages, start=1):
        print(f"{Fore.YELLOW}{i}. {lang}")

    # Input for language selection
    try:
        lang_choice = int(
            input(f"\n{Fore.CYAN}Enter the number corresponding to the language you want to search for: "))
        selected_language = available_languages[lang_choice - 1]
    except (ValueError, IndexError):
        print(f"{Fore.RED}Invalid selection. Defaulting to Python.")
        selected_language = "Python"

    # Display available tools menu
    available_tools = [
        "firebase", "mysql", "docker", "kubernetes", "react", "angular", "vue",
        "tensorflow", "pytorch", "flask", "django", "fastapi", "mongodb", "postgresql"
    ]
    print(f"\n{Fore.CYAN}Available tools/technologies to filter by:")
    for i, tool in enumerate(available_tools, start=1):
        print(f"{Fore.YELLOW}{i}. {tool}")

    # Input for tools selection
    print(f"\n{Fore.CYAN}Do you want to filter by associated tools/technologies? (y/n): ")
    apply_tool_filter = input().lower() == 'y'
    if apply_tool_filter:
        try:
            tool_choices = input(
                f"{Fore.CYAN}Enter the numbers corresponding to the tools (comma-separated, e.g., 1,3,5): ")
            tool_indices = [int(idx.strip()) - 1 for idx in tool_choices.split(",") if idx.strip().isdigit()]
            tools = [available_tools[idx] for idx in tool_indices if 0 <= idx < len(available_tools)]
        except (ValueError, IndexError):
            print(f"{Fore.RED}Invalid selection. No tools will be applied.")
            tools = []
    else:
        tools = []  # No filtering

    # Input for number of results
    try:
        num_results = int(input(f"{Fore.CYAN}How many results do you want to see? "))
    except ValueError:
        print(f"{Fore.RED}Invalid input. Defaulting to 10 results.")
        num_results = 10

    # Optional: Input for star filtering
    apply_star_filter = input(f"{Fore.CYAN}Do you want to filter by stars? (y/n): ").lower() == 'y'
    if apply_star_filter:
        print(f"\n{Fore.CYAN}Enter the range of stars (e.g., '>100', '<500', or '100-500'):")
        star_range = input(f"{Fore.CYAN}Enter the star range: ")
        try:
            if '>' in star_range:
                min_stars = int(star_range.replace('>', '').strip())
                max_stars = float('inf')
            elif '<' in star_range:
                max_stars = int(star_range.replace('<', '').strip())
                min_stars = 0
            elif '-' in star_range:
                min_stars, max_stars = map(int, star_range.split('-'))
            else:
                print(f"{Fore.RED}Invalid input. Defaulting to no star filter.")
                min_stars, max_stars = 0, float('inf')
        except ValueError:
            print(f"{Fore.RED}Invalid input. Defaulting to no star filter.")
            min_stars, max_stars = 0, float('inf')
    else:
        min_stars, max_stars = 0, float('inf')  # No filtering

    # Optional: Input for date filtering
    apply_date_filter = input(f"{Fore.CYAN}Do you want to filter by last commit date? (y/n): ").lower() == 'y'
    if apply_date_filter:
        try:
            years = int(input(f"{Fore.CYAN}Enter the number of years to filter by (leave blank for none): ") or 0)
            months = int(input(f"{Fore.CYAN}Enter the number of months to filter by (leave blank for none): ") or 0)
        except ValueError:
            print(f"{Fore.RED}Invalid input. Defaulting to no date filter.")
            years, months = 0, 0
    else:
        years, months = 0, 0  # No filtering

    # Construct the search query
    query = f"language:{selected_language.lower()}"
    if tools:
        query += " " + " ".join([f"topic:{tool}" for tool in tools])

    print(f"\n{Fore.CYAN}Searching repositories...")
    results = search_repositories(query, per_page=100, page=1)  # Fetch 100 repositories
    if not results or 'items' not in results:
        print(f"{Fore.RED}No repositories found. Please try again with different criteria.")
        return

    # Apply custom filters
    filtered_repos = []
    print(f"\n{Fore.CYAN}Processing repositories...")
    for repo in tqdm(results['items'], desc=f"{Fore.CYAN}Filtering repositories", unit="repo"):
        owner = repo['owner']['login']
        repo_name = repo['name']

        # Fetch the latest commit date
        latest_commit_date = get_latest_commit_date(owner, repo_name)
        if not latest_commit_date:
            continue

        # Filter by stars
        if not (min_stars <= repo['stargazers_count'] <= max_stars):
            continue

        # Filter by date
        if not is_within_date_range(latest_commit_date, years=years, months=months):
            continue

        repo['latest_commit_date'] = latest_commit_date
        filtered_repos.append(repo)

    # Sort by stars
    filtered_repos.sort(key=lambda x: x['stargazers_count'], reverse=True)

    if not filtered_repos:
        print(f"\n{Fore.RED}No repositories matched your criteria. Try adjusting your filters or removing them.")
        print(f"{Fore.CYAN}Here are some unfiltered results:")
        for i, repo in enumerate(results['items'][:num_results], start=1):
            print(f"{Fore.YELLOW}{i}. {repo['name']} by {repo['owner']['login']} ({repo['stargazers_count']} stars)")
            print(f"{Fore.CYAN}   Link: {repo['html_url']}")
        return

    print(f"\n{Fore.CYAN}{'-' * 50}")
    print(f"{Fore.GREEN}Found {len(filtered_repos)} repositories matching your criteria:")
    print(f"{Fore.CYAN}{'-' * 50}")
    for i, repo in enumerate(filtered_repos[:num_results], start=1):
        print(f"{Fore.YELLOW}{i}. {repo['name']} by {repo['owner']['login']} ({repo['stargazers_count']} stars)")
        print(f"{Fore.CYAN}   Link: {repo['html_url']}")
        print(f"{Fore.CYAN}   Last Commit: {repo['latest_commit_date']}")
        print(f"{Fore.CYAN}{'-' * 50}")

    try:
        choice = int(input(f"\n{Fore.CYAN}Select a repository number to analyze: ")) - 1
        selected_repo = filtered_repos[choice]
        owner = selected_repo['owner']['login']
        repo_name = selected_repo['name']
    except (ValueError, IndexError):
        print(f"{Fore.RED}Invalid selection. Exiting.")
        return

    print(f"\n{Fore.CYAN}{'-' * 50}")
    print(f"{Fore.GREEN}Analyzing repository: {repo_name} by {owner}")
    print(f"{Fore.CYAN}{'-' * 50}")
    print(f"\n{Fore.CYAN}Fetching repository metadata...")
    metadata = get_repository_metadata(owner, repo_name)
    print(f"{Fore.GREEN}Name: {metadata['name']}")
    print(f"{Fore.CYAN}Description: {metadata['description']}")
    print(f"{Fore.CYAN}Stars: {metadata['stargazers_count']}, Forks: {metadata['forks_count']}")
    print(f"{Fore.CYAN}Created At: {metadata['created_at']}, Updated At: {metadata['updated_at']}")
    print(f"{Fore.CYAN}Link: {metadata['html_url']}")
    print(f"{Fore.CYAN}{'-' * 50}")

    save_file({
        "Repository": [repo_name],
        "Owner": [owner],
        "Description": [metadata['description']],
        "Stars": [metadata['stargazers_count']],
        "Forks": [metadata['forks_count']],
        "Created At": [metadata['created_at']],
        "Updated At": [metadata['updated_at']],
        "Last Commit": [selected_repo['latest_commit_date']],
        "Link": [metadata['html_url']]
    })


def save_file(data, csv_path="my_data.csv", json_path="my_data.json"):
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"{Fore.GREEN}File saved successfully: {csv_path}")
    df.to_json(json_path, orient="records", indent=4, force_ascii=False)
    print(f"{Fore.GREEN}File saved successfully: {json_path}")


if __name__ == "__main__":
    main()
