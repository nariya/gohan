'use client'

import { useEffect, useRef, useState } from 'react'

interface Place {
  place_id: string
  name: string
  geometry: {
    location: {
      lat: number
      lng: number
    }
  }
  vicinity: string
  rating?: number
  photos?: Array<{
    photo_reference: string
  }>
}

interface GoogleMapProps {
  places: Place[]
  onPlaceSelect: (place: Place) => void
}

declare global {
  interface Window {
    google: any
  }
}

export default function GoogleMap({ places, onPlaceSelect }: GoogleMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<any>(null)
  const [markers, setMarkers] = useState<any[]>([])

  useEffect(() => {
    if (typeof window !== 'undefined' && !window.google) {
      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places`
      script.async = true
      script.defer = true
      script.onload = initMap
      document.head.appendChild(script)
    } else if (window.google) {
      initMap()
    }
  }, [])

  const initMap = () => {
    if (mapRef.current && window.google) {
      const mapInstance = new window.google.maps.Map(mapRef.current, {
        center: { lat: 35.6762, lng: 139.6503 }, // Tokyo
        zoom: 13,
      })
      setMap(mapInstance)
    }
  }

  useEffect(() => {
    if (map && places.length > 0) {
      // Clear existing markers
      markers.forEach(marker => marker.setMap(null))
      
      const newMarkers: any[] = []
      const bounds = new window.google.maps.LatLngBounds()

      places.forEach((place) => {
        const marker = new window.google.maps.Marker({
          position: {
            lat: place.geometry.location.lat,
            lng: place.geometry.location.lng,
          },
          map: map,
          title: place.name,
        })

        marker.addListener('click', () => {
          onPlaceSelect(place)
        })

        newMarkers.push(marker)
        bounds.extend(marker.getPosition())
      })

      setMarkers(newMarkers)
      map.fitBounds(bounds)
    }
  }, [map, places, onPlaceSelect])

  return (
    <div 
      ref={mapRef} 
      className="w-full h-96 rounded-lg border"
      style={{ minHeight: '400px' }}
    />
  )
}