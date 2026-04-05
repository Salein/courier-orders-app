import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface OrderItemRaw {
  name: string
  quantity: number
  price: number | null
}

export interface OrderAddressRaw {
  raw: string | null
  latitude: number | null
  longitude: number | null
  display_name: string | null
}

export interface Order {
  id: string
  address: OrderAddressRaw | string | null
  phone: string | null
  items: OrderItemRaw[]
  total_sum: number | null
  lat: number | null
  lon: number | null
  status: string
  created_at: string
  ocr_text?: string
  ocr_confidence?: number
  ocr_raw_image_name?: string
  comment?: string | null
}

export interface UploadResponse {
  id: string
  order: Order
}

export async function uploadPhoto(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return res.data
}

export async function getOrders(): Promise<Order[]> {
  const res = await api.get<Order[]>('/orders')
  return res.data
}

export async function getOrder(id: string): Promise<Order> {
  const res = await api.get<Order>(`/orders/${id}`)
  return res.data
}

export async function closeOrder(id: string): Promise<void> {
  await api.patch(`/orders/${id}/close`)
}

export default {
  uploadPhoto,
  getOrders,
  getOrder,
  closeOrder
}
