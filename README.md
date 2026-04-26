# HW-3: Database system development (Railway Travel Classes and Facilities domain)

A web application implementing 3 forms (INSERT / UPDATE / DELETE) and 3 reports (SELECT) over a normalized MySQL 8.4 database. Built with FastAPI (server-rendered Jinja2 + a JSON API), SQLAlchemy Core (no ORM — every SQL statement is visible in the source), PyMySQL, pytest, and Docker Compose.

## Prerequisites

### Onion / three-layer architecture

The application is organized as a strict three-layer architecture (a slimmed-down Onion). The main idea is to keep HTTP concerns, business logic, and data access apart so each layer can be reasoned about and tested in isolation.

- **Controller** receives the HTTP request, validates input via Pydantic DTOs, calls exactly one service method, and renders either a Jinja2 template (HTML) or a Pydantic response model (JSON). It does NOT contain business logic and NEVER touches SQL or repositories directly.
- **Service** implements one business capability (e.g. issue a ticket, build a manifest), manages the transaction with `engine.begin()` / `engine.connect()`, orchestrates one or more repositories, and raises typed domain exceptions on rule violations.
- **Repository** owns one aggregate (one table or a parent + its specialization tables sharing a PK) and runs raw SQL via SQLAlchemy Core's `text()` with named parameters.
- **Domain models** (plain `@dataclass` classes) mirror DB rows and flow upward through services to controllers. **DTOs** (Pydantic models) are HTTP-only — services never see them.

To see this in practice, consider issuing a ticket: 
1. The browser POSTs `/forms/issue-ticket`. 
2. `forms_controller.py` validates the form, builds an `IssueTicketCommand`, and calls `TicketService.issue_ticket(cmd)`. 
3. The service opens a transaction, asks `PassengerRepository`, `TrainRepository`, `TravelClassRepository`, and `PricingRepository` to validate FKs and look up the price, then asks `TicketRepository.next_ticket_number(...)` and `TicketRepository.insert(...)` to write the row. 
4. The committed `Ticket` domain dataclass flows back up; the controller hands it to the `forms/issue_ticket_success.html` template along with a snapshot of the affected `(train, service_date)`, and the browser receives the rendered HTML.

```mermaid
flowchart LR
    Browser["Browser<br/>POST /forms/issue-ticket"] --> Ctrl["forms_controller.py<br/>(FastAPI router)"]
    Ctrl --> Svc["TicketService.issue_ticket"]
    Svc --> R1["PassengerRepository"]
    Svc --> R2["TrainRepository"]
    Svc --> R3["TravelClassRepository"]
    Svc --> R4["PricingRepository"]
    Svc --> R5["TicketRepository"]
    R1 --> DB[(MySQL 8.4)]
    R2 --> DB
    R3 --> DB
    R4 --> DB
    R5 --> DB
    DB --> R5
    R5 --> Svc
    Svc --> Ctrl
    Ctrl --> Tmpl["Jinja2 template<br/>forms/issue_ticket_success.html"]
    Tmpl --> Resp["HTML response"]
```

The same flow exists for every other operation; reports compose multiple read-only repository calls in Python rather than using a single complex JOIN.

## 1. How to build a project?

### 1.1. Prerequisites

