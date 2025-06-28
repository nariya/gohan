'use client'

import { useState } from 'react'

interface ScrapedPlace {
  id: number
  place_name: string
  place_address: string
  rating?: number
  notes: string
  created_at: string
}

export default function ScrapingSearch() {
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('東京')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<ScrapedPlace[]>([])
  const [scrapingResults, setScrapingResults] = useState<any[]>([])

  const handleScrape = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8000/api/scrape/places?query=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}`
      )
      const data = await response.json()
      
      if (data.status === 'success') {
        setScrapingResults(data.results)
        // スクレイピング後、データベースから最新のデータを取得
        await loadScrapedPlaces()
      } else {
        alert('スクレイピングに失敗しました')
      }
    } catch (error) {
      console.error('Error during scraping:', error)
      alert('エラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  const loadScrapedPlaces = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/scraped/places')
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Error loading scraped places:', error)
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
          user_id: 1, // TODO: ユーザー認証実装後に変更
          place_id: `manual_${Date.now()}`,
          place_name: place.name || place.place_name,
          place_address: place.address || place.place_address,
          latitude: 0.0,
          longitude: 0.0,
          rating: place.rating,
          notes: `スクレイピング取得: ${place.category || ''}`,
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
      <h2 className="text-2xl font-bold mb-6">詳細検索（スクレイピング）</h2>
      
      <div className="space-y-4 mb-6">
        <div className="flex space-x-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="検索キーワード（例: 美味しいラーメン）"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="場所（例: 渋谷）"
            className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <button
          onClick={handleScrape}
          disabled={loading}
          className="w-full px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors"
        >
          {loading ? 'スクレイピング中...' : '詳細検索を開始'}
        </button>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
          <p className="mt-2 text-gray-600">Google Mapsからデータを取得中...</p>
        </div>
      )}

      {scrapingResults.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">最新のスクレイピング結果</h3>
          <div className="grid gap-4">
            {scrapingResults.map((place, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{place.name}</h4>
                    <p className="text-gray-600 text-sm">{place.address}</p>
                    {place.rating && (
                      <div className="flex items-center mt-1">
                        <span className="text-yellow-400">★</span>
                        <span className="ml-1 text-sm">{place.rating}</span>
                        {place.review_count && (
                          <span className="ml-2 text-gray-500 text-sm">({place.review_count}件)</span>
                        )}
                      </div>
                    )}
                    {place.category && (
                      <p className="text-blue-600 text-sm mt-1">{place.category}</p>
                    )}
                    {place.phone && (
                      <p className="text-gray-600 text-sm">📞 {place.phone}</p>
                    )}
                    {place.opening_hours && (
                      <p className="text-gray-600 text-sm">🕒 {place.opening_hours}</p>
                    )}
                  </div>
                  <button
                    onClick={() => addToFavorites(place)}
                    className="ml-4 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    お気に入り追加
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">保存済みスクレイピングデータ</h3>
          <button
            onClick={loadScrapedPlaces}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
          >
            更新
          </button>
        </div>
        
        {results.length === 0 ? (
          <p className="text-gray-500">まだスクレイピングデータがありません</p>
        ) : (
          <div className="grid gap-3">
            {results.map((place) => (
              <div key={place.id} className="border border-gray-200 rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium">{place.place_name}</h4>
                    <p className="text-gray-600 text-sm">{place.place_address}</p>
                    {place.rating && (
                      <div className="flex items-center mt-1">
                        <span className="text-yellow-400">★</span>
                        <span className="ml-1 text-sm">{place.rating}</span>
                      </div>
                    )}
                    <p className="text-gray-500 text-xs mt-1">{place.notes}</p>
                  </div>
                  <button
                    onClick={() => addToFavorites(place)}
                    className="ml-4 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    お気に入り追加
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}