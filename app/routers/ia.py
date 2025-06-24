from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.ai import generate_ai_completion

router = APIRouter(
    prefix="/ia",
    tags=["Inteligencia Artificial (IA)"]
)

class TitleRequest(BaseModel):
    title: str

class DescriptionRequest(BaseModel):
    description: str

@router.post("/better-title")
def better_title(request: TitleRequest):
    prompt = f"Mejora el siguiente título de producto para que sea más atractivo y profesional: '{request.title}'"
    system_message = "Eres un experto en marketing de productos. Devuelve solo el nuevo título mejorado, sin explicaciones."
    result = generate_ai_completion(prompt, system_message)
    if not result:
        raise HTTPException(status_code=500, detail="Error al generar el título mejorado.")
    return {"better_title": result.strip()}

@router.post("/better-descripcion")
def better_description(request: DescriptionRequest):
    prompt = f"Mejora la siguiente descripción de producto para que sea más atractiva, detallada y profesional: '{request.description}'"
    system_message = "Eres un experto en marketing de productos. Devuelve solo la nueva descripción mejorada, sin explicaciones."
    result = generate_ai_completion(prompt, system_message)
    if not result:
        raise HTTPException(status_code=500, detail="Error al generar la descripción mejorada.")
    return {"better_description": result.strip()}
