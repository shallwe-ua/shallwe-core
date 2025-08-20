# syntax=docker/dockerfile:1

ARG NODE_VERSION=18.19.1
FROM node:${NODE_VERSION}-alpine

WORKDIR /app

# Copy dependency lists
COPY package.json package-lock.json ./

# Install all dependencies
RUN npm install

# Copy the rest of the application code
COPY . .
