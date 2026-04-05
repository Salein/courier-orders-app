import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import useOrderStore from '../store/orderStore'
import 'leaflet/dist/leaflet.css'

// Fix default icon in webpack
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow
})
L.Marker.prototype.options.icon = DefaultIcon

function haversine(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const toRad = (x: number) => (x * Math.PI) / 180
  const R = 6371 // km
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

// Component that updates map center
function MapController({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])
  return null
}

function MapPage() {
  const { orders, userLocation, setUserLocation, fetchOrders } = useOrderStore()
  const mapRef = useRef<L.Map | null>(null)

  useEffect(() => {
    if (!userLocation && 'geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setUserLocation({
            lat: pos.coords.latitude,
            lon: pos.coords.longitude
          })
          fetchOrders().catch(console.error)
        },
        (err) => {
          alert('Нужно разрешить доступ к геолокации, чтобы показать карту.')
        },
        { enableHighAccuracy: true }
      )
    } else if (userLocation) {
      fetchOrders().catch(console.error)
    }
  }, [userLocation, setUserLocation, fetchOrders])

  if (!userLocation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center p-6 bg-white rounded-xl shadow">
          <h1 className="text-xl font-bold mb-4">🗺 Карта заказов</h1>
          <p className="text-gray-600 mb-4">
            Для отображения карты нужен доступ к геолокации. Включите её в настройках браузера и обновите страницу.
          </p>
          <Link to="/" className="text-blue-600 hover:underline">← Назад</Link>
        </div>
      </div>
    )
  }

  // Active orders with coordinates
  const activeOrders = orders.filter(o => o.status === 'active' && o.lat && o.lon)

  // Sort by distance
  const sorted = activeOrders
    .map((order) => ({
      ...order,
      distance: haversine(userLocation.lat, userLocation.lon, order.lat!, order.lon!)
    }))
    .sort((a, b) => a.distance - b.distance)

  const mapCenter: [number, number] = [userLocation.lat, userLocation.lon]

  return (
    <div className="h-screen w-full">
      <div className="absolute top-4 left-4 z-[1000] bg-white px-4 py-2 rounded-lg shadow-md">
        <p className="font-medium text-gray-800">Курьер: {userLocation.lat.toFixed(4)}, {userLocation.lon.toFixed(4)}</p>
      </div>
      <div className="absolute bottom-4 left-0 w-full z-[1000] px-4">
        <Link
          to="/"
          className="px-4 py-3 bg-gray-800 text-white font-medium rounded-lg w-full text-center block"
        >
          ← Назад к списку
        </Link>
      </div>

      <MapContainer center={mapCenter} zoom={13} style={{ height: '100%', width: '100%' }} ref={mapRef}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <MapController center={mapCenter} />

        {/* User marker */}
        <Marker position={[userLocation.lat, userLocation.lon]} icon={L.divIcon({
          html: '<div style="background:#4F46E5;width:24px;height:24px;border-radius:50%;border:3px solid white;box-shadow:0 0 8px rgba(0,0,0,0.3);"></div>',
          className: '',
          iconSize: [24, 24]
        })} />

        {/* Order markers */}
        {sorted.map((order, index) => (
          <Marker
            key={order.id}
            position={[order.lat!, order.lon!]}
            icon={L.divIcon({
              html: `<div style="background:#DC2626;width:28px;height:28px;border-radius:50%;color:white;font-weight:bold;display:flex;align-items:center;justify-content:center;border:2px solid white;box-shadow:0 0 8px rgba(0,0,0,0.3);">${index + 1}</div>`,
              className: '',
              iconSize: [28, 28]
            })}
          >
            <Popup>
              <div className="text-gray-800">
                <p className="font-semibold">{order.address}</p>
                {order.total_sum > 0 && <p className="text-sm">Сумма: {order.total_sum.toFixed(2)} BYN</p>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}

export default MapPage
