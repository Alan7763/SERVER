from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
import json

# 1. Configuración del nuevo cliente de IA
client = genai.Client(api_key="AQ.Ab8RN6JZ8cG5g5I1gLeZlY7CuN-UCYvmuGED9b_SekNxm46BUw")

app = FastAPI()


# 2. Esquema de datos
class QuestionResponse(BaseModel):
    Question: str
    Options: list[str]
    Correct: str


@app.get("/generate_question", response_model=QuestionResponse)
async def generate_question():
    # 3. El Prompt Estricto
    prompt = """
    Genera una pregunta corta y facil de opción múltiple sobre ingeniería de software, arquitectura de sistemas, metodologías ágiles o patrones de diseño.
    Debes devolver ÚNICAMENTE un objeto JSON válido con la siguiente estructura exacta. No incluyas saludos, ni bloques de código markdown (```json).
    {
        "Question": "¿Pregunta generada aquí?",
        "Options": ["A) Opción 1", "B) Opción 2", "C) Opción 3", "D) Opción 4"],
        "Correct": "A, B, C o D (solo la letra correcta)"
    }
    """

    try:
        # 4. Nueva sintaxis con el modelo correcto
        response = client.models.generate_content(
            model='gemini-3.6-flash',  # <-- ¡El modelo exacto de tu lista!
            contents=prompt
        )

        # Limpiamos posibles residuos de formato que la IA pueda agregar
        raw_text = response.text.replace("```json", "").replace("```", "").strip()

        # Convertimos el texto a un diccionario de Python
        pregunta_json = json.loads(raw_text)
        return pregunta_json

    except Exception as e:
        print(f"Error en la IA: {e}")
        # Retorno de contingencia
        return {
            "Question": "Error del Jefe. ¿Qué patrón asegura una única instancia de una clase?",
            "Options": ["A) Factory", "B) Singleton", "C) Builder", "D) Prototype"],
            "Correct": "B"
        }