# Executive Marketing Summary GenAI Project

This project generates executive-ready marketing performance summaries using Generative AI. It supports ingesting raw marketing data objects (campaigns, attendees, responses, activities, contacts/leads, accounts, opportunities) from CSV, JSON, or API sources.

## Features
- Modular data models for all key marketing objects
- Utilities for generating and loading dummy data
- Flexible data ingestion (CSV, JSON, API)
- Placeholder for GenAI integration

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Run the main script: `python main.py`

## Project Structure
- data_models/: Data classes for each marketing object
- data_ingestion/: Utilities for loading/generating data
- genai/: GenAI integration logic
- main.py: Entry point

## Next Steps
- Implement data models and dummy data
- Add GenAI summary generation
- Output summaries for analyst review
