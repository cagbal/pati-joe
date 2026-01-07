import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

# --- Configuration ---
SECRET_KEY = "supersecretkey" # Demo icin basit key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DATABASE_URL = "sqlite:///./pati_joe.db"

# --- Database Setup ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_sitter = Column(Boolean, default=False)
    
    profile = relationship("Profile", back_populates="user", uselist=False)
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String)
    city = Column(String, index=True)
    price = Column(Float)
    weight_limit = Column(Integer) # kg
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="profile")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

Base.metadata.create_all(bind=engine)

# --- Schemas ---
class ProfileUpdate(BaseModel):
    full_name: str
    city: str
    price: float
    weight_limit: int
    bio: str
    is_active: bool

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

# --- Security ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Bearer prefix'ini temizle
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

async def get_current_active_user(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# --- App ---
app = FastAPI(title="Pati-joe")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Startup Event (Demo Data) ---
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "demo").first():
        print("Creating demo data...")
        # Create Demo User (Sitter)
        demo_user = User(username="demo", hashed_password=get_password_hash("demo123"), is_sitter=True)
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        demo_profile = Profile(
            user_id=demo_user.id,
            full_name="Demo Bakıcı",
            city="Istanbul",
            price=250.0,
            weight_limit=15,
            bio="Merhaba! Ben demo bakıcıyım. Köpeklere bayılırım.",
            is_active=True
        )
        db.add(demo_profile)

        # Create some other dummy sitters
        sitters_data = [
            {"u": "ali", "p": "ali123", "name": "Ali Veli", "city": "Ankara", "price": 150.0, "w": 30, "bio": "Ankara'da genis bahceli evim var."},
            {"u": "ayse", "p": "ayse123", "name": "Ayşe Yılmaz", "city": "Izmir", "price": 300.0, "w": 10, "bio": "Kucuk irk kopekler uzmanlik alanim."},
            {"u": "mehmet", "p": "mehmet123", "name": "Mehmet Can", "city": "Istanbul", "price": 400.0, "w": 50, "bio": "Buyuk irklarla cok iyi anlasirim. Kadikoydeyim."},
            {"u": "zeynep", "p": "zeynep123", "name": "Zeynep Su", "city": "Antalya", "price": 200.0, "w": 20, "bio": "Aktif ve enerjik bir bakiciyim."},
        ]

        for data in sitters_data:
            u = User(username=data["u"], hashed_password=get_password_hash(data["p"]), is_sitter=True)
            db.add(u)
            db.commit()
            db.refresh(u)
            p = Profile(
                user_id=u.id,
                full_name=data["name"],
                city=data["city"],
                price=data["price"],
                weight_limit=data["w"],
                bio=data["bio"],
                is_active=True
            )
            db.add(p)
        
        db.commit()
    db.close()

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request, 
    city: Optional[str] = None, 
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Profile).filter(Profile.is_active == True)
    
    if city:
        query = query.filter(Profile.city.ilike(f"%{city}%"))
    if max_price:
        query = query.filter(Profile.price <= max_price)
    
    profiles = query.all()
    user = await get_current_user(request, db)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "profiles": profiles, 
        "user": user,
        "search_city": city,
        "search_price": max_price
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    
    # Eger profili yoksa (sadece usersa) olusturmasi gerekebilir ama demo icin var varsayiyoruz
    if not profile and user.is_sitter:
        # Otomatik bos profil olustur
        profile = Profile(user_id=user.id, full_name=user.username, city="", price=0, weight_limit=0, bio="", is_active=False)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    received_msgs = db.query(Message).filter(Message.receiver_id == user.id).order_by(Message.id.desc()).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "profile": profile,
        "messages": received_msgs
    })

@app.put("/api/profile")
async def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.full_name = data.full_name
    profile.city = data.city
    profile.price = data.price
    profile.weight_limit = data.weight_limit
    profile.bio = data.bio
    profile.is_active = data.is_active
    
    db.commit()
    return {"status": "success"}

@app.post("/api/messages")
async def send_message(data: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    if user.id == data.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")
        
    msg = Message(sender_id=user.id, receiver_id=data.receiver_id, content=data.content)
    db.add(msg)
    db.commit()
    return {"status": "sent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
