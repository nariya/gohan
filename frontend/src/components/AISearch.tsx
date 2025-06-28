'use client'

import { useState } from 'react'

interface SearchCriteria {
  keywords: string[]
  target_audience?: string
  atmosphere?: string
  price_range?: string
  cuisine_type?: string
  special_requirements: string[]
}

interface AISearchResult {
  query: string
  criteria: SearchCriteria
  summary: string
  results: any[]
  total_count: number
  search_queries_used: string[]
  status: string
}

export default function AISearch() {
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('東京')
  const [loading, setLoading] = useState(false)
  const [searchResult, setSearchResult] = useState<AISearchResult | null>(null)

  const examples = [
    "女性に受けるラーメン屋さん",
    "デートで使える高級フレンチ",
    "家族連れにおすすめのイタリアン",
    "一人でも入りやすいおしゃれなカフェ",
    "コスパの良い焼肉店",
    "インスタ映えするスイーツのお店"
  ]

  const handleSearch = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8000/api/ai/search?query=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}`
      )
      
      if (response.ok) {
        const data = await response.json()
        setSearchResult(data)
      } else {
        alert('AI検索に失敗しました')
      }
    } catch (error) {
      console.error('Error during AI search:', error)
      alert('エラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  const addToFavorites = async (place: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/favorites', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1,
          place_id: place.place_id || `ai_${Date.now()}`,
          place_name: place.name || place.place_name,
          place_address: place.vicinity || place.address || place.place_address,
          latitude: place.geometry?.location?.lat || 0.0,
          longitude: place.geometry?.location?.lng || 0.0,
          rating: place.rating,
          notes: `AI検索: ${place.ai_reason || ''}`,
        }),
      })
      
      if (response.ok) {
        alert('お気に入りに追加しました！')
      }
    } catch (error) {
      console.error('Error adding to favorites:', error)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-purple-600">AI検索</h2>
      
      {/* 検索フォーム */}
      <div className="space-y-4 mb-6">
        <div className="flex space-x-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="自然な言葉で検索してください（例: 女性に受けるラーメン屋さん）"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="場所"
            className="w-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
        
        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 transition-colors font-medium"
        >
          {loading ? 'AI分析中...' : 'AI検索を開始'}
        </button>
      </div>

      {/* 検索例 */}
      <div className="mb-8">
        <h3 className="text-sm font-medium text-gray-700 mb-3">検索例:</h3>
        <div className="flex flex-wrap gap-2">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => setQuery(example)}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* ローディング */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          <p className="mt-4 text-gray-600">AIがあなたの要求を分析しています...</p>
          <p className="text-sm text-gray-500 mt-2">複数の検索方法を試して最適な結果を見つけています</p>
        </div>
      )}

      {/* 検索結果 */}
      {searchResult && !loading && (
        <div className="space-y-6">
          {/* 検索サマリー */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h3 className="font-semibold text-purple-800 mb-2">AI分析結果</h3>
            <p className="text-purple-700 mb-3">{searchResult.summary}</p>
            
            {/* 解析された検索条件 */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              {searchResult.criteria.target_audience && (
                <div>
                  <span className="font-medium">ターゲット:</span>
                  <span className="ml-1 text-purple-600">{searchResult.criteria.target_audience}</span>
                </div>
              )}
              {searchResult.criteria.atmosphere && (
                <div>
                  <span className="font-medium">雰囲気:</span>
                  <span className="ml-1 text-purple-600">{searchResult.criteria.atmosphere}</span>
                </div>
              )}
              {searchResult.criteria.price_range && (
                <div>
                  <span className="font-medium">価格帯:</span>
                  <span className="ml-1 text-purple-600">{searchResult.criteria.price_range}</span>
                </div>
              )}
              {searchResult.criteria.cuisine_type && (
                <div>
                  <span className="font-medium">料理:</span>
                  <span className="ml-1 text-purple-600">{searchResult.criteria.cuisine_type}</span>
                </div>
              )}
            </div>
            
            <div className="mt-3 text-sm text-gray-600">
              検索キーワード: {searchResult.criteria.keywords.join(', ')}
            </div>
          </div>

          {/* 検索結果一覧 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">
              おすすめのお店 ({searchResult.total_count}件)
            </h3>
            
            {searchResult.results.length === 0 ? (
              <p className="text-gray-500">該当するお店が見つかりませんでした</p>
            ) : (
              <div className="grid gap-4">
                {searchResult.results.map((place, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-lg">{place.name || place.place_name}</h4>
                          {place.ai_score && (
                            <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                              AIスコア: {place.ai_score}
                            </span>
                          )}
                        </div>
                        
                        <p className="text-gray-600 text-sm mb-2">
                          {place.vicinity || place.address || place.place_address}
                        </p>
                        
                        {place.rating && (
                          <div className="flex items-center mb-2">
                            <span className="text-yellow-400">★</span>
                            <span className="ml-1 text-sm">{place.rating}</span>
                            {place.review_count && (
                              <span className="ml-2 text-gray-500 text-sm">({place.review_count}件)</span>
                            )}
                          </div>
                        )}
                        
                        {place.category && (
                          <p className="text-blue-600 text-sm mb-1">{place.category}</p>
                        )}
                        
                        {place.ai_reason && (
                          <p className="text-purple-600 text-sm bg-purple-50 p-2 rounded">
                            💡 {place.ai_reason}
                          </p>
                        )}
                        
                        {place.phone && (
                          <p className="text-gray-600 text-sm mt-2">📞 {place.phone}</p>
                        )}
                        
                        {place.opening_hours && (
                          <p className="text-gray-600 text-sm">🕒 {place.opening_hours}</p>
                        )}
                      </div>
                      
                      <button
                        onClick={() => addToFavorites(place)}
                        className="ml-4 px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors text-sm"
                      >
                        お気に入り追加
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 使用された検索クエリ */}
          <div className="text-sm text-gray-500">
            <details>
              <summary className="cursor-pointer hover:text-gray-700">
                使用された検索クエリを表示 ({searchResult.search_queries_used.length}個)
              </summary>
              <div className="mt-2 space-y-1">
                {searchResult.search_queries_used.map((query, index) => (
                  <div key={index} className="bg-gray-50 p-2 rounded text-xs">
                    {index + 1}. {query}
                  </div>
                ))}
              </div>
            </details>
          </div>
        </div>
      )}
    </div>
  )
}