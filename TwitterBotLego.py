import os
import random
import requests
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session  


# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Path a imagenes 
images_path = os.getenv("IMAGES_PATH") # Ruta de la carpeta donde se guardarán las imágenes

# Variables OpenAI
api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=api_key) # Inicializa el cliente de OpenAI con API key

# Variables Twitter 
consumer_key = os.environ.get("TWITTER_API_KEY")
consumer_secret = os.environ.get("API_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")
last_image_path=""
# Encabezados para la autenticación
headers = {
    "Authorization": f"Bearer {bearer_token}"
}

""""------------------------------------------------------------------------------------------- Manejo de archivos y creacion de Prompt -----------------------------------------------------------------------------------------------"""

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
prompt = f"A lego {character} {place} {activity} {time}"
prompt_original=prompt
print("\n" + "\n" + "\n")
print(prompt)
print("\n" + "-"*80 + "\n")



""""  ------------------------------------------------------------------------------------ Llamado a API GPT para enriqueser prompt ------------------------------------------------------------------------------------------"""

def obtener_respuesta_enriquecida(prompt_inicial):
    """
    Función para enriquecer un prompt de generación de imágenes usando GPT-3.5-turbo.
    """
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative assistant, skilled in enriching prompts for image generation with vivid and specific details."},
            {"role": "user", "content": f"Enriquece este prompt para generación de imágenes: '{prompt_inicial}'. Añade detalles específicos sobre el personaje, el lugar, la actividad y el ambiente."}
        ]
    )
    respuesta_completa =completion.choices[0].message
    # Retorna el mensaje enriquecido

    return respuesta_completa.content

""""  ------------------------------------------------------------------------------------ Seleccion del prompt normal o prompt enriquesido ------------------------------------------------------------------------------------------"""
def generate_prompt(prompt):
    """
    Selecciona un prompt basado en la hora actual.
    Si es antes de las 12 del mediodía, usa el prompt normal.
    De lo contrario, usa el prompt enriquecido.
    """
    from datetime import datetime

    # Obtener la hora actual
    hora_actual = datetime.now().hour

    # Elegir el prompt basado en la hora
    if hora_actual < 12:
        return prompt
    else:

        return obtener_respuesta_enriquecida(prompt)


""""  ---------------------------------------------------------------------------------------------- Llamado a API de OpenAI ----------------------------------------------------------------------------------------------------------"""

# Generar la imagen usando la API de OpenAI
def generar_y_guardar_imagen(prompt, images_path):
    global last_image_path  # Indica que vamos a modificar la variable global

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
            print("\n" + "-"*80 + "\n")

            # Determinar el nombre autoincremental de la imagen
            existing_files = [int(f.split('Lego')[1].split('.')[0]) for f in os.listdir(images_path) if f.startswith('Lego') and f.endswith('.jpg')]
            next_file_number = max(existing_files) + 1 if existing_files else 1
            filename = f"Lego{next_file_number}.jpg"
            path_to_save_image = os.path.join(images_path, filename)

            # Intenta descargar la imagen y guardarla
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(path_to_save_image, 'wb') as file:
                        file.write(image_response.content)
                    print(f"Imagen descargada exitosamente y guardada en {path_to_save_image}")
                    print("\n" + "-"*80 + "\n")

                    last_image_path = path_to_save_image  # Actualiza la ruta de la última imagen
                else:
                    print("No se pudo descargar la imagen desde la URL.")
            except Exception as e:
                print(f"Ocurrió un error al descargar la imagen: {e}")
        else:
            print("No se encontraron imágenes en la respuesta.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


#------------------------------------------------------------------------------------ Llamado a la API de twitter ----------------------------------------------------------------------------------------------------------------------------

def upload_media_to_twitter(file_path):
    # Utiliza las variables de autenticación correctas
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret)
    url = "https://upload.twitter.com/1.1/media/upload.json"
    with open(file_path, "rb") as file:
        files = {"media": file}
        response = oauth.post(url, files=files)
    if response.status_code == 200:
        media_id = response.json()["media_id_string"]
        return media_id
    else:
        raise Exception(f"Media upload failed: {response.status_code} {response.text}")

def tweet_with_media(media_id, text):
    # Utiliza las variables de autenticación correctas
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret)
    url = "https://api.twitter.com/2/tweets"
    payload = {
        "text": text,
        "media": {
            "media_ids": [media_id]
        }
    }
    response = oauth.post(url, json=payload)
    if response.status_code == 201:
        print("Tweet posted successfully")
        print("\n" + "-"*80 + "\n")
    else:
        raise Exception(f"Failed to post tweet: {response.status_code} {response.text}")


#--------------------------------------------------------------------------------------------------- MAIN -------------------------------------------------------------------------------------------------------------------------------------------

try:
    prompt=generate_prompt(prompt)
    generar_y_guardar_imagen(prompt,images_path)
    media_id = upload_media_to_twitter(last_image_path)             # Path de la ultima imagen descargada
    tweet_text = f"{prompt_original} - Generated with Dall-e"       # Texto del tweet 
    tweet_with_media(media_id, tweet_text)                          # Publica el tweet con la imagen
except Exception as e:
    print(e)
