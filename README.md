# Courier Orders App

Мобильное веб-приложение для курьеров в РБ. Снимаешь накладную → распознаёт → лист заказов + карта с точками, отсортированными по близости.

## 🚀 Quick start (локально)

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

Открой **http://localhost:5173** в браузере.

Чтобы открыть с телефона (в той же WiFi):
- Узнай IP компьютера (например `192.168.1.100`)
- На телефоне открой `http://192.168.1.100:5173`

---

## 🌍 Доступ из любой точки (не только в локальной сети)

### Вариант A: Tailscale (рекомендуется)

Tailscale создаёт VPN-сеть между устройствами без сложной настройки.

На **компьютере с бэкендом**:

```bash
# Установи Tailscale (из официального сайта или через пакетный менеджер)
# Для Ubuntu/Debian:
sudo apt update && sudo apt install tailscale

# Войди в свой аккаунт
sudo tailscale up

# После подключения посмотри IP:
tailscale ip
# Пример: 100.101.102.103
```

Теперь запусти бэкенд, слушая на `0.0.0.0` (по умолчанию):

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

На **телефоне**:
- Установи Tailscale из App Store/Google Play
- Войди в тот же аккаунт
- Телефон получит IP типа `100.101.102.104`
- Открой `http://<компьютерный_IP_в_tailscale>:8000/api/health` чтобы проверить доступность бэкенда
- Открой `http://<компьютерный_IP_в_tailscale>:5173` для фронтенда (если фронтенд тоже запущен на компе, прокси «/api» сольётся с бэкендом через порт 8000)

Всегда используй IP из Tailscale, а не локальный.

---

### Вариант B: ngrok (быстрый туннель)

На компьютере:

```bash
# Скачай ngrok с https://ngrok.com
./ngrok http 8000 &
```

ngrok выдаст публичный URL вида `https://abc123.ngrok.io`.

В `frontend/src/api/client.ts` измени:

```ts
baseURL: 'https://abc123.ngrok.io/api'
```

Теперь фронтенд можно хоть на Vercel/Netlify, а бэкенд остаётся локально через туннель.

---

### Вариант C: VPS (постоянный домен)

1. Задеплой backend на сервер (Docker или systemd).
2. Задеплой frontend на Vercel/Netlify/Render.
3. Настрой Nginx/Caddy для проксирования `/api` → бэкенд.
4. Добавь Let's Encrypt HTTPS.

---

## 📱 Работа на телефоне (проверка)

1. Разреши камеру и геолокацию в браузере.
2. Фотографируй накладную.
3. Смотри список заказов.
4. Открывай карту — метки будут пронумерованы по удалённости от тебя.

---

## 🐛 Возможные ошибки

- **OCR не распознаёт** → чёткие фото, хорошее освещение, без бликов.
- **Геолокация не работает** → разреши доступ в браузере.
- **Nominatim 429 Too Many Requests** → используй задержку между запросами (в `geocoder.py` можно добавить `await asyncio.sleep(1)`).
- **Порт занят** → поменяй порты в `frontend/vite.config.ts` и при запуске `uvicorn`.
- **Tailscale не подключается** → проверь, что антивирус/брандмауэр не блокируют.

---

## 📦 Stack

- **Backend**: FastAPI, EasyOCR, Pydantic, Nominatim, JSON storage
- **Frontend**: React 18, Vite, Zustand, Leaflet, Tailwind

---

## 🗂 Структура проекта

```
courier-app/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── ocr_service.py
│   ├── parser.py
│   ├── geocoder.py
│   ├── storage.py
│   ├── requirements.txt
│   └── data/
│       └── orders.json
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── Home.tsx
│       │   ├── OrderDetail.tsx
│       │   └── Map.tsx
│       ├── store/
│       ├── api/
│       └── types/
└── README.md
```

---

## 📄 Лицензия

MIT — можете использовать и менять как угодно.
