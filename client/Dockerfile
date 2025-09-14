FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:18-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# NEXT_PUBLIC_API_BASE_URL прокинем при деплое Cloud Run
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080
COPY --from=build /app ./
EXPOSE 8080
CMD ["npm", "run", "start", "--", "-p", "8080"]


