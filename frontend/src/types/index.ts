export interface OrderItem {
  name: string
  qty: number
  price: number
}

export interface Order {
  id: string
  address: string
  phone: string
  items: OrderItem[]
  total_sum: number
  lat: number | null
  lon: number | null
  status: string
  created_at: string
}

export interface UploadResponse {
  id: string
  order: Order
}

export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

export interface Location {
  lat: number
  lon: number
}
