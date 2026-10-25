import requests
from bs4 import BeautifulSoup

url = "https://neoimport.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Conectando a Neo Import...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    print("¡Conexión exitosa! Analizando estructura...")

    # NOTA: Las clases o etiquetas (como 'product', 'price', etc.) 
    # dependen de cómo esté construida la web de Neo Import.
    # Aquí puedes buscar los contenedores de productos.
    productos = soup.find_all('div') # Ajustar según el selector real de la página
    print(f"Se encontraron elementos en la página principal.")
else:
    print(f"Error al acceder a la página. Código: {response.status_code}")
