import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(title="Arboriza API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Adicionamos o user_uid no formato esperado
class TreeData(BaseModel):
    common_name: str
    scientific_name: str
    lat: float
    lng: float
    status: str
    user_uid: str 

@app.get("/")
def home():
    return {"mensagem": "Arboriza Backend: Online e Protegido!"}

@app.post("/trees/")
def save_tree(tree: TreeData):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Banco de dados não configurado no Render.")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            
            # 2. Adicionamos a coluna user_uid no comando SQL
            query = text("""
                INSERT INTO trees (common_name, scientific_name, status, user_uid, geom) 
                VALUES (:cname, :sname, :status, :uid, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
            """)
            
            # 3. Enviamos o dado para o banco
            conn.execute(query, {
                "cname": tree.common_name,
                "sname": tree.scientific_name,
                "status": tree.status,
                "uid": tree.user_uid,
                "lng": tree.lng,
                "lat": tree.lat
            })
            conn.commit() 
            
        return {"success": True, "message": f"{tree.common_name} salva com sucesso no mapa!"}
        
    except Exception as e:
        print(f"Erro no banco: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar a árvore no banco de dados.")