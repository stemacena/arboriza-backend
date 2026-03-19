from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Arboriza API")

# Isso é obrigatório para permitir que o seu site no Netlify consiga acessar esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"mensagem": "A API do Arboriza em Python está online e pronta para conectar no Supabase!"}

@app.get("/status")
def status():
    return {"status": "ok", "versao": "1.0"}