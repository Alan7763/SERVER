import os
import json
import random
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

app = FastAPI()
# Lee la clave de forma segura desde las variables de entorno de Render
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QuestionResponse(BaseModel):
    Question: str
    Options: list[str]
    Correct: str

CACHE = {"normal": [], "enraged": []}

FALLBACKS = [
    {"Question": "¿Qué patrón asegura una única instancia de una clase?", "Options": ["A) Factory", "B) Singleton", "C) Observer", "D) Adapter"], "Correct": "B"},
    {"Question": "¿Qué código HTTP indica que un recurso fue creado exitosamente?", "Options": ["A) 200 OK", "B) 204 No Content", "C) 201 Created", "D) 400 Bad Request"], "Correct": "C"},
    {"Question": "¿Qué estructura de datos sigue el principio LIFO?", "Options": ["A) Cola (Queue)", "B) Pila (Stack)", "C) Lista enlazada", "D) Grafo"], "Correct": "B"},
]

def refill_cache(phase: str):
    nivel = "avanzado de concurrencia, seguridad o arquitectura" if phase == "enraged" else "intermedio de ingeniería de software, POO, Git o bases de datos"
    prompt = (
        f"Genera exactamente 10 preguntas cortas y faciles distintas de opción múltiple (A, B, C, D) de nivel {nivel} en español. "
        "Responde ÚNICAMENTE con un JSON válido con la clave 'items', donde cada elemento tenga: "
        "'Question' (string), 'Options' (lista de 4 strings empezando con 'A) ', 'B) ', 'C) ', 'D) ') y 'Correct' ('A', 'B', 'C' o 'D')."
    )
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )
    batch = json.loads(chat.choices[0].message.content).get("items", [])
    random.shuffle(batch)
    CACHE[phase].extend(batch)

@app.get("/generate_question", response_model=QuestionResponse)
def generate_question(phase: str = "normal"):
    bucket = "enraged" if phase == "enraged" else "normal"
    if not CACHE[bucket]:
        try:
            refill_cache(bucket)
        except Exception as e:
            print(f"[ERROR GROQ]: {e}")
            return random.choice(FALLBACKS)
    return CACHE[bucket].pop()
