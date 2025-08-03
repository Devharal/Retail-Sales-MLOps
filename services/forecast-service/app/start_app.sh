#!/bin/bash


uvicorn app.main:app --host 0.0.0.0 --port $FORECAST_SERVICE_PORT --reload
