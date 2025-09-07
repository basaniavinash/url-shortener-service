from fastapi import APIRouter, HTTPException, Path
from starlette.responses import RedirectResponse

from app.models import CreateResp, CreateReq, ExpandResp
from app.service import ShortenerService

router = APIRouter()
svc = ShortenerService()

@router.post("/v1/shorten", response_model=CreateResp, tags=["shortener"])
def shorten_url(req: CreateReq):
    try:
        out = svc.create(
            long_url=str(req.url),
            alias=req.alias,
            expires_at_iso=req.expires_at,
            owner_id=req.owner_id
        )

        return out

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except KeyError:
        raise HTTPException(status_code=400, detail="Alias already taken")

@router.get("/v1/expand/{id}", response_model=ExpandResp, tags=["shortener"])
def expand_url(id: str):
    try:
        out = svc.expand(id)
        return out
    except LookupError:
        raise HTTPException(status_code=404, detail="Not found")

@router.get("/v1/list/{owner_id}", tags=["shortener"])
def list_by_owner(owner_id: str):
    try:
        out = svc.list_by_owner(owner_id)
        return out
    except LookupError:
        raise HTTPException(status_code=400, detail=f"Error fetching urls for {owner_id}")

@router.get("/{id}", include_in_schema=False)
def redirect(id: str = Path(..., pattern=r"^[A-Za-z0-9_-]{4,20}$")):
    try:
        out = svc.resolve(id)
        if not out:
            raise HTTPException(status_code=500, detail="Invalid redirect target")
        return RedirectResponse(url=out, status_code=302)
    except LookupError:
        raise HTTPException(status_code=404, detail="Not Found")
    except PermissionError as pe:
        raise HTTPException(status_code=410, detail=str(pe))
