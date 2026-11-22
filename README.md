# PSR Print Studio

Turns a plain-language request, such as *"a Raspberry Pi case with a camera on a turning arm"*,
into modular, printable 3D parts that assemble and move after printing.

An LLM writes a design spec, the backend builds and checks the parts, and the web app shows
the assembled result in 3D.

## Structure

| Folder | What it is | Docs |
|---|---|---|
| `backend/` | Python · FastAPI · CadQuery: design engine, checks, STL/GLB export, AI loop (Ollama) | [backend/README.md](backend/README.md) |
| `frontend/` | Angular · Angular Material · three.js: 3D viewer and UI | [frontend/README.md](frontend/README.md) |


## Quick start

**1. Backend** (port 8000)
```bash
cd backend
conda env create -f environment.yml
conda activate psr-backend
uvicorn src.api.app:app --reload
```
API docs: http://127.0.0.1:8000/docs

**2. Frontend** (port 4200)
```bash
cd frontend
npm install
ng serve
```
Open http://localhost:4200

**3. Optional: AI design from text.** Install [Ollama](https://ollama.com), run `ollama serve`,
and pull the model set in `backend/.env`.


## How it fits together

```
Angular app ──/designs──▶ FastAPI ──▶ DesignService ──▶ build · check · export
     ▲                                                          │
     └──── manifest.json + GLB meshes + STL plates ◀────────────┘
```
