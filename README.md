# Courier Orders App

Мобильное веб-приложение для курьеров в РБ. Снимаешь накладную → распознаёт → лист заказов + карта с точками, отсортированными по близости.

## 🚀 Quick start

### Backend (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\\Scripts\\activate на Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Открой http://localhost:5173 в браузере (на телефоне — через local IP компьютера).

## 🔧 Настройки

- **EasyOCR** автоматически скачивает модели при первом запуске (ru+en). Может занять минуту.
- **Nominatim**: бесплатный геокодер OSM, в бэкенде используется User-Agent. Если будет 429 — добавь `time.sleep(1)` между запросами.
- Данные хранятся в `backend/data/orders.json`. Не удаляй эту папку.

## 📱 Работа на телефоне

1. Убедись, что телефон и компьютер в одной Wi-Fi сети.
2. Запусти фронтенд, на телефоне открой `http://<COMPUTER_IP>:5173`.
3. Разреши камеру и геолокацию.
4. Фотографируй накладные.

## 🐛 Возможные ошибки

- **OCR не распознаёт** — используй чёткие фото, хорошее освещение, без бликов.
- **Геолокация не работает** — разреши доступ в браузере, проверь настройки сайта.
- **Nominatim 429 Too Many Requests** — подожди минуту или добавь задержку в `geocoder.py`.
- **Порт занят** — поменяй порты в `frontend/vite.config.ts` и при запуске uvicorn.

## 📦 Stack

- Backend: FastAPI, EasyOCR, Pydantic, Nominatim
- Frontend: React 18, Vite, Zustand, Leaflet, Tailwind

Happy coding!
