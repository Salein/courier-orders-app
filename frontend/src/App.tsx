import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import OrderDetail from './pages/OrderDetail'
import Map from './pages/Map'
import { useOrderStore } from './store/orderStore'
import './index.css'

function App() {
  const fetchOrders = useOrderStore((s) => s.fetchOrders)

  // Preload orders on app start
  fetchOrders().catch(console.error)

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/order/:id" element={<OrderDetail />} />
        <Route path="/map" element={<Map />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
