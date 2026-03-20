import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

# O Python vai pegar aquela senha secreta que você salvou no Render!
DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(title="Arboriza API")

# Permite que o Netlify converse com o Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define o formato dos dados que a árvore precisa ter
class TreeData(BaseModel):
    common_name: str
    scientific_name: str
    lat: float
    lng: float
    status: str

@app.get("/")
def home():
    return {"mensagem": "Arboriza Backend: Online e Protegido!"}

@app.post("/trees/")
def save_tree(tree: TreeData):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Banco de dados não configurado no Render.")
    
    try:
        # 1. Conecta no Supabase
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            
            # 2. Comando SQL Mágico: Salva a árvore e converte Lat/Lng em Ponto no Mapa (PostGIS)
            query = text("""
                INSERT INTO trees (common_name, scientific_name, status, geom) 
                VALUES (:cname, :sname, :status, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
            """)
            
            # 3. Executa a inserção
            conn.execute(query, {
                "cname": tree.common_name,
                "sname": tree.scientific_name,
                "status": tree.status,
                "lng": tree.lng,
                "lat": tree.lat
            })
            conn.commit() # Salva definitivamente
            
        return {"success": True, "message": f"{tree.common_name} salva com sucesso no mapa!"}
        
    except Exception as e:
        print(f"Erro no banco: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar a árvore no banco de dados.")