# Nexus Agency Website

A React frontend with a FastAPI backend for the Nexus software agency website. Features a portfolio, team page, testimonials, and contact form.

## Project Structure

- `packages/api-backend/` — FastAPI backend service
- `packages/web-app/` — React frontend application

## Getting Started

### Backend

```bash
cd packages/api-backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd packages/web-app
npm install
npm start
```

The frontend runs on `http://localhost:3000` and the API on `http://localhost:8000`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/api/v1/stats` | Company stats |
| GET | `/api/v1/services` | Services list |
| GET | `/api/v1/projects` | Portfolio projects |
| GET | `/api/v1/team` | Team members |
| POST | `/api/v1/contact` | Submit contact form |
| GET | `/api/v1/contact/submissions` | View submissions |
| POST | `/api/v1/auth/signup` | Register |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/testimonials` | List testimonials |
| POST | `/api/v1/testimonials` | Submit testimonial |
| GET | `/api/v1/testimonials/export/html` | Export as HTML |
