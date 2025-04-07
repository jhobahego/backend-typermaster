# TyperMaster API

Backend API para la aplicación TyperMaster, un juego de mecanografía que ayuda a los usuarios a mejorar su velocidad de escritura.

## 🔗 Enlaces Relacionados

- [Frontend TyperMaster](https://github.com/jhobahego/frontend-typermaster)

## 🚀 Características

- Endpoints para obtener textos aleatorios para practicar
- Almacenamiento de resultados de las prácticas
- Historial de puntuaciones con paginación
- Integración con PostgreSQL
- Soporte para CORS
- Configuración para entornos de desarrollo y producción

## 🛠️ Requisitos Previos

- Python 3.8 o superior
- PostgreSQL
- pip (gestor de paquetes de Python)
- Google Gemini API Key (for text generation)

## ⚙️ Configuración

1. Clona el repositorio
```bash
git clone https://github.com/tu-usuario/backend-typermaster.git
cd backend-typermaster
```
2. Crea y activa un entorno virtual
```bash
python -m venv venv
source venv/bin/activate # Linux/MacOS
venv\Scripts\activate # Windows
```

3. Instala las dependencias
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno. Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
```dotenv
# Database
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/typermaster

# Gemini API Key (Required for text generation)
GEMINI_API_KEY=TU_CLAVE_API_DE_GEMINI

# CORS Origins
DEV_ORIGINS=http://localhost:5173,http://localhost:3000
PROD_ORIGINS=https://tudominio.com

# Environment
ENVIRONMENT=development
```
Asegúrate de reemplazar `TU_CLAVE_API_DE_GEMINI` con tu clave real.

5. Crea la base de datos en PostgreSQL
```sql
CREATE DATABASE typermaster;
```

6. Crea los archivos `.env.development` y `.env.production` basándote en los ejemplos:

.env.development:

```env
# Database
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/typermaster

# CORS Origins
DEV_ORIGINS=http://localhost:5173,http://localhost:3000
PROD_ORIGINS=https://tudominio.com

# Environment
ENVIRONMENT=development
```

## 🚀 Ejecución

Para desarrollo:
```bash
ENV=development uvicorn main:app --reload
```

Para producción:
```bash
ENV=production uvicorn main:app
```

La API estará disponible en `http://localhost:8000`

## 📚 Documentación API

Una vez que el servidor esté corriendo, puedes acceder a:

- Documentación Swagger UI: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`

## 🔄 Endpoints Principales

- `GET /texts` - Obtiene un texto aleatorio para practicar
- `POST /results` - Guarda el resultado de una práctica
- `GET /results` - Obtiene el historial de resultados (paginado)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

## 📝 Licencia

[MIT](https://choosealicense.com/licenses/mit/)

