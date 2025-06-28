'use client'

import { useState } from 'react'
import GoogleMap from '@/components/GoogleMap'
import PlaceCard from '@/components/PlaceCard'
import ScrapingSearch from '@/components/ScrapingSearch'
import AISearch from '@/components/AISearch'

interface Place {
  place_id: string
  name: string
  vicinity: string
  rating?: number
  photos?: Array<{
    photo_reference: string
  }>
  geometry: {
    location: {
      lat: number
      lng: number
    }
  }
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('')
  const [places, setPlaces] = useState<Place[]>([])
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'normal' | 'scraping' | 'ai'>('normal')

  const searchPlaces = async () => {
    if (!searchQuery.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8000/api/search/places?query=${encodeURIComponent(searchQuery)}`
      )
      const data = await response.json()
      setPlaces(data.results || [])
    } catch (error) {
      console.error('Error searching places:', error)
    } finally {
      setLoading(false)
    }
  }

  const addToFavorites = async (place: Place) => {
    try {
      const response = await fetch('http://localhost:8000/api/favorites', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1, // TODO: Implement user authentication
          place_id: place.place_id,
          place_name: place.name,
          place_address: place.vicinity,
          latitude: place.geometry.location.lat,
          longitude: place.geometry.location.lng,
          rating: place.rating,
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
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">GohanMap</h1>
        
        {/* タブ切り替え */}
        <div className="flex justify-center mb-8">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('normal')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === 'normal' 
                  ? 'bg-white text-blue-600 shadow' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              通常検索
            </button>
            <button
              onClick={() => setActiveTab('ai')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === 'ai' 
                  ? 'bg-white text-purple-600 shadow' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              AI検索
            </button>
            <button
              onClick={() => setActiveTab('scraping')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === 'scraping' 
                  ? 'bg-white text-green-600 shadow' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              詳細検索
            </button>
          </div>
        </div>

        {activeTab === 'scraping' ? (
          <ScrapingSearch />
        ) : activeTab === 'ai' ? (
          <AISearch />
        ) : (
          <>
            <div className="max-w-2xl mx-auto mb-8">
          <div className="flex space-x-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="お店を検索（例: ラーメン、寿司、カフェ）"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && searchPlaces()}
            />
            <button
              onClick={searchPlaces}
              disabled={loading}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
            >
              {loading ? '検索中...' : '検索'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <GoogleMap 
              places={places} 
              onPlaceSelect={setSelectedPlace}
            />
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">検索結果</h2>
            {places.length === 0 && !loading && (
              <p className="text-gray-500">検索してお店を探してみましょう！</p>
            )}
            {places.map((place) => (
              <PlaceCard
                key={place.place_id}
                place={place}
                onAddToFavorites={addToFavorites}
              />
            ))}
          </div>
        </div>

        {selectedPlace && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
              <h3 className="text-xl font-semibold mb-4">{selectedPlace.name}</h3>
              <p className="text-gray-600 mb-4">{selectedPlace.vicinity}</p>
              {selectedPlace.rating && (
                <div className="flex items-center mb-4">
                  <span className="text-yellow-400">★</span>
                  <span className="ml-1">{selectedPlace.rating}</span>
                </div>
              )}
              <div className="flex space-x-4">
                <button
                  onClick={() => addToFavorites(selectedPlace)}
                  className="flex-1 bg-blue-500 text-white py-2 rounded hover:bg-blue-600 transition-colors"
                >
                  お気に入りに追加
                </button>
                <button
                  onClick={() => setSelectedPlace(null)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400 transition-colors"
                >
                  閉じる
                </button>
              </div>
            </div>
          </div>
        )}
        </>
        )}
      </div>
    </div>
  )
}
