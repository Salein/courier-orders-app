import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import useOrderStore from '../store/orderStore'
import { uploadPhoto } from '../api/client'
import type { UploadStatus } from '../types'

function Home() {
  const { orders, uploadStatus, fetchOrders, setUploadStatus } = useOrderStore()
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchOrders().catch(console.error)
  }, [])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploadStatus('uploading')
    setUploadError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const data = await uploadPhoto(file)
      setUploadStatus('success')
      // The store's fetchOrders will also refresh, but we can also add immediately
      // addOrder from store if we want optimistic update; here we just refetch
      await fetchOrders()
    } catch (err: any) {
      setUploadStatus('error')
      setUploadError(err.message || 'Неизвестная ошибка')
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-md mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          📦 Курьерские заказы
        </h1>

        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <label
            htmlFor="photo-upload"
            className="block w-full text-center py-3 px-4 bg-blue-600 text-white font-medium rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
          >
            {uploadStatus === 'uploading' ? '⏳ Обработка...' : '📷 Сфотографировать накладную'}
          </label>
          <input
            ref={fileInputRef}
            id="photo-upload"
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={handleFileChange}
            disabled={uploadStatus === 'uploading'}
          />

          {uploadStatus === 'success' && (
            <p className="mt-3 text-green-600 text-center text-sm">✅ Заказ добавлен!</p>
          )}
          {uploadStatus === 'error' && uploadError && (
            <p className="mt-3 text-red-600 text-center text-sm">❌ {uploadError}</p>
          )}
        </div>

        {/* Map Button */}
        <div className="mb-6">
          <Link
            to="/map"
            className="block w-full text-center py-3 px-4 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
          >
            🗺 Открыть карту
          </Link>
        </div>

        {/* Orders List */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-3">Активные заказы</h2>
          {orders.length === 0 && (
            <p className="text-gray-400 text-center py-8">Нет активных заказов</p>
          )}
          {orders.map((order) => (
            <Link
              key={order.id}
              to={`/order/${order.id}`}
              className="block bg-white rounded-xl shadow-md p-4 mb-3 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium text-gray-800">{order.address || 'Адрес не определён'}</p>
                  {order.phone && (
                    <p className="text-sm text-gray-500 mt-1">📞 {order.phone}</p>
                  )}
                </div>
                <span className="text-blue-600 font-semibold">
                  {order.total_sum ? `${order.total_sum.toFixed(2)} BYN` : ''}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {new Date(order.created_at).toLocaleString('ru-RU')}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Home
