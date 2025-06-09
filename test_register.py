import requests
import json

def test_register():
    url = "http://localhost:8000/auth/register"
    data = {
        "email": "waltercarrasco@mail.com",
        "password": "Secure123!",  # Cumple con los requisitos de seguridad
        "confirm_password": "Secure123!",
        "rol": "comprador"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_register()
