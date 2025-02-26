# GitHub Scraper App

A powerful and interactive GitHub scraper built using Python's Tkinter for GUI, which allows users to search for repositories on GitHub based on programming language, tools, stars, and last commit date. This app also provides advanced filtering options, such as applying multiple filters for tools/technologies and commit dates, and displays the search results in a user-friendly interface.

## Features
- **Search Repositories by Language**: Select one or more programming languages to search for relevant repositories.
- **Filter by Tools**: Apply a filter for repositories that use specific tools/technologies like Firebase, Docker, etc.
- **Filter by Stars**: Set a range for the minimum and maximum stars for repositories.
- **Filter by Last Commit Date**: Filter repositories based on their last commit date (within a certain number of years or months).
- **View Results with Links**: Display the repositories found, with clickable links directly to the repositories on GitHub.

## Libraries Used
The app uses several external libraries to make it functional and efficient. Below are the necessary libraries and how to install them.

### Required Libraries
1. **Tkinter**: Provides the graphical user interface for the app.
   - Tkinter is bundled with Python, so you don’t need to install it separately. If you are using Linux, you may need to install it manually.
   
   **Linux Installation** (for some distros like Ubuntu):
   ```bash
   sudo apt-get install python3-tk
   ```

2. **requests**: Used for making HTTP requests to GitHub's API.
   - Install using `pip`:
   ```bash
   pip install requests
   ```

3. **retrying**: Provides retrying functionality for API requests, to handle rate limits or temporary issues gracefully.
   - Install using `pip`:
   ```bash
   pip install retrying
   ```

4. **pandas**: Handles data manipulation and is useful for processing large sets of API results.
   - Install using `pip`:
   ```bash
   pip install pandas
   ```

5. **colorama**: Provides colored terminal text, which helps in creating visually distinct log messages.
   - Install using `pip`:
   ```bash
   pip install colorama
   ```

6. **webbrowser**: Used for opening GitHub repository URLs in a browser.

### Installation Instructions
1. Clone or download this repository.
2. Ensure you have Python 3.6 or higher installed on your machine.
3. Install the necessary libraries using `pip`:
   ```bash
   pip install -r requirements.txt
   ```
4. Replace `INSERT YOUR TOKEN` with your GitHub personal access token to authenticate API requests (details on how to generate a token can be found in [GitHub Docs](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)).

5. Run the app using:
   ```bash
   python github_scraper.py
   ```

## Key Functions in the Code

### 1. `make_api_request(url, params=None)`
   - **Purpose**: Makes an authenticated GET request to GitHub's API with optional parameters.
   - **Usage**: This function handles retries in case of temporary API failures and manages rate-limiting logic to prevent overloading GitHub's API.
   - **Key Feature**: Automatically retries requests with exponential backoff, ensuring robust error handling for temporary issues.

### 2. `search_repositories(query, per_page=100, page=1)`
   - **Purpose**: Searches for GitHub repositories based on the provided query string.
   - **Usage**: Accepts a search query and fetches the repository results. Supports pagination via `page` and `per_page`.

### 3. `get_latest_commit_date(owner, repo)`
   - **Purpose**: Fetches the latest commit date for a repository.
   - **Usage**: This is used to filter repositories based on the date of the latest commit, allowing you to search for actively maintained projects.

### 4. `is_within_date_range(date_str, years=None, months=None)`
   - **Purpose**: Checks if the provided commit date is within the specified time range.
   - **Usage**: Filters repositories by the date of their latest commit, allowing users to exclude repositories that haven't been recently updated.

### 5. `log_message(message, color="black", link=False)`
   - **Purpose**: Logs messages in the app's log window.
   - **Usage**: This method allows the app to log the status of operations (e.g., repository search, errors, filters applied) in the UI. Messages can be color-coded and, if required, made clickable for links.

### 6. `open_link(event)`
   - **Purpose**: Opens a clickable URL (GitHub repository URL) in the default web browser when clicked in the logs.
   - **Usage**: The log window supports clickable hyperlinks, allowing users to open the repositories directly from the app.

## How the App Can Help You
This GitHub Scraper is a powerful tool for developers, researchers, or anyone interested in finding interesting open-source projects on GitHub based on specific programming languages, tools/technologies, or the recency of updates.

### Use Cases:
- **Finding repositories based on specific technologies**: If you're interested in finding repositories that use Firebase, Docker, or any other technology, this tool will help you filter projects that match your criteria.
- **Search for actively maintained projects**: By filtering based on the date of the latest commit, you can find projects that are actively maintained and updated.
- **Explore repositories with specific star counts**: This feature helps in identifying popular repositories that meet your desired level of community engagement.
- **Efficient exploration of repositories**: Instead of manually browsing GitHub, you can use this app to quickly find repositories that match your interests, saving time and effort.

## Conclusion
The GitHub Scraper App is a handy tool for developers, researchers, or anyone looking to find specific projects on GitHub. With its powerful filtering options, it provides an easy way to discover repositories that match particular criteria. Whether you're searching for projects based on language, tools, stars, or recent activity, this app offers a fast and efficient way to search and explore the vast open-source ecosystem on GitHub.
![image](https://github.com/user-attachments/assets/84d0691b-f600-43d4-b886-91d56eed2429)
