# Agentic Negotiator

A multi-agent AI negotiation platform where specialized **Consumer**, **Producer**, and **Negotiator** agents work together to reach optimal deals, using LLM-driven decision workflows.

**Live demo:** <your-vercel-link>  |  **API docs:** <your-railway-link>/docs

---

## Overview

Agentic Negotiator simulates real-world negotiation between two parties with competing goals. A **Consumer** agent wants the best price and terms, a **Producer** agent wants to protect margins and constraints, and a **Negotiator** agent sits in the middle, evaluating each offer, generating counteroffers, and steering both sides toward an outcome that maximizes overall satisfaction.

The architecture is domain-agnostic, so the same agent workflow can be applied to procurement, pricing, contracts, supply chain, and other business decisions.

## Key Features

- **Multi-agent architecture:** dedicated Consumer, Producer, and Negotiator agents with distinct goals and constraints
- **LLM-driven negotiation workflow:** evaluates offers, generates counteroffers, and explains its reasoning
- **Outcome optimization:** scores each round on satisfaction and constraints to converge on the best deal
- **Heuristic fallback mode:** runs without a local LLM using `NEGOTIATION_HEURISTIC=1`
- **User accounts and roles:** sign up, log in, and choose a consumer or producer role
- **Negotiation summaries:** a full round-by-round summary of every negotiation
- **Persistent storage:** requests, offers, and results are stored in MySQL

## How It Works

1. A user signs up, logs in, and chooses a role (Consumer or Producer).
2. The Consumer submits a request with requirements and a target price.
3. The Producer responds with their constraints and an initial offer.
4. The Negotiator agent evaluates both positions each round, scores satisfaction, and proposes a counteroffer.
5. Rounds repeat until the parties agree or a limit is reached.
6. The final deal and the full negotiation history appear on the summary page.

```
 Consumer Agent  <--->  Negotiator Agent  <--->  Producer Agent
       |                       |                        |
       +-------------- Satisfaction scoring ------------+
                               |
                          MySQL database
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Database | MySQL with SQLAlchemy and PyMySQL |
| AI | LLM-driven agents with a heuristic fallback (optional local GPT4All model) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Deployment | Railway (backend and database), Vercel (frontend) |

## Project Structure

```
agentic-negotiator/
├── backend/
│   ├── app/            # API routes, agents, and negotiation logic
│   └── tests/          # backend tests
├── frontend/
│   ├── index.html      # landing page
│   ├── signup.html     # create an account
│   ├── login.html      # sign in
│   ├── role.html       # choose Consumer or Producer
│   ├── request.html    # submit a negotiation request
│   ├── producer.html   # producer dashboard
│   ├── negotiate.html  # live negotiation view
│   ├── summary.html    # final results
│   ├── app.js
│   └── styles.css
├── scripts/            # helper scripts
├── init_db.py          # creates the database tables
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- MySQL Server 8.0
- Git

### 1. Clone the repository

```bash
git clone https://github.com/krithvik07/agentic-negotiator.git
cd agentic-negotiator
```

### 2. Create a virtual environment and install dependencies

Windows (PowerShell):

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up MySQL

Log in to MySQL and run:

```sql
CREATE DATABASE negotiation_db;
CREATE USER 'negotiation_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON negotiation_db.* TO 'negotiation_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Create the database tables

```bash
python init_db.py
```

### 6. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

### 7. Open the frontend

Open `frontend/index.html` with VS Code's Live Server extension, or run:

```bash
cd frontend
python -m http.server 5500
```

## Deployment

- **Backend and database (Railway):** deploy from GitHub, add a MySQL service, and set `DATABASE_URL` using the Railway MySQL variables. Start command:
```
  python init_db.py && uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```
- **Frontend (Vercel):** import the repo, set the Root Directory to `frontend`, and set the Framework Preset to `Other`.
- Update the API URL in `frontend/app.js` to your deployed backend address, and add your frontend URL to the CORS allowed origins in the backend.

## Testing

```bash
pytest backend/tests
```

## Roadmap

- [ ] Support for more than two negotiating parties
- [ ] Pluggable LLM providers (OpenAI, Gemini, Groq)
- [ ] Domain templates (procurement, pricing, contracts)
- [ ] Negotiation analytics dashboard
- [ ] Docker setup for one-command local runs

