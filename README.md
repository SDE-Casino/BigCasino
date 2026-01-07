# BigCasino 🎰

A microservices-based casino platform featuring Memory and Solitaire games with Google OAuth authentication. Built as an SDE project by **Riccardo Miolato** and **Mattia Ferretti**.

---

## 🏗️ Architecture Overview

BigCasino follows a **layered microservices architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                           UI                                 │
│                  (React + TanStack Router)                   │
└─────────────────────────────────┬───────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Memory      │       │   Solitaire     │       │ Authentication  │
│  Process      │       │    Process      │       │    Process      │
│  Centric      │       │    Centric      │       │    Centric      │
└───────┬───────┘       └────────┬────────┘       └────────┬────────┘
        │                        │                         │
        ▼                        ▼                         ▼
┌───────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Memory Logic  │       │ Solitaire Logic │       │   Auth Logic    │
└───────┬───────┘       └────────┬────────┘       └────────┬────────┘
        │                        │                         │
        ▼                        ▼                         ▼
┌───────────────┐       ┌─────────────────┐       ┌─────────────────┐
│Memory Adapter │       │  Deck Adapter   │       │  Auth Adapter   │
│Image Adapter  │       │                 │       │  Google OAuth   │
└───────┬───────┘       └─────────────────┘       └────────┬────────┘
        │                                                  │
        ▼                                                  ▼
┌───────────────┐                                 ┌─────────────────┐
│  PostgreSQL   │                                 │    MongoDB      │
└───────────────┘                                 └─────────────────┘
```

### Layer Description

| Layer | Description |
|-------|-------------|
| **UI** | React frontend with TanStack Router and TailwindCSS |
| **Process Centric** | Orchestrates business workflows and coordinates between services |
| **Logic** | Contains core game/authentication business logic |
| **Adapter** | Handles data persistence and external API integrations |
| **Database** | PostgreSQL for Memory, MongoDB for Authentication |

---

## 📁 Project Structure

```
BigCasino/
├── ui/                          # Frontend application
│   └── src/                     # React components and routes
│
├── memory/                      # Memory game service
│   ├── memory/                  # Process centric layer
│   ├── memory_logic/            # Game logic
│   ├── memory_adapter/          # Database adapter (PostgreSQL)
│   └── image_adapter/           # Image handling service
│
├── solitaire/                   # Solitaire game service
│   ├── process_centric/         # Process centric layer
│   ├── solitaire_logic/         # Game logic
│   └── deck_adapter/            # Card deck API adapter
│
├── authentication/              # Authentication service
│   ├── process-centric/         # Process centric layer
│   ├── logic/                   # Auth logic
│   ├── adapter/                 # User data adapter
│   └── google/                  # Google OAuth integration
│
└── docker-compose.yml           # Container orchestration
```

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js & pnpm (for local UI development)

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BigCasino
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - **UI**: http://localhost:3000
   - **Memory Service**: http://localhost:8003
   - **Solitaire Service**: http://localhost:8010
   - **Auth Service**: http://localhost:8009

---

## 🔌 Service Ports

| Service | Port |
|---------|------|
| UI | 3000 |
| Memory (Process Centric) | 8003 |
| Memory Logic | 8002 |
| Memory Adapter | 8001 |
| Image Adapter | 8000 |
| Solitaire (Process Centric) | 8010 |
| Solitaire Logic | 8005 |
| Deck Adapter | 8006 |
| Auth (Process Centric) | 8009 |
| Auth Logic | 8008 |
| Auth Adapter | 8007 |
| Google OAuth | 8004 |
| PostgreSQL | 5432 |
| MongoDB | 27017 |

---

## 🌐 External Services

BigCasino integrates with the following external APIs:

| Service | Description | Used By |
|---------|-------------|---------|
| [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2) | User authentication via Google accounts | Authentication Service |
| [Deck of Cards API](https://deckofcardsapi.com/) | RESTful API for shuffling, drawing, and managing playing cards | Solitaire Service |
| [Cat as a Service (CATAAS)](https://cataas.com/) | Random cat image generation for memory card images | Memory Service |

---

## 🛠️ Tech Stack

- **Frontend**: React 19, TanStack Router, TanStack Query, TailwindCSS
- **Backend**: Python (FastAPI/Uvicorn)
- **Databases**: PostgreSQL, MongoDB
- **Containerization**: Docker & Docker Compose

---

## 👥 Authors

| Component | Author |
|-----------|--------|
| **Memory Service** | Mattia Ferretti |
| **UI** | Mattia Ferretti |
| **Solitaire Service** | Riccardo Miolato |
| **Authentication Service** | Riccardo Miolato |

---

## 📝 License

This project is developed for educational purposes as part of an SDE course.
