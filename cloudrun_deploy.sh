#!/bin/bash
# Script para build e deploy no Google Cloud Run

PROJECT_ID="SEU_PROJECT_ID"
REGION="us-central1"
SERVICE_NAME="jarviss-backend"

# Build da imagem

gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy no Cloud Run

gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=...,SECRET_KEY=...,JWT_SECRET_KEY=...,WHATSAPP_TOKEN=...,WHATSAPP_PHONE_ID=..." 