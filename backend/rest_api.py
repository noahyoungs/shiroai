# rest_api.py
from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr, validator
from typing import List, Optional, Literal
from slides.icons.icon_similarity_search import (
    get_top_n_icons_for_bullet_point,
    get_top_n_icons_with_unique_embedding,
    get_top_n_icons_for_query,
)
from slides.images.generate_image import generate_upload_update_by_prompt
from dotenv import load_dotenv
from auth.authorize import authorize
import http.cookies
import logging
import uvicorn

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# Define request models
class BulletPointRequest(BaseModel):
    bullet_point: str
    n: int
    presentation_id: str

class UniqueEmbeddingRequest(BaseModel):
    bullet_point: str
    bullet_point_list: List[str]
    n: int
    presentation_id: str

class QueryRequest(BaseModel):
    query: str
    n: int
    presentation_id: str

# Update GenerateImageRequest to include negative_prompt
class GenerateImageRequest(BaseModel):
    presentationID: str
    prompt: str
    shape: Literal["full", "square"]
    style_preset: Optional[str]
    model_type: Literal["sdxl", "core", "dalle"]
    negative_prompt: Optional[str] = None

    @validator('presentationID', 'prompt')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('must not be empty')
        return v

# Define response model
class IconObject(BaseModel):
    detailed_name: str
    name: str
    source: str

async def authenticate_request(request: Request, presentation_id: str):
    cookie_str = request.headers.get('cookie', '')
    cookies = http.cookies.SimpleCookie()
    cookies.load(cookie_str)
    
    accessToken = cookies.get("next-auth.session-token", None).value if cookies else None
    
    if accessToken:
        logger.debug(f"Access token found: {accessToken}")
        logger.debug(f"Presentation ID: {presentation_id}")
        isAuthorized, isAuthenticated, userID = await authorize(presentation_id, accessToken)
        if not isAuthenticated:
            logger.warning("Not authenticated.")
            raise HTTPException(status_code=401, detail="Authentication issue. Please try logging out and logging back in.")
        if not isAuthorized:
            logger.warning("Unauthorized.")
            raise HTTPException(status_code=403, detail="Authorization issue. Please try logging out and logging back in.")
        return presentation_id, userID
    else:
        logger.warning("No access token found.")
        raise HTTPException(status_code=403, detail="Authorization issue, access token not found. Please try logging out and logging back in.")

@router.post("/icon/simple_bp_search", response_model=List[IconObject])
async def get_top_n_icons_for_bullet_point_route(request: BulletPointRequest, req: Request):
    try:
        await authenticate_request(req, request.presentation_id)
        result = await get_top_n_icons_for_bullet_point(request.bullet_point, request.n)
        # Map result to IconObject
        response = [IconObject(detailed_name=icon['icon_name'], name=icon['original_label'], source=icon['source']) for icon in result]
        return response
    except HTTPException as auth_error:
        logger.error(f"HTTP error occurred: {auth_error.detail}")
        raise auth_error
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/icon/unique_bp_search", response_model=List[IconObject])
async def get_top_n_icons_with_unique_embedding_route(request: UniqueEmbeddingRequest, req: Request):
    try:
        await authenticate_request(req, request.presentation_id)
        result = await get_top_n_icons_with_unique_embedding(request.bullet_point, request.bullet_point_list, request.n)
        # Map result to IconObject
        response = [IconObject(detailed_name=icon['icon_name'], name=icon['original_label'], source=icon['source']) for icon in result]
        return response
    except HTTPException as auth_error:
        logger.error(f"HTTP error occurred: {auth_error.detail}")
        raise auth_error
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/icon/query_search", response_model=List[IconObject])
async def get_top_n_icons_for_query_route(request: QueryRequest, req: Request):
    try:
        await authenticate_request(req, request.presentation_id)
        result = await get_top_n_icons_for_query(request.query, request.n)
        # Map result to IconObject
        response = [IconObject(detailed_name=icon['icon_name'], name=icon['original_label'], source=icon['source']) for icon in result]
        return response
    except HTTPException as auth_error:
        logger.error(f"HTTP error occurred: {auth_error.detail}")
        raise auth_error
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/slides/generate_image", response_model=dict)
async def generate_image_route(request: GenerateImageRequest, req: Request):
    try:
        await authenticate_request(req, request.presentationID)
        image_data = await generate_upload_update_by_prompt(
            request.presentationID, 
            request.prompt, 
            request.shape, 
            request.style_preset, 
            request.model_type,
            request.negative_prompt
        )
        return image_data
    except HTTPException as auth_error:
        logger.error(f"HTTP error occurred: {auth_error.detail}")
        raise auth_error
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

app.include_router(router)

# To run this file directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
