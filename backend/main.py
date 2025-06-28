from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import requests
from database import get_db, init_db
from models import User, Favorite, SearchHistory
from schemas import UserCreate, FavoriteCreate, SearchHistoryCreate, PlaceSearchResponse
from scraper import scrape_google_maps
from ai_search import AIQueryAnalyzer

load_dotenv()

app = FastAPI(title="GohanMap API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"message": "GohanMap API"}

@app.post("/api/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/search/places")
async def search_places(
    query: str,
    location: str = "35.6762,139.6503",  # Tokyo default
    radius: int = 5000,
    db: Session = Depends(get_db)
):
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(status_code=500, detail="Google Maps API key not configured")
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": radius,
        "keyword": query,
        "type": "restaurant",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch places")
    
    data = response.json()
    
    # Save search history
    search_history = SearchHistory(
        query=query,
        location=location,
        results_count=len(data.get("results", []))
    )
    db.add(search_history)
    db.commit()
    
    return data

@app.post("/api/favorites")
async def add_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    db_favorite = Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

@app.get("/api/favorites/{user_id}")
async def get_favorites(user_id: int, db: Session = Depends(get_db)):
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    return favorites

@app.get("/api/history")
async def get_search_history(limit: int = 10, db: Session = Depends(get_db)):
    history = db.query(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(limit).all()
    return history

@app.get("/api/scrape/places")
async def scrape_places(
    query: str,
    location: str = "東京",
    db: Session = Depends(get_db)
):
    """Playwrightを使ってGoogle Mapsから店舗情報をスクレイピング"""
    try:
        places = await scrape_google_maps(query, location)
        
        # スクレイピング結果をデータベースに保存
        for place in places:
            if place.get('name'):
                # 重複チェック（店名と住所で判定）
                existing = db.query(Favorite).filter(
                    Favorite.place_name == place['name'],
                    Favorite.place_address == place.get('address', '')
                ).first()
                
                if not existing:
                    # お気に入りテーブルに一時保存（user_id=0 でスクレイピングデータとして区別）
                    scraped_place = Favorite(
                        user_id=0,  # スクレイピングデータ用のuser_id
                        place_id=f"scraped_{hash(place['name'] + place.get('address', ''))}",
                        place_name=place['name'],
                        place_address=place.get('address', ''),
                        latitude=0.0,  # 座標は後で取得
                        longitude=0.0,
                        rating=place.get('rating'),
                        notes=f"Category: {place.get('category', 'N/A')}, Phone: {place.get('phone', 'N/A')}, Hours: {place.get('opening_hours', 'N/A')}"
                    )
                    db.add(scraped_place)
        
        db.commit()
        return {
            "results": places,
            "count": len(places),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/api/scraped/places")
async def get_scraped_places(limit: int = 50, db: Session = Depends(get_db)):
    """スクレイピングで取得した店舗一覧を返す"""
    scraped_places = db.query(Favorite).filter(Favorite.user_id == 0).limit(limit).all()
    return scraped_places

@app.get("/api/ai/search")
async def ai_search_places(
    query: str,
    location: str = "東京",
    db: Session = Depends(get_db)
):
    """AIを使って自然言語クエリを解析し、最適な検索を実行"""
    analyzer = AIQueryAnalyzer()
    
    try:
        # 1. 自然言語クエリを解析
        criteria = await analyzer.analyze_query(query, location)
        
        # 2. 検索クエリを生成
        search_queries = await analyzer.generate_search_queries(criteria)
        
        all_results = []
        
        # 3. 複数の検索方法を試行
        for search_query in search_queries[:3]:  # 最大3つのクエリ
            try:
                # Google Maps API検索
                if GOOGLE_MAPS_API_KEY:
                    api_results = await search_with_google_api(search_query, location)
                    all_results.extend(api_results)
                
                # スクレイピング検索（時間がかかるので1つだけ）
                if len(all_results) < 10:
                    scraping_results = await scrape_google_maps(search_query, location)
                    all_results.extend(scraping_results)
                    
            except Exception as e:
                print(f"Error in search query '{search_query}': {e}")
                continue
        
        # 4. 重複除去
        unique_results = []
        seen_names = set()
        for result in all_results:
            name = result.get('name', '')
            if name and name not in seen_names:
                seen_names.add(name)
                unique_results.append(result)
        
        # 5. AIで結果を評価・ランキング
        enhanced_results = await analyzer.enhance_search_results(unique_results, criteria)
        
        # 6. サマリー生成
        summary = await analyzer.generate_search_summary(query, criteria, enhanced_results)
        
        # 7. 検索履歴を保存
        search_history = SearchHistory(
            query=f"AI: {query}",
            location=location,
            results_count=len(enhanced_results)
        )
        db.add(search_history)
        db.commit()
        
        return {
            "query": query,
            "criteria": {
                "keywords": criteria.keywords,
                "target_audience": criteria.target_audience,
                "atmosphere": criteria.atmosphere,
                "price_range": criteria.price_range,
                "cuisine_type": criteria.cuisine_type,
                "special_requirements": criteria.special_requirements
            },
            "summary": summary,
            "results": enhanced_results[:20],  # 最大20件
            "total_count": len(enhanced_results),
            "search_queries_used": search_queries,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI search failed: {str(e)}")

async def search_with_google_api(query: str, location: str) -> list:
    """Google Maps APIで検索（内部関数）"""
    try:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": "35.6762,139.6503",  # デフォルト座標
            "radius": 5000,
            "keyword": query,
            "type": "restaurant",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        
    except Exception as e:
        print(f"Google API search error: {e}")
    
    return []