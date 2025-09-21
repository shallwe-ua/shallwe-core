# syntax=docker/dockerfile:1

# =========================
# Stage 1: Base with dependencies
ARG NODE_VERSION=18.19.1
FROM node:${NODE_VERSION}-alpine AS base

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci


# =========================
# Stage 2: Development with hot reload
FROM base AS dev
COPY . .


# =========================
# Stage 3: Optimized production builder
FROM dev AS builder

# Declare build arguments (pull envs from build shell) to evaluate for compilation
ARG NEXT_PUBLIC_SHALLWE_ENV_MODE
ARG NEXT_PUBLIC_SHALLWE_OAUTH_CLIENT_ID
ARG NEXT_PUBLIC_SHALLWE_OAUTH_REDIRECT_URI
ARG NEXT_PUBLIC_SHALLWE_API_BASE_URL_EXTERNAL
ARG NEXT_PUBLIC_SHALLWE_API_BASE_URL_INTERNAL
ARG NEXT_PUBLIC_SHALLWE_SKIP_MIDDLEWARE

RUN npm run build


# =========================
# Stage 4: Production image
FROM node:${NODE_VERSION}-alpine AS prod

WORKDIR /app

# Copy optimized prod build
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/public ./public
