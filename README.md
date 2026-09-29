# Django E-commerce

A Django REST API (`/api/`) with a React single-page frontend in `frontend/`.

## Setup

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py populate_products   # demo catalog
.venv/bin/python manage.py createsuperuser     # optional, for /admin

cd frontend && npm install
```

## Development

Run both servers, then open http://localhost:5173:

```sh
.venv/bin/python manage.py runserver     # API on :8000
cd frontend && npm run dev               # React on :5173, proxies /api, /media and /admin to :8000
```

The SPA and API share an origin through the Vite proxy, so Django's session and CSRF cookies are used for
auth and for anonymous carts; the frontend calls `/api/auth/me/` on load to receive the CSRF cookie.

## Tests

```sh
.venv/bin/python manage.py test   # API
cd frontend && npm test           # React (Vitest)
```

## API overview

| Endpoint | Methods | Notes |
| --- | --- | --- |
| `auth/me/`, `auth/login/`, `auth/register/`, `auth/logout/` | GET / POST | Session auth; login/register merge the anonymous cart |
| `categories/` | GET | With active product counts |
| `products/` | GET | `q`, `category`, `min_price`, `max_price`, `in_stock`, `sort`, `page`, `page_size` |
| `products/<slug>/` | GET | Includes variation groups and related products |
| `cart/` | GET | `?province=XX` adds tax and shipping |
| `cart/items/`, `cart/items/<id>/` | POST / PATCH, DELETE | Each returns the updated cart |
| `provinces/` | GET | Tax rates and shipping costs |
| `checkout/validate/` | POST | Validate the `sections` of one checkout step |
| `checkout/` | POST | Place the order (login required) |
| `orders/`, `orders/<id>/` | GET | The current user's orders |

