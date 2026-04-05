import { create } from 'zustand'
import type { UploadStatus } from '../types'
import type { Order as ApiOrder } from '../api/client'
import * as api from '../api/client'

// Normalized order for UI
interface Order {
  id: string
  address: string
  phone: string
  items: { name: string; qty: number; price: number }[]
  total_sum: number
  lat: number | null
  lon: number | null
  status: string
  created_at: string
}

function normalizeApiOrder(o: ApiOrder): Order {
  const addr = typeof o.address === 'string'
    ? o.address
    : o.address?.display_name || o.address?.raw || ''
  return {
    id: o.id,
    address: addr,
    phone: o.phone || '',
    items: (o.items || []).map(i => ({ name: i.name, qty: i.quantity, price: i.price ?? 0 })),
    total_sum: o.total_sum ?? 0,
    lat: o.address && typeof o.address !== 'string' ? (o.address.latitude ?? null) : null,
    lon: o.address && typeof o.address !== 'string' ? (o.address.longitude ?? null) : null,
    status: o.status,
    created_at: o.created_at,
  }
}

interface OrderStore {
  orders: Order[]
  userLocation: { lat: number; lon: number } | null
  uploadStatus: UploadStatus
  fetchOrders: () => Promise<void>
  addOrder: (order: Order) => void
  closeOrder: (id: string) => Promise<void>
  setUserLocation: (loc: { lat: number; lon: number } | null) => void
  setUploadStatus: (status: UploadStatus) => void
}

const useOrderStore = create<OrderStore>((set) => ({
  orders: [],
  userLocation: null,
  uploadStatus: 'idle',
  fetchOrders: async () => {
    const apiOrders = await api.getOrders()
    const orders = apiOrders.map(normalizeApiOrder)
    set({ orders })
  },
  addOrder: (order) => set((state) => ({ orders: [order, ...state.orders] })),
  closeOrder: async (id) => {
    await api.closeOrder(id)
    set((state) => ({ orders: state.orders.filter((o) => o.id !== id) }))
  },
  setUserLocation: (loc) => set({ userLocation: loc }),
  setUploadStatus: (status) => set({ uploadStatus: status })
}))

export default useOrderStore
