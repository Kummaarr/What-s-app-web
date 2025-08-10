FROM node:18 AS build-frontend
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY --from=build-frontend /frontend/dist ./backend/static
ENV PORT=8000
CMD ["uvicorn", "backend.main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
