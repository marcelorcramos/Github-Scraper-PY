import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import pandas as pd
import requests
import time
from datetime import datetime, timedelta, timezone
from retrying import retry
from threading import Thread
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

GITHUB_API_URL = "https://api.github.com"
# Global variable to track API call count
api_call_count = 0


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def make_api_request(url, params=None):
    global api_call_count
    headers = {
        "Authorization": f"token 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"
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


def search_repositories(query, per_page=100, page=1):
    url = f"{GITHUB_API_URL}/search/repositories"
    params = {
        'q': query,
        'per_page': per_page,
        'page': page
    }
    return make_api_request(url, params)


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


class GitHubScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Scraper")
        self.root.geometry("1800x1080")

        # Variables for user inputs
        self.selected_languages = []
        self.selected_tools = []
        self.apply_tool_filter = tk.BooleanVar(value=False)
        self.min_stars = tk.StringVar(value="0")
        self.max_stars = tk.StringVar(value="∞")
        self.years = tk.StringVar(value="0")
        self.months = tk.StringVar(value="0")
        self.num_results = tk.StringVar(value="10")

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="GITHUB SCRAPER", font=("Arial", 25, "bold"), fg="black")
        title_label.grid(row=0, column=0, columnspan=3, pady=20)

        # Language Selection (Updated to use Combobox)
        language_frame = ttk.LabelFrame(self.root, text="Select Language", height=100)
        language_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        available_languages = ["Python", "C", "C++", "C#", "Go", "Java", "JavaScript",
                               "Kotlin", "PHP", "Ruby", "Rust", "Scala", "TypeScript"]

        self.selected_language = tk.StringVar()
        language_combobox = ttk.Combobox(language_frame, textvariable=self.selected_language, values=available_languages, state="readonly")
        language_combobox.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        language_combobox.set("Select a Language")  # Default placeholder text

        # Add a button to confirm the selection
        add_language_button = ttk.Button(language_frame, text="Add Selected Language", command=self.add_selected_language)
        add_language_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Delete Selected Language Button
        delete_language_button = ttk.Button(language_frame, text="Delete Selected Language", command=self.delete_selected_language)
        delete_language_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Listbox to display selected languages
        self.selected_languages_listbox = tk.Listbox(language_frame, selectmode=tk.MULTIPLE, height=5)
        self.selected_languages_listbox.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Tools Selection (unchanged)
        tools_frame = ttk.LabelFrame(self.root, text="Filter by Tools/Technologies", height=300)
        tools_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        available_tools = ["firebase", "mysql", "docker", "kubernetes", "react", "angular", "vue",
                           "tensorflow", "pytorch", "flask", "django", "fastapi", "mongodb", "postgresql"]

        self.tool_vars = {}
        canvas = tk.Canvas(tools_frame)
        scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, tool in enumerate(available_tools):
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(scrollable_frame, text=tool, variable=var)
            chk.grid(row=i, column=0, sticky="w", padx=10, pady=2)
            self.tool_vars[tool] = var

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        apply_tool_filter_chk = ttk.Checkbutton(tools_frame, text="Apply Tool Filter", variable=self.apply_tool_filter)
        apply_tool_filter_chk.pack(anchor="w", padx=10, pady=5)

        # Star Filtering
        star_frame = ttk.LabelFrame(self.root, text="Filter by Stars")
        star_frame.grid(row=1, column=2, padx=20, pady=10, sticky="nsew")
        min_stars_label = ttk.Label(star_frame, text="Min Stars:")
        min_stars_label.grid(row=0, column=0, padx=5, pady=5)
        min_stars_entry = ttk.Entry(star_frame, textvariable=self.min_stars)
        min_stars_entry.grid(row=0, column=1, padx=5, pady=5)

        max_stars_label = ttk.Label(star_frame, text="Max Stars:")
        max_stars_label.grid(row=1, column=0, padx=5, pady=5)
        max_stars_entry = ttk.Entry(star_frame, textvariable=self.max_stars)
        max_stars_entry.grid(row=1, column=1, padx=5, pady=5)

        # Date Filtering
        date_frame = ttk.LabelFrame(self.root, text="Filter by Last Commit Date")
        date_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        years_label = ttk.Label(date_frame, text="Years:")
        years_label.grid(row=0, column=0, padx=5, pady=5)
        years_entry = ttk.Entry(date_frame, textvariable=self.years)
        years_entry.grid(row=0, column=1, padx=5, pady=5)

        months_label = ttk.Label(date_frame, text="Months:")
        months_label.grid(row=1, column=0, padx=5, pady=5)
        months_entry = ttk.Entry(date_frame, textvariable=self.months)
        months_entry.grid(row=1, column=1, padx=5, pady=5)

        # Number of Results
        num_results_frame = ttk.LabelFrame(self.root, text="Number of Results")
        num_results_frame.grid(row=2, column=1, padx=20, pady=10, sticky="nsew")
        num_results_label = ttk.Label(num_results_frame, text="Results:")
        num_results_label.grid(row=0, column=0, padx=5, pady=5)
        num_results_entry = ttk.Entry(num_results_frame, textvariable=self.num_results)
        num_results_entry.grid(row=0, column=1, padx=5, pady=5)

        # Search Button and Progress Bar
        search_frame = ttk.Frame(self.root)
        search_frame.grid(row=2, column=2, padx=20, pady=10, sticky="nsew")
        self.search_button = ttk.Button(search_frame, text="Search Repositories", command=self.start_search)
        self.search_button.pack(side="left", padx=5)
        self.progress_bar = ttk.Progressbar(search_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(side="right", padx=5)

        # Logs Text Area
        logs_frame = ttk.LabelFrame(self.root, text="Logs")
        logs_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.log_text = tk.Text(logs_frame, height=15, wrap="word", cursor="arrow")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Make links clickable
        self.log_text.tag_configure("hyperlink", foreground="blue", underline=True)
        self.log_text.tag_bind("hyperlink", "<Button-1>", self.open_link)
        self.log_text.tag_bind("hyperlink", "<Enter>", lambda e: self.log_text.config(cursor="hand2"))
        self.log_text.tag_bind("hyperlink", "<Leave>", lambda e: self.log_text.config(cursor="arrow"))

    def open_link(self, event):
        index = self.log_text.index("@%s,%s" % (event.x, event.y))
        url = self.log_text.get(index + " wordstart", index + " wordend")
        if url.startswith("http"):
            webbrowser.open_new(url)

    def log_message(self, message, color="black", link=False):
        start_index = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, message + "\n", color)
        if link:
            self.log_text.tag_add("hyperlink", start_index, f"{start_index}+{len(message)}c")
        self.log_text.tag_configure(color, foreground=color)
        self.log_text.see(tk.END)

    def add_selected_language(self):
        """Add the selected language from the Combobox to the Listbox."""
        selected_lang = self.selected_language.get()
        if selected_lang and selected_lang != "Select a Language":
            if selected_lang not in self.selected_languages_listbox.get(0, tk.END):
                self.selected_languages_listbox.insert(tk.END, selected_lang)
                self.log_message(f"Added language: {selected_lang}", "green")
            else:
                self.log_message(f"Language '{selected_lang}' is already selected.", "orange")
        else:
            self.log_message("Please select a valid language.", "red")

    def delete_selected_language(self):
        """Delete the selected language(s) from the Listbox."""
        selected_indices = self.selected_languages_listbox.curselection()
        if not selected_indices:
            self.log_message("No language selected for deletion.", "red")
            return

        # Delete selected languages in reverse order to avoid index shifting
        for index in reversed(selected_indices):
            deleted_lang = self.selected_languages_listbox.get(index)
            self.selected_languages_listbox.delete(index)
            self.log_message(f"Deleted language: {deleted_lang}", "orange")

    def start_search(self):
        # Disable the search button to prevent multiple searches
        self.search_button.config(state="disabled")
        self.progress_bar["value"] = 0

        # Start the search in a separate thread
        search_thread = Thread(target=self.search_repositories)
        search_thread.start()

    def search_repositories(self):
        try:
            # Clear logs
            self.log_text.delete(1.0, tk.END)

            # Get user inputs
            selected_languages = list(self.selected_languages_listbox.get(0, tk.END))
            tools = [tool for tool, var in self.tool_vars.items() if var.get()]
            apply_tool_filter = self.apply_tool_filter.get()
            min_stars = self.min_stars.get()
            max_stars = self.max_stars.get()
            years = int(self.years.get()) if self.years.get().isdigit() else 0
            months = int(self.months.get()) if self.months.get().isdigit() else 0
            num_results = int(self.num_results.get()) if self.num_results.get().isdigit() else 10

            # Construct query
            if not selected_languages:
                self.log_message("Please select at least one language.", "red")
                self.search_button.config(state="normal")
                return

            query_parts = [f"language:{lang.lower()}" for lang in selected_languages]
            if apply_tool_filter and tools:
                query_parts += [f"topic:{tool}" for tool in tools]

            query = " ".join(query_parts)

            # Log start of search
            self.log_message(f"Searching repositories for languages: {', '.join(selected_languages)}", "blue")
            self.log_message(f"Query: {query}", "green")

            # Fetch repositories
            results = search_repositories(query, per_page=100, page=1)
            if not results or 'items' not in results:
                self.log_message("No repositories found. Please try again with different criteria.", "red")
                self.search_button.config(state="normal")
                return

            # Apply filters
            filtered_repos = []
            total_repos = len(results['items'])
            self.progress_bar["maximum"] = total_repos

            for i, repo in enumerate(results['items'], start=1):
                owner = repo['owner']['login']
                repo_name = repo['name']

                # Update progress bar
                self.progress_bar["value"] = i
                self.root.update_idletasks()

                # Fetch latest commit date
                latest_commit_date = get_latest_commit_date(owner, repo_name)
                if not latest_commit_date:
                    continue

                # Filter by stars
                stars = repo['stargazers_count']
                if not (int(min_stars) <= stars <= (float('inf') if max_stars == "∞" else int(max_stars))):
                    continue

                # Filter by date
                if not is_within_date_range(latest_commit_date, years=years, months=months):
                    continue

                # Add to filtered results
                filtered_repos.append(repo)
                if len(filtered_repos) >= num_results:
                    break

            # Display results
            if filtered_repos:
                for repo in filtered_repos:
                    repo_url = repo['html_url']
                    self.log_message(f"Repository: {repo['name']} ({repo['stargazers_count']} stars)", "blue", link=True)
                    self.log_text.insert(tk.END, repo_url + "\n", "hyperlink")
            else:
                self.log_message("No repositories matched the criteria.", "red")

        except Exception as e:
            self.log_message(f"An error occurred: {str(e)}", "red")
        finally:
            self.search_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubScraperApp(root)
    root.mainloop()