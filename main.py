from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

class TodoSchema(BaseModel):
    baslik: str
    tamamlandi: bool = False

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Merhaba FastAPI!"}

@app.post("/todo")
def todo_ekle(todo: TodoSchema, db: Session = Depends(database.get_db)):
    yeni = models.Todo(baslik=todo.baslik, tamamlandi=todo.tamamlandi)
    db.add(yeni)
    db.commit()
    db.refresh(yeni)
    return {"eklendi": yeni}

@app.get("/todos")
def todos_getir(db: Session = Depends(database.get_db)):
    return {"todos": db.query(models.Todo).all()}

@app.delete("/todo/{id}")
def todo_sil(id: int, db: Session = Depends(database.get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo bulunamadı")
    db.delete(todo)
    db.commit()
    return {"silindi": id}

@app.put("/todo/{id}")
def todo_guncelle(id: int, todo: TodoSchema, db: Session = Depends(database.get_db)):
    mevcut = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not mevcut:
        raise HTTPException(status_code=404, detail="Todo bulunamadı")
    mevcut.baslik = todo.baslik
    mevcut.tamamlandi = todo.tamamlandi
    db.commit()
    db.refresh(mevcut)
    return {"guncellendi": mevcut}
