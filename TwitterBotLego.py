import os
import random
import requests
from openai import OpenAI
from dotenv import load_dotenv


# Carga las variables de entorno desde el archivo .env
load_dotenv()
api_key = os.getenv("API_KEY")
images_path = os.getenv("IMAGES_PATH") # Ruta de la carpeta donde se guardarán las imágenes

# Inicializa el cliente de OpenAI con API key
openai = OpenAI(api_key=api_key)

""""------------------------------------------------------------------------- Manejo de archivos y creacion de Prompt ------------------------------------------------------------------------------------------------------------------------------------"""

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

# Generar la imagen usando la API de OpenAI
try:
    response = openai.images.generate(
    model="dall-e-3",  # Usando DALL·E 3
    prompt=prompt,
    n=1,
    size="1024x1024",
    quality="standard" 
)

    if response.data:
        image_url = response.data[0].url
        print(f"URL de la imagen: {image_url}")

        # Determinar el nombre autoincremental de la imagen
        existing_files = [int(f.split('Lego')[1].split('.')[0]) for f in os.listdir(images_path) if f.startswith('Lego') and f.endswith('.jpg')]
        next_file_number = max(existing_files) + 1 if existing_files else 1
        filename = f"Lego{next_file_number}.jpg"
        path_to_save_image = os.path.join(images_path, filename)

        # Descargar la imagen y guardarla en la ruta especificada
        try:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                with open(path_to_save_image, 'wb') as file:
                    file.write(image_response.content)
                print(f"Imagen descargada exitosamente y guardada en {path_to_save_image}")
            else:
                print("No se pudo descargar la imagen desde la URL.")
        except Exception as e:
            print(f"Ocurrió un error al descargar la imagen: {e}")
    else:
        print("No se encontraron imágenes en la respuesta.")

except Exception as e:
    print(f"Ocurrió un error: {e}")

