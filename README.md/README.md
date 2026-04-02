# Build 1.2 — Multi-Source Daily Aggregator

## What it does
Calls two live APIs and prints a combined daily briefing to the console.
Weather via OpenWeatherMap. Exchange rate via ExchangeRate API.

## What this demonstrates
Multiple API calls in one script, reusable functions, independent error
handling per API, environment variable management via dotenv.

## How to run
1. Create a .env file with: WEATHER_API_KEY=your_key_here
2. pip install requests python-dotenv
3. python aggregator.py

## Stack
Python 3, requests, python-dotenv