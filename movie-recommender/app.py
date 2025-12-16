import sys
import os
from pathlib import Path
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# --- 1. AI RECOMMENDER MODÜLÜNÜ TANITMA ---
# ai_recommender klasörünü python'un görebilmesi için yol ekliyoruz
# --- DÜZELTİLEN KISIM BAŞLANGIÇ ---
# app.py dosyasının nerede olduğunu bul
current_dir = os.path.dirname(os.path.abspath(__file__))

# Bir üst klasörü (Proje Ana Dizinini) bul
root_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Ana dizini Python'un arama yollarına ekle
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Ayrıca ai_recommender klasörünü de açıkça ekleyelim (Garanti olsun)
ai_rec_path = os.path.join(root_dir, 'ai_recommender')
if ai_rec_path not in sys.path:
    sys.path.append(ai_rec_path)
# --- DÜZELTİLEN KISIM BİTİŞ ---

# Senin recommender.py dosyanı import ediyoruz
# (Not: ai_recommender klasöründe __init__.py dosyası olduğundan emin ol)
try:
    from ai_recommender.recommender import ItemBasedRecommender
except ImportError as e:
    print(f"UYARI: Recommender modülü bulunamadı. Hata: {e}")
    ItemBasedRecommender = None

app = FastAPI(title="Movie Recommender API")

# CORS (Frontend'in bağlanabilmesi için izinler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. VERİLERİN YÜKLENMESİ (Arkadaşının kodu) ---
DATA_DIR = Path("data/processed")
ASSETS_DIR = DATA_DIR / "api_assets"

# Dosya yolları
MASTER_CSV = DATA_DIR / "movies_master.csv"
BASE_CSV = DATA_DIR / "movies_base.csv"
POPULAR_PATH = ASSETS_DIR / "popular_100.json"
GENRES_PATH = ASSETS_DIR / "genres.json"
SEARCH_PATH = ASSETS_DIR / "search_index.csv"

def load_movies_df() -> pd.DataFrame:
    """Film detaylarını hafızaya yükler (ID -> Title/Poster çevrimi için)"""
    if MASTER_CSV.exists():
        print(f"Yükleniyor: {MASTER_CSV}")
        df = pd.read_csv(MASTER_CSV)
    elif BASE_CSV.exists():
        print(f"Yükleniyor: {BASE_CSV}")
        df = pd.read_csv(BASE_CSV)
    else:
        # Dosya yoksa boş bir dataframe oluştur ki hata vermesin
        print("UYARI: Film CSV dosyaları bulunamadı!")
        return pd.DataFrame()
    
    # Veri tiplerini düzelt
    if "movieId" in df.columns:
        df["movieId"] = df["movieId"].astype(int)
        df = df.set_index("movieId", drop=False) # Hızlı arama için index yapıyoruz
    
    # Eksik sütunları doldur (Hata almamak için)
    for col in ["poster_url", "overview", "title_clean", "year", "genres", "rating_mean"]:
        if col not in df.columns:
            df[col] = ""
            
    return df

# Verileri Başlat
MOVIES = load_movies_df()

# JSON verilerini yükle
try:
    with open(POPULAR_PATH, "r", encoding="utf-8") as f:
        POPULAR_100 = json.load(f)
except Exception:
    POPULAR_100 = []

try:
    with open(GENRES_PATH, "r", encoding="utf-8") as f:
        GENRES_LIST = json.load(f)
except Exception:
    GENRES_LIST = []

# --- 3. MODELİN BAŞLATILMASI ---
print("🧠 Yapay Zeka Modeli Yükleniyor...")
try:
    # Model sınıfını başlatıyoruz. Bu işlem .pkl dosyalarını okur.
    rec_model = ItemBasedRecommender()
    print("✅ Model başarıyla yüklendi.")
except Exception as e:
    print(f"❌ Model yüklenirken hata oluştu: {e}")
    rec_model = None


# --- 4. İSTEK MODELLERİ (Frontend'den ne bekliyoruz?) ---
class RecommendationRequest(BaseModel):
    liked_movie_ids: List[int] # Kullanıcının sevdiği film ID'leri
    top_k: int = 10            # Kaç öneri istiyor?

# --- ENDPOINTLER ---

@app.get("/")
def home():
    return {"message": "Movie Recommender API is running!", "model_status": "Active" if rec_model else "Inactive"}

@app.get("/movies/popular")
def get_popular():
    return POPULAR_100

@app.get("/movies/genres")
def get_genres():
    return GENRES_LIST

@app.get("/movies/{movie_id}")
def get_movie_detail(movie_id: int):
    if movie_id not in MOVIES.index:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    row = MOVIES.loc[movie_id]
    return row.to_dict() # Tüm satırı JSON olarak dön

# --- KRİTİK NOKTA: ÖNERİ ENDPOINT'İ ---
@app.post("/recommend")
def recommend_movies(payload: RecommendationRequest):
    """
    Frontend'den sevilen filmleri alır, yapay zekaya sorar,
    gelen ID'leri resim ve başlıklarla süsleyip geri döner.
    """
    # 1. Model Kontrolü
    if rec_model is None:
        raise HTTPException(status_code=503, detail="Öneri modeli şu an aktif değil.")

    # 2. Yapay Zekadan ID'leri iste
    try:
        recommended_ids = rec_model.get_recommendations(
            liked_movie_ids=payload.liked_movie_ids,
            top_k=payload.top_k
        )
    except Exception as e:
        # Model bir hata yaparsa (örneğin ID bulamazsa)
        print(f"Öneri hatası: {e}")
        return []

    # 3. ID'leri Detaylı Veriye Çevir (Enrichment)
    results = []
    for mid in recommended_ids:
        if mid in MOVIES.index:
            movie_data = MOVIES.loc[mid].to_dict()
            
            # Gereksiz veya NaN olan alanları temizle (Frontend hatası olmasın diye)
            clean_data = {
                "movieId": int(movie_data["movieId"]),
                "title": str(movie_data.get("title", "")),
                "poster_url": str(movie_data.get("poster_url", "")),
                "year": int(movie_data["year"]) if pd.notna(movie_data.get("year")) else None,
                "genres": str(movie_data.get("genres", "")),
                "rating_mean": float(movie_data.get("rating_mean", 0))
            }
            results.append(clean_data)
            
    return results

# Arama Endpointi (Basit)
@app.get("/search")
def search_movies(q: str):
    if not q:
        return []
    
    q = q.lower()
    # Başlığında arama terimi geçen ilk 10 filmi getir
    mask = MOVIES["title"].str.lower().str.contains(q, na=False)
    results = MOVIES[mask].head(10).to_dict(orient="records")
    return results