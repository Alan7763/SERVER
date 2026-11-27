from google import genai

client = genai.Client(api_key="AQ.Ab8RN6JZ8cG5g5I1gLeZlY7CuN-UCYvmuGED9b_SekNxm46BUw")

try:
    print("Consultando modelos disponibles...")
    # El método correcto en la nueva versión es list()
    for model in client.models.list():
        # Filtramos para que solo nos muestre los modelos de la familia Gemini
        if "gemini" in model.name:
            print(model.name)
except Exception as e:
    print(f"Error de acceso: {e}")