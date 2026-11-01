import requests

SUPABASE_URL = "https://otnjxfzttdjihjcoximm.supabase.co"
SUPABASE_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Prefer": "count=exact"
}

response = requests.get(f"{SUPABASE_URL}/rest/v1/productos?select=id", headers=headers)
content_range = response.headers.get("content-range", "Desconocido")
print(f"📊 Estado en Supabase (Rango): {content_range}")
