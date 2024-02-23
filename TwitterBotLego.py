import os
import random
from openai import OpenAI
from dotenv import load_dotenv


# Carga las variables de entorno desde el archivo .env
load_dotenv()
api_key = os.getenv("API_KEY")

# Inicializa el cliente de OpenAI con API key
openai = OpenAI(api_key=api_key)

""""  ------------------------------------------------------------------------- Manejo de archivos y creacion de Prompt ------------------------------------------------------------------------------------------------------------------------------------"""

# Función para leer un dato aleatorio de un archivo
def read_random_line(filename):
    # Construye la ruta completa al archivo basado en la ubicación del script
    base_path = os.path.dirname(__file__)  # Obtiene la carpeta donde se encuentra el script
    file_path = os.path.join(base_path, "Prompts", filename)  # Construye la ruta al archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()
    return random.choice(lines)

# Leer un dato aleatorio de cada archivo
time = read_random_line('time.txt')
place = read_random_line('places.txt')
character = read_random_line('character.txt')
activity = read_random_line('activity.txt')


# Formar el prompt
prompt = f"A lego {character} in {place} {activity} {time}"
print(prompt)

# saltos de línea 
print("\n" + "-"*80 + "\n")

""""  ------------------------------------------------------------------------- Llamado a API de OpenAI ------------------------------------------------------------------------------------------------------------------------------------"""

# Intento de generar la imagen usando la API de OpenAI
try:
    # Ajusta este método según la documentación oficial actual de OpenAI
    response = openai.images.generate(
    model="dall-e-3",  # Usando DALL·E 3
    prompt=prompt,
    n=1,
    size="1024x1024",
    quality="hd"  # Especificando calidad HD
)

    # La estructura exacta de cómo acceder a la URL puede variar, este es un ejemplo genérico
    # Comprobación y extracción de la URL de la imagen de la respuesta
    if response.data and len(response.data) > 0:
        image_url = response.data[0].url  # Ajusta según la estructura real
        print(image_url)
    else:
        print("No se encontraron imágenes en la respuesta.")
except Exception as e:
    print(f"Ocurrió un error: {e}")













""""  ------------------------------------------------------------------------- Llamado a chat GPT-3 Funciona ------------------------------------------------------------------------------------------------------------------------------------
def obtener_respuesta():
    prompt = "Calcula el porcentaje del año que ha transcurrido."
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message

    respuesta = obtener_respuesta()
    print(respuesta)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""     