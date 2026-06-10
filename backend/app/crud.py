from sqlalchemy.orm import Session
from . import models, schemas  # <--- Fíjate en el punto

def crear_estacion(db: Session, estacion: schemas.EstacionCreate):
    # Toma los datos del esquema y crea el modelo de base de datos
    nueva_estacion = models.EstacionDB(
        id=estacion.id, 
        nombre=estacion.nombre, 
        ubicacion=estacion.ubicacion
    )
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return nueva_estacion

def guardar_lectura(db: Session, lectura: schemas.LecturaCreate):
    # Toma los datos del esquema y crea el registro de telemetría
    nueva_lectura = models.LecturaDB(
        valor=lectura.valor, 
        estacion_id=lectura.estacion_id
    )
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)
    return nueva_lectura
def obtener_estaciones(db: Session):
    return db.query(models.EstacionDB).all()