# test_openai.py
import os
from dotenv import load_dotenv
import openai

# Charger les variables d'environnement
load_dotenv()

# Configurer la clé API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Test simple
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ]
    )
    print("Connexion réussie!")
    print("Réponse:", response.choices[0].message['content'])
except Exception as e:
    print("Erreur:", e)