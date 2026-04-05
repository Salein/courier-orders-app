import { useParams, useNavigate, Link } from 'react-router-dom'
import useOrderStore from '../store/orderStore'
import { useEffect } from 'react'

function OrderDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { orders, closeOrder, fetchOrders } = useOrderStore()

  const order = orders.find(o => o.id === id)

  useEffect(() => {
    if (!order && id) {
      fetchOrders()
    }
  }, [order, id, fetchOrders])

  if (!order) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Загрузка...</p>
      </div>
    )
  }

  const handleClose = async () => {
    await closeOrder(order.id)
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-md mx-auto px-4 py-6">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h1 className="text-xl font-bold text-gray-800 mb-4">Детали заказа</h1>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Адрес доставки</label>
              <p className="text-gray-800 mt-1">{order.address || 'Не определён'}</p>
            </div>

            {order.phone && (
              <div>
                <label className="text-sm font-medium text-gray-500">Телефон</label>
                <p className="text-gray-800 mt-1">{order.phone}</p>
              </div>
            )}

            {order.items.length > 0 && (
              <div>
                <label className="text-sm font-medium text-gray-500">Товары</label>
                <div className="mt-2 space-y-2">
                  {order.items.map((item, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-gray-700">{item.name} × {item.qty}</span>
                      <span className="text-gray-600">{item.price.toFixed(2)} BYN</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {order.total_sum > 0 && (
              <div className="pt-4 border-t border-gray-100">
                <div className="flex justify-between text-lg font-bold">
                  <span>Итого:</span>
                  <span className="text-blue-600">{order.total_sum.toFixed(2)} BYN</span>
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 space-y-3">
            <button
              onClick={handleClose}
              className="block w-full py-3 px-4 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-colors"
            >
              ✅ Закрыть заказ
            </button>
            <Link
              to="/"
              className="block w-full py-3 px-4 text-center bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
            >
              ← Назад к списку
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OrderDetail
