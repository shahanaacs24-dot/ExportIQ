# ExportIQ — AI-Powered MSME Export Readiness Assessment Platform

ExportIQ is a comprehensive, production-grade decision-support platform designed for Indian MSMEs to assess their export readiness for specific product-destination combinations. It evaluates legal registrations, product quality certifications, trade documentation, phytosanitary certificates, and destination-specific regulatory requirements.

---

## Key Features

1. **MSME Business Profile Management**: Manage organization details, GSTIN, PAN, IEC, Udyam registration, turnover, and export experience.
2. **Product & Destination Selection**: Browse supported export products (with HS codes) and destination countries (USA, UK, EU, UAE, etc.).
3. **Document Upload & Parsing**: Upload PDF or image documents. Supports native PDF text extraction (`pdfminer.six`) and OCR (`pytesseract`).
4. **Structured Field Extraction**: Automatically extracts business identifiers (GSTIN, PAN, IEC, Udyam numbers, and dates) using robust regex extractors.
5. **Knowledge Base & Compliance Matching Engine**: Deterministic rules engine matching business profile and document evidence against applicable export requirements. Distinguishes **compliant**, **missing**, **incomplete**, **expired**, **unverified**, and **not_applicable** states.
6. **Export Readiness Index (ERI)**: Calculates a transparent, weighted readiness score from 0 to 100 with category breakdowns and score explanations.
7. **Gap Analysis & Recommendations**: Automatically identifies compliance gaps and generates prioritized, actionable recommendations with official source references.
8. **PDF Readiness Report Generation**: Generates and downloads a structured PDF readiness report via ReportLab.
9. **Role-Based Security**: Complete JWT authentication with strict user ownership isolation.

---

## Technology Stack

- **Frontend**: React, Vite, TypeScript, Tailwind CSS, React Hook Form, Zod, Lucide Icons.
- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic.
- **Database**: PostgreSQL 18.
- **Document Processing**: `pdfminer.six`, Pillow, `pytesseract`.
- **Reports**: ReportLab PDF generation.
- **Testing**: `pytest` for backend, Vite / TypeScript build checks for frontend.
- **Deployment**: Docker, Docker Compose.

---

## Folder Structure

```
ExportIQ/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Routers (auth, profile, products, documents, assessments, reports)
│   │   ├── core/                # Config, database session, security, dependencies
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Document parser, OCR, compliance engine, ERI, PDF reports
│   │   ├── knowledge_base/      # Seeding script
│   │   └── migrations/          # Alembic migrations
│   ├── tests/                   # Pytest test suite (health, auth, profile, products, documents, compliance, eri, reports)
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API clients
│   │   ├── components/ui/       # UI components (Spinner, FormField, ErrorAlert)
│   │   ├── pages/               # Views (Login, Register, Dashboard, Profile, Products, Assessments)
│   │   └── types/               # TypeScript interfaces
│   ├── package.json
│   └── Dockerfile               # Frontend Dockerfile
├── docker-compose.yml           # Docker Compose setup
├── .env.example                 # Environment variables template
└── README.md                    # Project documentation
```

---

## Local Development (Without Docker — Uses your Local PostgreSQL)

### Prerequisites
- Python 3.11+ installed and in PATH
- Node.js 18+ & npm installed
- Local PostgreSQL 18.6 running on `localhost:5432` with database `exportiq`

### 1. Backend Setup
```bash
cd backend

# Create virtual environment & activate (optional but recommended)
python -m venv venv
source venv/Scripts/activate  # On Windows PowerShell: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp ../.env.example .env
# Edit .env and set your database URL:
# DATABASE_URL=postgresql+psycopg2://exportiq:your_password@localhost:5432/exportiq

# Seed database with products, countries, and requirements
python -m app.knowledge_base.seed

# Run backend tests
python -m pytest -v

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/api/docs`

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- Frontend App: `http://localhost:5173`

---

## Launching with Docker Compose

If Docker Desktop is running on your machine:
```bash
# Copy environment template
cp .env.example .env

# Build and start services in background
docker-compose up --build -d

# Check service logs
docker-compose logs -f
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Database: PostgreSQL on port `5433` (isolated from local PostgreSQL on 5432)

---

## Testing Instructions

```bash
# Run all backend tests
cd backend
python -m pytest -v

# Run frontend production build check
cd frontend
npm run build
```

---

## Known Limitations & Assumptions

1. **OCR Dependency**: `pdfminer.six` handles all native text-based PDFs. Scanned image-based PDFs require Tesseract OCR installed on the host or container.
2. **Indicative Assessment**: ExportIQ is a decision-support tool. It does not provide legal approval or official government certification.
3. **Jurisdiction Scope**: Initial requirements cover Indian export regulations (DGFT, FSSAI, APEDA, GST) and major destination markets (USA, EU, UAE, UK).

---

## Disclaimer

ExportIQ provides indicative export readiness assessments only and does not issue official certificates or guarantee export success. Always verify requirements with qualified trade professionals and official regulatory authorities.
