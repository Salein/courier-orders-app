# Courier Orders API (FastAPI)

Бэкенд для приложения курьерских заказов.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn main:app --reload --port 8000
```

## Эндпоинты

| Метод | Путь                              | Описание                         |
|-------|-----------------------------------|---------------------------------|
| POST  | `/api/upload`                     | Загрузка фото + распознавание   |
| GET   | `/api/orders`                     | Список активных заказов         |
| GET   | `/api/orders/{id}`                | Детали заказа                   |
| PATCH | `/api/orders/{id}/close`          | Закрыть заказ                   |

CORS разрешён для `http://localhost:5173`.

Заказы хранятся в `data/orders.json`.
