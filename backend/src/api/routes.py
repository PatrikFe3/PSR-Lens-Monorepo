from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from src.ai.orchestrator import NeedsInput
from src.api.schemas import BuildRequest, BuildResponse, PromptRequest
from src.core.issues import DesignError
from src.exceptions.ollama_exception import OllamaConnectionError
from src.services.design_service import DesignService

router = APIRouter()


@lru_cache(maxsize=1)
def service() -> DesignService:
    return DesignService()


def _response(result) -> BuildResponse:
    return BuildResponse(design_id=result.design_id, manifest=result.manifest, plates=result.plates,
                         files=sorted(result.files), warnings=[i.to_dict() for i in result.issues])


def _design_error(err: DesignError) -> JSONResponse:
    return JSONResponse(status_code=422, content={'detail': 'The design failed its checks.',
                                                  'issues': [i.to_dict() for i in err.issues]})


@router.get('/health')
def health():
    return {'status': 'ok', 'kernel': service().kernel.name}


@router.get('/catalog')
def catalog():
    s = service()
    return {**s.catalog.summary(), 'templates': [t.describe() for t in s.templates.values()]}


@router.post('/designs', response_model=BuildResponse)
def build(request: BuildRequest):
    try:
        return _response(service().build(request.spec, printer=request.printer, material=request.material))
    except DesignError as err:
        return _design_error(err)
    except KeyError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err


@router.post('/designs/from-prompt', response_model=BuildResponse)
def build_from_prompt(request: PromptRequest):
    try:
        _, result = service().design_from_prompt(request.prompt, ask_user=request.ask_user,
                                                 printer=request.printer, material=request.material)
        return _response(result)
    except NeedsInput as err:
        return JSONResponse(status_code=409, content={'detail': 'The design needs answers first.',
                                                      'questions': err.questions,
                                                      'spec': err.spec.model_dump()})
    except DesignError as err:
        return _design_error(err)
    except OllamaConnectionError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except ImportError as err:
        raise HTTPException(status_code=503, detail=f'AI is not available: {err}. Run "pip install ollama".') from err


def _file(design_id: str, *parts: str) -> Path:
    root = (service().output_dir / design_id).resolve()
    path = root.joinpath(*parts).resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail='File not found.')
    return path


@router.get('/designs/{design_id}/manifest')
def manifest(design_id: str):
    return FileResponse(_file(design_id, 'manifest.json'), media_type='application/json')


@router.get('/designs/{design_id}/meshes/{name}')
def mesh(design_id: str, name: str):
    return FileResponse(_file(design_id, 'meshes', name), media_type='model/gltf-binary')


@router.get('/designs/{design_id}/plates/{number}')
def plate(design_id: str, number: int):
    return FileResponse(_file(design_id, 'plates', f'plate_{number}.stl'), media_type='model/stl',
                        filename=f'{design_id}_plate_{number}.stl')
