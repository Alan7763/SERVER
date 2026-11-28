import os
import json
import random
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QuestionResponse(BaseModel):
    Question: str
    Options: list[str]
    Correct: str

CACHE = {"normal": [], "enraged": []}
USED_QUESTIONS: list[str] = []

SUBTEMAS = {
    "normal": [
        "Comandos básicos de Git (init, add, commit, push, pull, status)",
        "Conceptos básicos de bases de datos y SQL (SELECT, INSERT, WHERE, tablas, llaves primarias)",
        "Fundamentos de programación (variables, ciclos for/while, arreglos, funciones, booleanos)",
        "Desarrollo web básico (HTML, CSS, HTTP GET/POST, JSON, códigos 200 y 404)",
        "Programación Orientada a Objetos básica (clases, objetos, herencia, métodos)",
        "Estructuras de datos fundamentales (listas, pilas, colas, diccionarios)",
    ],
    "enraged": [
        "Seguridad web básica (contraseñas, HTTPS, SQL Injection, autenticación)",
        "Redes y APIs (REST, JSON, códigos 401/403/500, puertos, DNS)",
        "Buenas prácticas de código y pruebas (bugs, debugging, pruebas unitarias, DRY)",
        "Sistemas operativos y terminal (archivos, procesos, RAM, CPU, Linux básico)",
    ],
}

FALLBACKS = [
    {"Question": "¿Qué comando sube tus commits locales a GitHub?", "Options": ["A) git pull", "B) git push", "C) git add", "D) git clone"], "Correct": "B"},
    {"Question": "¿Qué código HTTP significa 'No encontrado'?", "Options": ["A) 200", "B) 500", "C) 404", "D) 201"], "Correct": "C"},
    {"Question": "¿Qué instrucción SQL se usa para consultar datos?", "Options": ["A) INSERT", "B) DELETE", "C) UPDATE", "D) SELECT"], "Correct": "D"},
    {"Question": "¿Qué tipo de dato guarda solo verdadero o falso?", "Options": ["A) String", "B) Integer", "C) Boolean", "D) Float"], "Correct": "C"},
    {"Question": "¿Qué protocolo cifra el tráfico web de forma segura?", "Options": ["A) HTTP", "B) FTP", "C) HTTPS", "D) SMTP"], "Correct": "C"},
]

@app.get("/")
def health_check():
    return {"status": "online", "service": "Roblox Boss API"}

def refill_cache(phase: str):
    temas_elegidos = random.sample(SUBTEMAS[phase], k=3)
    recientes = USED_QUESTIONS[-15:]
    bloque_prohibido = "\n".join(f"- {q}" for q in recientes) if recientes else "Ninguna aún."

    dificultad = "fácil a intermedio-bajo (conceptos claros y directos)" if phase == "enraged" else "muy fácil y básica (nivel estudiante principiante)"

    prompt = (
        f"Genera exactamente 10 preguntas CORTAS y FÁCILES de opción múltiple (A, B, C, D) sobre programación e ingeniería de software en español.\n"
        f"Nivel de dificultad: {dificultad}.\n"
        f"Temas a cubrir: {', '.join(temas_elegidos)}.\n"
        f"REGLAS ESTRICTAS DE LONGITUD Y FORMATO:\n"
        f"1. Cada 'Question' debe tener MÁXIMO 12 palabras (una sola oración corta y directa).\n"
        f"2. Cada opción en 'Options' debe tener MÁXIMO 4 palabras después de la letra (ej. 'A) git commit').\n"
        f"3. No repitas ni parafrasees estas preguntas recientes:\n{bloque_prohibido}\n"
        f"4. Varía la letra correcta entre A, B, C y D.\n"
        f"5. Responde ÚNICAMENTE con un JSON válido con la clave 'items', donde cada objeto tenga: "
        f"'Question' (string), 'Options' (lista de 4 strings con prefijo 'A) ', 'B) ', 'C) ', 'D) ') y 'Correct' ('A', 'B', 'C' o 'D')."
    )

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.9,
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

    item = CACHE[bucket].pop()
    USED_QUESTIONS.append(item["Question"])
    if len(USED_QUESTIONS) > 40:
        USED_QUESTIONS.pop(0)
    return item
