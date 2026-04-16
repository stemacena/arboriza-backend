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

class TreeData(BaseModel):
    common_name: str
    scientific_name: str
    lat: float
    lng: float
    status: str
    user_uid: str 
    cover_photo: str

@app.get("/")
def home():
    return {"mensagem": "Arboriza Backend: Online e Protegido!"}

@app.post("/trees/")
def save_tree(tree: TreeData):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Banco não configurado.")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            
            # =================================================================
            # 🧠 INTELIGÊNCIA GEOGRÁFICA: Cruzando a árvore com o MapBiomas!
            # =================================================================
            bioma_query = text("""
                SELECT classe FROM mapbiomas_rio 
                WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
                LIMIT 1
            """)
            resultado_bioma = conn.execute(bioma_query, {"lng": tree.lng, "lat": tree.lat}).fetchone()
            
            # Se a árvore caiu dentro do polígono, pegamos o nome. Se não, é "Área Desconhecida".
            historico_solo = resultado_bioma[0] if resultado_bioma else "Área ainda não mapeada"
            
            # Salva a árvore normalmente
            query = text("""
                INSERT INTO trees (common_name, scientific_name, status, user_uid, cover_photo, geom) 
                VALUES (:cname, :sname, :status, :uid, :photo, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
            """)
            conn.execute(query, {
                "cname": tree.common_name, "sname": tree.scientific_name,
                "status": tree.status, "uid": tree.user_uid,
                "photo": tree.cover_photo, "lng": tree.lng, "lat": tree.lat
            })
            conn.commit() 
            
        # Devolvemos a resposta de sucesso JÁ COM O DADO DO MAPBIOMAS!
        return {
            "success": True, 
            "message": f"Árvore salva!", 
            "mapbiomas_classe": historico_solo
        }
        
    except Exception as e:
        print(f"Erro no banco: {e}")
        raise HTTPException(status_code=500, detail="Erro no banco.")