- **Python 3.13+** — recommended via [pyenv](https://github.com/pyenv/pyenv), [asdf](https://asdf-vm.com/), or [the official installer](https://www.python.org/downloads/).
- **Docker + Docker Compose** — for the local MySQL instance: [Docker Desktop](https://www.docker.com/products/docker-desktop/).
  - Alternatively, install **MySQL 8.4** locally: <https://dev.mysql.com/downloads/mysql/>
- **Make** — already available on macOS / Linux; on Windows use WSL or [chocolatey: make](https://community.chocolatey.org/packages/make).

### 1.2. Clone and open the project

```bash
git clone <repo-url> db-hw3-railway-service
cd db-hw3-railway-service
```

Open in your IDE of choice. The repo root contains the FastAPI app under `app/`, raw migrations under `migrations/`, and CSV fixtures under `seeds/`.

### 1.3. Configure and run

**Step 1 — Create a virtualenv and install dependencies.**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Step 2 — Set `DATABASE_URL`.** Copy `.env.example` to `.env`. 
The default points at the Docker MySQL container with the PyMySQL `local_infile=1` flag enabled (required for `LOAD DATA … INFILE` during seeding):

```dotenv
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/railway_service?local_infile=1
DEBUG=true
TEMPLATE_DIR=app/templates
STATIC_DIR=app/static
```

**Step 3 — Start MySQL and apply migrations.** Two ways:

```bash
make wipe       # docker compose down -v && up -d db (fresh volume, MySQL only)
make migrate    # python migrate.py — applies 001_initial_schema, 002_hw3_refinements, 099_seed_data
```

`make migrate` creates a `schema_migrations` tracking table on first run so subsequent calls are no-ops. 

`make reset` drops every base table and re-applies all migrations — handy after experimenting in the DB.

**Step 4 — Run the FastAPI app.**

```bash
make run        # uvicorn app.main:app --reload
make up         # or via Docker compose
```

### 1.4. Verify

Open these URLs in your browser:

| URL                                            | What you'll see                                    |
|------------------------------------------------|----------------------------------------------------|
| <http://localhost:8000/>                       | Index page with links to all 3 forms and 3 reports |
| <http://localhost:8000/docs>                   | Auto-generated Swagger UI for the JSON API         |
| <http://localhost:8000/forms/issue-ticket>     | Form 1 — Issue Ticket                              |
| <http://localhost:8000/forms/reschedule-train> | Form 2 — Reschedule Train (cascade UPDATE)         |
| <http://localhost:8000/forms/cancel-ticket>    | Form 3 — Cancel Ticket                             |
| <http://localhost:8000/reports/boarding-pass>  | Report 1 — Boarding Pass (printable ticket)        |
| <http://localhost:8000/reports/train-manifest> | Report 2 — Train Manifest                          |
| <http://localhost:8000/reports/route-pricing>  | Report 3 — Route Pricing Schedule                  |

## 2. Forms and reports

### Forms

| # | Form                 | Operation        | Stakeholder        | Rubric demo                                                                                                                                                                                                                                          |
|---|----------------------|------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | **Issue Ticket**     | INSERT           | Booking Clerk      | Multi-aggregate FK validation + atomic insert with pricing-derived `price_paid`.                                                                                                                                                                     |
| 2 | **Reschedule Train** | UPDATE (cascade) | Operations Manager | `ON UPDATE CASCADE` on the composite PK `(train_number, service_date)` propagating to `coach` and `ticket`. The success page renders 3 before / 3 after table snapshots side-by-side.                                                                |
| 3 | **Cancel Ticket**    | DELETE           | Booking Clerk      | Single-row deletion preserving referential integrity (nothing FKs into `ticket`). Dependent dropdown demo: pick a train → ticket dropdown is repopulated via a small fetch call to `/api/lookups/tickets-for-train/{train}/{date}`, no JS framework. |

### Reports

| # | Report                     | Stakeholder                 | Composition                                                                                                                                                                       |
|---|----------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | **Boarding Pass**          | Passenger                   | 8 reads (ticket / passenger / train / operator / route / class / route_station / station) composed in Python; rendered as a printable ticket-styled card with `@media print` CSS. |
| 2 | **Train Manifest**         | Operations Manager          | 6 reads (train / operator / route / ticket / passenger / class) composed in Python; tabular passenger list, supports the empty-manifest case (train with zero tickets).           |
| 3 | **Route Pricing Schedule** | Ops Manager / Booking Clerk | 4 reads (pricing / operator / class / route) with optional `?operator=` and `?route=` filters. Empty filter combinations return 200 with `rows=[]`.                               |

Each form and report has both an HTML route (under `/forms/...` or `/reports/...`) and a mirrored JSON API route under `/api/...`.

## 3. Database Schema

![Database schema](railway_service.png)

19 tables grouped into 12 repository aggregates:

- **9 entity aggregates:** `railway_operator`, `route`, `station`, `travel_class` (+3 specializations: `first_class`, `second_class`, `sleeping_class`), `facility`, `passenger`, `train`, `coach` (+4 specializations: `seating_coach`, `sleeping_coach`, `dining_coach`, `luggage_van`), `ticket`.
- **3 junction aggregates:** `route_station` (route ↔ station, M:N), `class_facility` (travel_class ↔ facility, M:N), `operator_class_route_pricing` (ternary).

Generated columns: `train.duration_minutes` (computed from scheduled_departure / scheduled_arrival) and `route.distance_price_multiplier` (computed from `total_distance_km`). Both are excluded from INSERT/UPDATE column lists in repositories per APD-003 §3.3.

The full DDL with FK constraints inlined is in [`migrations/001_initial_schema.sql`](migrations/001_initial_schema.sql); 

HW3 column refinements (`booking_status`, `payment_method`, `actual_*`, `delay_reason`, drop of `passenger.phone`) are in [`migrations/002_hw3_refinements.sql`](migrations/002_hw3_refinements.sql).

## 4. Make commands

```bash
make help        # list everything
make up          # start MySQL + app via docker compose (background)
make down        # stop the stack
make db-up       # start only the db service
make db-shell    # open the mysql client inside the db container
make migrate     # python migrate.py — apply pending migrations
make reset       # drop all tables and re-apply schema + seeds (preserves volume)
make wipe        # docker compose down -v && up -d db (full volume nuke + restart)
make run         # uvicorn app.main:app --reload (local, expects venv activated)
make test        # python -m pytest -v (resets DB at session start)
make install     # pip install -e ".[dev]"
make clean       # remove __pycache__, .pytest_cache, *.egg-info
make logs        # tail app container logs
make ps          # docker compose ps
```

`make migrate` and `make reset` use the same `migrate.py` runner — `--reset` drops every base table via an `information_schema.tables` query (no hardcoded list) and re-applies the migrations from scratch.

## 5. Tests

The full pytest suite lives under [`tests/`](tests/).

```bash
make test
...
# ============================== 16 passed in 7.18s ==============================
```

Coverage matrix:

- **Forms (8 tests):** every form has a happy-path test that captures `before_*.csv` and `after_*.csv` snapshots of the affected tables to `tests/evidence/<test_name>/` and writes a `diff.md` summary; plus error-path tests for each documented exception.
- **Reports (8 tests):** structural correctness — exact row counts, sort order, joined-field presence, empty-case handling, 404 on missing input.

Each pytest run regenerates `tests/evidence/test_plan.md` with one entry per test (status + docstring). The cascade test in `tests/test_forms/test_reschedule_train.py` produces 6 CSVs (3 before / 3 after for `train`, `coach`, `ticket`) — that's the single screenshot needed for HW3 Step 7's cascade-UPDATE evidence.

Test runs are reproducible: a session-level `setup_database` fixture wipes via `information_schema` and re-runs `migrate.py` via subprocess, so tests always start from the canonical seed state regardless of any prior DB experimentation.

## 6. Project structure

```
db-hw3-railway-service/
├── app/                         FastAPI application
│   ├── main.py                  app entrypoint, router wiring, exception handlers
│   ├── config.py                Pydantic Settings (.env loader)
│   ├── db.py                    SQLAlchemy Engine factory
│   ├── dependencies.py          FastAPI DI factories for services
│   ├── exceptions.py            DomainError hierarchy + handler registration
│   ├── controllers/             FastAPI routers (HTML + /api/* JSON)
│   ├── services/                business logic (one per capability)
│   ├── repositories/            raw SQL via SQLAlchemy Core (one per aggregate)
│   ├── domain/                  @dataclass DB-shaped models + report payloads
│   ├── dto/                     Pydantic HTTP-shaped models
│   ├── templates/               Jinja2 HTML
│   └── static/                  styles.css incl. @media print
├── migrations/                  001_initial_schema.sql, 002_hw3_refinements.sql, 099_seed_data.sql
├── seeds/                       19 CSV fixtures, mounted to /var/lib/mysql-files in the db container
├── tests/                       pytest suite + tests/evidence/ artifacts
├── migrate.py                   migration runner (supports --reset)
├── docker-compose.yml           MySQL 8.4 (with --local-infile=1) + app
├── Dockerfile                   Python 3.13-slim base
├── pyproject.toml               PEP 621 deps + pytest config
└── Makefile                     up/down/migrate/reset/wipe/test/run/...
```

## 8. Useful links

### FastAPI / Pydantic

- **FastAPI tutorial** — <https://fastapi.tiangolo.com/tutorial/> — start here if FastAPI is new
- **Pydantic v2 docs** — <https://docs.pydantic.dev/latest/>

### SQLAlchemy Core (no ORM)

- **SQLAlchemy 2.0 Core tutorial** — <https://docs.sqlalchemy.org/en/20/tutorial/index.html> — focus on the "Working with Engines and Connections" and "Working with Data" pages
- **`text()` and named parameters** — <https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.text>
- **`bindparam(expanding=True)` for `IN (:ids)`** — <https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.bindparam>

### MySQL 8.4

- **Reference manual** — <https://dev.mysql.com/doc/refman/8.4/en/>

### Jinja2

- **Documentation** — <https://jinja.palletsprojects.com/en/3.1.x/>

### pytest

- **Documentation** — <https://docs.pytest.org/en/stable/>

### Reference projects

- **FastAPI's official full-stack template** — <https://github.com/fastapi/full-stack-fastapi-template> — uses ORM, but a useful reference for project layout, DI patterns, and Pydantic settings.
