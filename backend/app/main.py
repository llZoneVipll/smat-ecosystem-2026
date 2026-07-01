from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.auth import crear_token_acceso, obtener_identidad_actual

# IMPORTACIONES RELATIVAS PROFESIONALES
# El punto '.' indica que los archivos están en la misma carpeta /app
from . import models, schemas, crud 
from .database import engine, get_db

# Inicialización de la base de datos (Laboratorio 4.3) [cite: 147, 148]
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
API RESTful para la gestión y monitoreo de desastres naturales (FISI - UNMSM).
Seguridad Avanzada: Implementación de JWT y Protección de Endpoints.
    """,
    version="1.1.0"
)

# CONFIGURACIÓN DE SEGURIDAD (Middleware CORS - Laboratorio 4.3) [cite: 161-167]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# ENDPOINTS DE SEGURIDAD (Laboratorio 4.4)
# ==========================================================

@app.post("/token", tags=["Seguridad"])
async def login_para_obtener_token():
    """
    Endpoint para simular el inicio de sesión y obtener un Token JWT válido [cite: 64-67].
    """
    # Se genera un token con el sujeto "admin_smat" [cite: 67]
    return {"access_token": crear_token_acceso({"sub": "admin_smat"}), "token_type": "bearer"}

# ==========================================================
# ENDPOINTS DE NEGOCIO (CONTROLADORES)
# ==========================================================

@app.post("/estaciones/", status_code=201, tags=["Gestión de Infraestructura"])
def crear_estacion(
    estacion: schemas.EstacionCreate, 
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_identidad_actual) # PROTECCIÓN JWT [cite: 74]
):
    # Delegamos la creación al módulo CRUD [cite: 75]
    estacion_creada = crud.crear_estacion(db=db, estacion=estacion)
    return {"msj": "Estación guardada en DB", "data": estacion_creada}

@app.get("/estaciones/", tags=["Gestión de Infraestructura"])
def listar_estaciones(db: Session = Depends(get_db)):
    """
    Endpoint necesario para que la App Móvil liste las estaciones.
    """
    estaciones = crud.obtener_estaciones(db)
    return estaciones

@app.post("/lecturas/", status_code=201, tags=["Telemetría de Sensores"])
def registrar_lectura(
    lectura: schemas.LecturaCreate, 
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_identidad_actual) # PROTECCIÓN JWT [cite: 90]
):
    # RETO DE INTEGRIDAD: Validación Cruzada (Laboratorio 4.4) [cite: 91-97]
    # Antes de guardar, verificamos que el estacion_id realmente exista en la DB [cite: 94, 95]
    estacion_db = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    
    if not estacion_db:
        raise HTTPException(
            status_code=404, 
            detail="Error de Integridad: La estación no existe en la base de datos."
        )
    
    # Delegamos el guardado al módulo CRUD
    crud.guardar_lectura(db=db, lectura=lectura)
    return {"status": "Lectura guardada con éxito en DB"}

@app.get("/estaciones/{id}/riesgo", tags=["Análisis de Riesgo"])
def evaluar_riesgo(id: int, db: Session = Depends(get_db)):
    """
    Evalúa el nivel de criticidad basado en la última lectura reportada.
    """
    ultima_lectura = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).order_by(models.LecturaDB.id.desc()).first()
    
    if not ultima_lectura:
        raise HTTPException(status_code=404, detail="No hay lecturas registradas para esta estación")
    
    # Lógica de criticidad para el reto de alertas
    estado = "NORMAL"
    if ultima_lectura.valor > 50: 
        estado = "PELIGRO"
    elif ultima_lectura.valor > 30: 
        estado = "ALERTA"
        
    return {"estacion_id": id, "ultimo_valor": ultima_lectura.valor, "nivel_riesgo": estado}

@app.get("/estaciones/{id}/historial", tags=["Reportes Analíticos"])
def obtener_historial(id: int, db: Session = Depends(get_db)):
    historial = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).all()
    if not historial:
        raise HTTPException(status_code=404, detail="La estación no cuenta con historial de lecturas")
    return {"estacion_id": id, "historial": historial}

@app.get("/estaciones/dashboard", tags=["Auditoría"])
def obtener_dashboard(db: Session = Depends(get_db)):
    """
    Reto Final: Resumen del estado del ecosistema (Laboratorio 4.3)[cite: 168, 169].
    """
    total_estaciones = db.query(models.EstacionDB).count() # [cite: 177]
    total_lecturas = db.query(models.LecturaDB).count() # [cite: 178]
    
    # Búsqueda del punto crítico máximo [cite: 179]
    lectura_max = db.query(models.LecturaDB).order_by(models.LecturaDB.valor.desc()).first()
    punto_critico = None
    if lectura_max:
        estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura_max.estacion_id).first()
        punto_critico = {
            "estacion_id": lectura_max.estacion_id,
            "nombre_estacion": estacion.nombre if estacion else "Desconocida",
            "valor_maximo": lectura_max.valor
        }
        
    return {
        "total_estaciones_monitoreadas": total_estaciones,
        "total_lecturas_procesadas": total_lecturas,
        "punto_critico_maximo": punto_critico
    }