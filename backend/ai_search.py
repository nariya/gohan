import openai
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class SearchCriteria:
    keywords: List[str]
    location: str
    target_audience: Optional[str]
    atmosphere: Optional[str]
    price_range: Optional[str]
    cuisine_type: Optional[str]
    special_requirements: List[str]

class AIQueryAnalyzer:
    def __init__(self):
        # DeepSeek API設定（OpenAI互換）
        self.client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
    
    async def analyze_query(self, user_query: str, location: str = "東京") -> SearchCriteria:
        """自然言語クエリを構造化された検索条件に変換"""
        
        system_prompt = """
あなたは日本の飲食店検索のエキスパートです。
ユーザーの自然言語での要求を解析して、Google Maps検索に最適化された検索条件に変換してください。

以下のJSON形式で回答してください：
{
    "keywords": ["検索キーワード1", "検索キーワード2"],
    "location": "場所",
    "target_audience": "ターゲット層（女性、カップル、家族、ビジネスマンなど）",
    "atmosphere": "雰囲気（おしゃれ、カジュアル、高級、アットホームなど）",
    "price_range": "価格帯（安い、普通、高め、高級など）",
    "cuisine_type": "料理ジャンル（ラーメン、イタリアン、和食など）",
    "special_requirements": ["特別な要求1", "特別な要求2"]
}

例：
- 「女性に受けるラーメン屋さん」→ keywords: ["ラーメン", "おしゃれ", "女性人気"], target_audience: "女性", atmosphere: "おしゃれ"
- 「デートで使える高級フレンチ」→ keywords: ["フレンチ", "高級", "デート"], target_audience: "カップル", atmosphere: "高級"
"""

        user_prompt = f"""
以下のユーザーリクエストを解析してください：
リクエスト: {user_query}
場所: {location}
"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            parsed_result = json.loads(result)
            
            return SearchCriteria(
                keywords=parsed_result.get("keywords", []),
                location=parsed_result.get("location", location),
                target_audience=parsed_result.get("target_audience"),
                atmosphere=parsed_result.get("atmosphere"),
                price_range=parsed_result.get("price_range"),
                cuisine_type=parsed_result.get("cuisine_type"),
                special_requirements=parsed_result.get("special_requirements", [])
            )
            
        except Exception as e:
            print(f"Error in AI query analysis: {e}")
            # フォールバック: 基本的な検索条件を返す
            return SearchCriteria(
                keywords=[user_query],
                location=location,
                target_audience=None,
                atmosphere=None,
                price_range=None,
                cuisine_type=None,
                special_requirements=[]
            )
    
    async def generate_search_queries(self, criteria: SearchCriteria) -> List[str]:
        """検索条件から複数の検索クエリを生成"""
        queries = []
        
        # 基本クエリ
        base_query = " ".join(criteria.keywords)
        queries.append(f"{base_query} {criteria.location}")
        
        # ターゲット層を考慮したクエリ
        if criteria.target_audience:
            queries.append(f"{criteria.target_audience} 人気 {base_query} {criteria.location}")
        
        # 雰囲気を考慮したクエリ
        if criteria.atmosphere:
            queries.append(f"{criteria.atmosphere} {base_query} {criteria.location}")
        
        # 価格帯を考慮したクエリ
        if criteria.price_range:
            queries.append(f"{criteria.price_range} {base_query} {criteria.location}")
        
        # 特別要求を考慮したクエリ
        for requirement in criteria.special_requirements:
            queries.append(f"{requirement} {base_query} {criteria.location}")
        
        return queries
    
    async def enhance_search_results(self, results: List[Dict], criteria: SearchCriteria) -> List[Dict]:
        """AIを使って検索結果を評価・フィルタリング・ランキング"""
        
        if not results:
            return results
        
        system_prompt = f"""
あなたは飲食店レビューのエキスパートです。
以下の検索条件に基づいて、店舗リストを評価し、各店舗に0-100のスコアを付けてください。

検索条件:
- ターゲット層: {criteria.target_audience or 'なし'}
- 雰囲気: {criteria.atmosphere or 'なし'}
- 価格帯: {criteria.price_range or 'なし'}
- 料理ジャンル: {criteria.cuisine_type or 'なし'}
- 特別要求: {', '.join(criteria.special_requirements) if criteria.special_requirements else 'なし'}

JSON形式で回答してください：
{
    "店舗名": {
        "score": 85,
        "reason": "評価理由"
    }
}
"""

        try:
            # 結果を文字列に変換
            results_text = ""
            for i, place in enumerate(results[:10]):  # 最大10件まで
                results_text += f"店舗{i+1}: {place.get('name', 'N/A')} - {place.get('address', 'N/A')} - 評価:{place.get('rating', 'N/A')} - カテゴリ:{place.get('category', 'N/A')}\n"
            
            user_prompt = f"以下の店舗リストを評価してください:\n{results_text}"
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_scores = json.loads(response.choices[0].message.content)
            
            # スコアを結果に追加
            for place in results:
                place_name = place.get('name', '')
                if place_name in ai_scores:
                    place['ai_score'] = ai_scores[place_name]['score']
                    place['ai_reason'] = ai_scores[place_name]['reason']
                else:
                    place['ai_score'] = 50  # デフォルトスコア
                    place['ai_reason'] = '評価なし'
            
            # AIスコアでソート
            results.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
            
        except Exception as e:
            print(f"Error in AI result enhancement: {e}")
            # フォールバック: 評価順でソート
            results.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return results
    
    async def generate_search_summary(self, query: str, criteria: SearchCriteria, results: List[Dict]) -> str:
        """検索結果のサマリーを生成"""
        
        system_prompt = """
あなたは飲食店検索結果の要約エキスパートです。
ユーザーの検索要求と結果を基に、親しみやすく有用なサマリーを生成してください。
"""

        try:
            results_summary = f"検索結果: {len(results)}件見つかりました。"
            if results:
                top_places = [place.get('name', '') for place in results[:3]]
                results_summary += f" トップ3: {', '.join(top_places)}"
            
            user_prompt = f"""
検索要求: {query}
検索条件: ターゲット層={criteria.target_audience}, 雰囲気={criteria.atmosphere}
{results_summary}

この検索結果の要約を200文字以内で生成してください。
"""
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in summary generation: {e}")
            return f"「{query}」の検索結果を{len(results)}件見つけました。"

# テスト用の実行関数
async def test_ai_search():
    analyzer = AIQueryAnalyzer()
    
    query = "女性に受けるラーメン屋さん"
    location = "渋谷"
    
    print(f"Analyzing query: {query}")
    criteria = await analyzer.analyze_query(query, location)
    
    print(f"Criteria: {criteria}")
    
    queries = await analyzer.generate_search_queries(criteria)
    print(f"Generated queries: {queries}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ai_search())