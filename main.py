from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models, database, auth

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="giris")

class TodoSchema(BaseModel):
    baslik: str
    tamamlandi: bool = False

class KullaniciSchema(BaseModel):
    kullanici_adi: str
    sifre: str

def aktif_kullanici(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    payload = auth.token_coz(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Geçersiz token")
    kullanici = db.query(models.Kullanici).filter(
        models.Kullanici.kullanici_adi == payload.get("sub")
    ).first()
    if not kullanici:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
    return kullanici

@app.get("/")
def ana_sayfa():
	return {"mesaj": "Merhaba FastAPI! CI/CD çalışıyor!"}

@app.post("/kayit")
def kayit(kullanici: KullaniciSchema, db: Session = Depends(database.get_db)):
    mevcut = db.query(models.Kullanici).filter(
        models.Kullanici.kullanici_adi == kullanici.kullanici_adi
    ).first()
    if mevcut:
        raise HTTPException(status_code=400, detail="Kullanıcı zaten var")
    yeni = models.Kullanici(
        kullanici_adi=kullanici.kullanici_adi,
        sifre_hash=auth.sifre_hashle(kullanici.sifre)
    )
    db.add(yeni)
    db.commit()
    return {"mesaj": "Kayıt başarılı"}

@app.post("/giris")
def giris(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    kullanici = db.query(models.Kullanici).filter(
        models.Kullanici.kullanici_adi == form.username
    ).first()
    if not kullanici or not auth.sifre_dogrula(form.password, kullanici.sifre_hash):
        raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre")
    token = auth.token_olustur({"sub": kullanici.kullanici_adi})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/todo")
def todo_ekle(todo: TodoSchema, db: Session = Depends(database.get_db), kullanici: models.Kullanici = Depends(aktif_kullanici)):
    yeni = models.Todo(baslik=todo.baslik, tamamlandi=todo.tamamlandi)
    db.add(yeni)
    db.commit()
    db.refresh(yeni)
    return {"eklendi": yeni}

@app.get("/todos")
def todos_getir(db: Session = Depends(database.get_db), kullanici: models.Kullanici = Depends(aktif_kullanici)):
    return {"todos": db.query(models.Todo).all()}

@app.delete("/todo/{id}")
def todo_sil(id: int, db: Session = Depends(database.get_db), kullanici: models.Kullanici = Depends(aktif_kullanici)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo bulunamadı")
    db.delete(todo)
    db.commit()
    return {"silindi": id}

@app.put("/todo/{id}")
def todo_guncelle(id: int, todo: TodoSchema, db: Session = Depends(database.get_db), kullanici: models.Kullanici = Depends(aktif_kullanici)):
    mevcut = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not mevcut:
        raise HTTPException(status_code=404, detail="Todo bulunamadı")
    mevcut.baslik = todo.baslik
    mevcut.tamamlandi = todo.tamamlandi
    db.commit()
    db.refresh(mevcut)
    return {"guncellendi": mevcut}
