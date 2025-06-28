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

interface PlaceCardProps {
  place: Place
  onAddToFavorites: (place: Place) => void
}

export default function PlaceCard({ place, onAddToFavorites }: PlaceCardProps) {
  const photoUrl = place.photos?.[0] 
    ? `https://maps.googleapis.com/maps/api/place/photo?maxwidth=300&photoreference=${place.photos[0].photo_reference}&key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}`
    : '/placeholder-restaurant.jpg'

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex space-x-4">
        <img 
          src={photoUrl} 
          alt={place.name}
          className="w-20 h-20 object-cover rounded-lg"
          onError={(e) => {
            (e.target as HTMLImageElement).src = '/placeholder-restaurant.jpg'
          }}
        />
        <div className="flex-1">
          <h3 className="font-semibold text-lg">{place.name}</h3>
          <p className="text-gray-600 text-sm">{place.vicinity}</p>
          {place.rating && (
            <div className="flex items-center mt-1">
              <span className="text-yellow-400">★</span>
              <span className="ml-1 text-sm">{place.rating}</span>
            </div>
          )}
          <button
            onClick={() => onAddToFavorites(place)}
            className="mt-2 bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
          >
            お気に入りに追加
          </button>
        </div>
      </div>
    </div>
  )
}