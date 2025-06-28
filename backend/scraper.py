import asyncio
from playwright.async_api import async_playwright
import json
import time
from typing import List, Dict
from sqlalchemy.orm import Session
from database import get_db
from models import SearchHistory

class GoogleMapsScraper:
    def __init__(self):
        self.browser = None
        self.page = None

    async def setup(self, headless: bool = True):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        
        # User-Agentを設定
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    async def search_places(self, query: str, location: str = "東京") -> List[Dict]:
        """Google Mapsで店舗を検索してデータを取得"""
        if not self.page:
            await self.setup()

        search_url = f"https://www.google.com/maps/search/{query}+{location}"
        
        try:
            # Google Mapsページに移動
            await self.page.goto(search_url, wait_until="networkidle")
            await asyncio.sleep(3)

            places = []
            
            # 検索結果のコンテナを待つ
            await self.page.wait_for_selector('[role="main"]', timeout=10000)
            
            # スクロールして更多结果を読み込み
            await self._scroll_results()
            
            # 各店舗の情報を取得
            place_elements = await self.page.query_selector_all('[data-result-index]')
            
            for i, element in enumerate(place_elements[:20]):  # 最大20件
                try:
                    place_data = await self._extract_place_data(element, i)
                    if place_data:
                        places.append(place_data)
                        
                except Exception as e:
                    print(f"Error extracting place {i}: {e}")
                    continue
                    
            return places
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []

    async def _scroll_results(self):
        """結果リストをスクロールして更多データを読み込み"""
        try:
            # サイドパネルの結果リストを取得
            results_panel = await self.page.query_selector('[role="main"]')
            if results_panel:
                # 複数回スクロールして更多結果を読み込み
                for _ in range(3):
                    await self.page.evaluate('''
                        const panel = document.querySelector('[role="main"]');
                        if (panel) {
                            panel.scrollTo(0, panel.scrollHeight);
                        }
                    ''')
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"Error during scrolling: {e}")

    async def _extract_place_data(self, element, index: int) -> Dict:
        """個別の店舗データを抽出"""
        try:
            # 要素をクリックして詳細を表示
            await element.click()
            await asyncio.sleep(2)
            
            place_data = {}
            
            # 店名を取得
            name_element = await self.page.query_selector('h1')
            if name_element:
                place_data['name'] = await name_element.text_content()
            
            # 住所を取得
            address_element = await self.page.query_selector('[data-item-id="address"]')
            if address_element:
                address_text = await address_element.text_content()
                place_data['address'] = address_text.strip()
            
            # 電話番号を取得
            phone_element = await self.page.query_selector('[data-item-id*="phone"]')
            if phone_element:
                phone_text = await phone_element.text_content()
                place_data['phone'] = phone_text.strip()
            
            # 評価を取得
            rating_element = await self.page.query_selector('[role="img"][aria-label*="星"]')
            if rating_element:
                aria_label = await rating_element.get_attribute('aria-label')
                if aria_label and '星' in aria_label:
                    rating_text = aria_label.split('星')[0]
                    try:
                        place_data['rating'] = float(rating_text)
                    except:
                        pass
            
            # レビュー数を取得
            review_element = await self.page.query_selector('button[aria-label*="件のレビュー"]')
            if review_element:
                aria_label = await review_element.get_attribute('aria-label')
                if aria_label:
                    review_count = ''.join(filter(str.isdigit, aria_label.split('件')[0]))
                    if review_count:
                        place_data['review_count'] = int(review_count)
            
            # 営業時間を取得
            hours_element = await self.page.query_selector('[data-item-id="oh"]')
            if hours_element:
                hours_text = await hours_element.text_content()
                place_data['opening_hours'] = hours_text.strip()
            
            # カテゴリを取得
            category_element = await self.page.query_selector('button[jsaction*="category"]')
            if category_element:
                category_text = await category_element.text_content()
                place_data['category'] = category_text.strip()
            
            # 価格帯を取得
            price_element = await self.page.query_selector('[aria-label*="価格帯"]')
            if price_element:
                aria_label = await price_element.get_attribute('aria-label')
                place_data['price_range'] = aria_label
            
            # ウェブサイトを取得
            website_element = await self.page.query_selector('[data-item-id="authority"]')
            if website_element:
                website_link = await website_element.query_selector('a')
                if website_link:
                    place_data['website'] = await website_link.get_attribute('href')
            
            return place_data
            
        except Exception as e:
            print(f"Error extracting data for place {index}: {e}")
            return None

    async def get_place_photos(self, place_name: str) -> List[str]:
        """店舗の写真URLを取得"""
        try:
            photo_urls = []
            photo_elements = await self.page.query_selector_all('button[data-photo-index]')
            
            for photo_element in photo_elements[:5]:  # 最大5枚
                try:
                    await photo_element.click()
                    await asyncio.sleep(1)
                    
                    img_element = await self.page.query_selector('img[src*="googleusercontent"]')
                    if img_element:
                        img_src = await img_element.get_attribute('src')
                        if img_src:
                            photo_urls.append(img_src)
                    
                    # モーダルを閉じる
                    close_button = await self.page.query_selector('[aria-label="閉じる"]')
                    if close_button:
                        await close_button.click()
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    print(f"Error getting photo: {e}")
                    continue
                    
            return photo_urls
            
        except Exception as e:
            print(f"Error getting photos for {place_name}: {e}")
            return []

    async def close(self):
        """ブラウザを閉じる"""
        if self.browser:
            await self.browser.close()

async def scrape_google_maps(query: str, location: str = "東京") -> List[Dict]:
    """Google Mapsをスクレイピングして店舗情報を取得"""
    scraper = GoogleMapsScraper()
    
    try:
        await scraper.setup(headless=True)
        places = await scraper.search_places(query, location)
        
        # データベースに検索履歴を保存
        db = next(get_db())
        search_history = SearchHistory(
            query=f"{query} {location}",
            location=location,
            results_count=len(places)
        )
        db.add(search_history)
        db.commit()
        db.close()
        
        return places
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
        
    finally:
        await scraper.close()

# テスト用の実行関数
async def main():
    query = "ラーメン"
    location = "渋谷"
    
    print(f"Searching for '{query}' in '{location}'...")
    places = await scrape_google_maps(query, location)
    
    print(f"Found {len(places)} places:")
    for i, place in enumerate(places):
        print(f"\n{i+1}. {place.get('name', 'N/A')}")
        print(f"   Address: {place.get('address', 'N/A')}")
        print(f"   Rating: {place.get('rating', 'N/A')}")
        print(f"   Category: {place.get('category', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())