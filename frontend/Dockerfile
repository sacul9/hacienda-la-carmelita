FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
