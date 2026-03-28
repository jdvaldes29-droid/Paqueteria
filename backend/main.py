from app.supabase_client import supabase
from dotenv import load_dotenv
import os

load_dotenv()

def test_connection():
    try:
        response = supabase.table("repartidores").select("*").limit(1).execute()
        print("Conexión OK. Repartidores:", response.data)
    except Exception as e:
        print("Error de conexión:", e)

def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        print("Usuario logueado:", response.user.email)
        return response
    except Exception as e:
        print("Error de login:", e)

if __name__ == "__main__":
    test_connection()