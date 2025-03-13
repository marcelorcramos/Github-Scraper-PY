# 🚀 GitHub Scraper (Python + Next.js)

A powerful GitHub repository scraper with a **FastAPI** backend and a **Next.js** frontend.  
This project allows users to search for repositories, filter by programming language, stars, forks, and more.  

## 🌟 Features

- 🔍 **Advanced GitHub repository search** using GraphQL API  
- ⚡ **FastAPI backend** for handling API requests  
- 💡 **Next.js frontend** for an intuitive user interface  
- 📦 **Caching** to optimize API requests  
- 🎨 **TailwindCSS** for modern UI design  
- 🛠 **Docker support** for easy deployment  

---

## 📌 Prerequisites

Before running the project, ensure you have the following installed:

- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/en/download/)
- [Docker & Docker Compose](https://docs.docker.com/get-docker/) *(Optional)*
- A **GitHub Personal Access Token** with `repo` and `read:org` permissions

---

## 🛠 Setup & Installation

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/marcelorcramos/Github-Scraper-PY.git
cd Github-Scraper-PY
```

### 2️⃣ Backend Setup (FastAPI)

#### Create a Virtual Environment  
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

#### Install Dependencies  
```sh
pip install -r requirements.txt
```

#### Configure Environment Variables  
Create a `.env` file in the root directory and add:

```sh
GITHUB_TOKEN=your_personal_access_token_here
```

#### Run the Backend  
```sh
cd python
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

The API should now be running at `http://localhost:8000`.

---

### 3️⃣ Frontend Setup (Next.js)

#### Install Dependencies  
```sh
npm install
```

#### Start the Frontend  
```sh
npm run dev
```

Now, open your browser and visit `http://localhost:3000`.

---

## 🐳 Running with Docker (Optional)

If you prefer using Docker, simply run:

```sh
docker-compose up --build
```

This will start both the backend and frontend automatically.

---

## 📸 Screenshot

Here's how the app looks in action:

![GithubScraper](https://github.com/user-attachments/assets/00b953f9-53ff-4bc1-ac32-4977721209a2)

---
