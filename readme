# 🛍️ AI-Powered E-Commerce REST API

¡Bienvenido al backend core de una plataforma de comercio electrónico moderna, segura y potenciada por Inteligencia Artificial! Esta API fue construida desde cero utilizando **FastAPI** y sigue una arquitectura limpia, modular y escalable para el manejo de usuarios, catálogos, finanzas internacionales y lógica predictiva.

---

## 🚀 Características Principales (Features)

* **🔐 Autenticación Robusta:** Registro e inicio de sesión utilizando hashing de contraseñas con `bcrypt` y protección de rutas mediante tokens **JWT (JSON Web Tokens)**.
* **🛡️ Control de Accesos por Roles:** Sistema de seguridad basado en dependencias inyectadas para restringir módulos críticos (como la creación de productos) únicamente a usuarios con rol `admin`.
* **📦 Gestión de Catálogo e Inventario:** Base de datos relacional (**SQLite** con **SQLAlchemy**) para controlar stock, precios y descripciones de mercancía en tiempo real.
* **🛒 Carrito de Compras Inteligente:** Lógica acumulativa que incrementa las cantidades en lugar de duplicar registros, validando la disponibilidad de inventario antes de añadir artículos.
* **💳 Procesamiento de Pagos Globales:** Integración nativa con la pasarela financiera de **Stripe** mediante la generación segura de *PaymentIntents*.
* **🤖 Recomendaciones con IA:** Motor predictivo conectado con la API de **Google Gemini** (`gemini-2.5-flash`) que analiza las preferencias del carrito del usuario y el catálogo completo para sugerir productos de forma personalizada.

---

##  Stack Tecnológico

* **Framework Principal:** FastAPI (Python 3.14+)
* **ORMs & Base de Datos:** SQLAlchemy, SQLite
* **Seguridad:** PyJWT, Bcrypt, Python-Dotenv
* **Pasarela de Pagos:** Stripe SDK
* **Inteligencia Artificial:** Google GenAI Core Engine
* **Servidor ASGI:** Uvicorn

---

##  Instalación y Configuración Local

Sigue estos pasos para levantar el entorno de desarrollo en tu computadora local:

### 1. Clonar el repositorio e ingresar al directorio
```bash
git clone [https://github.com/AriCO-PE/E-Commerce-API-fastAPI.git](https://github.com/AriCO-PE/E-Commerce-API-fastAPI.git)
cd E-Commerce-API-fastAPI