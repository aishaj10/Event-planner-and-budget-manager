# Event-planner-and-budget-manager
AI-based Event Planner and Budget Manager web application that helps users manage expenses, analyze budgets, discover nearby venues, and get planning assistance using an AI chatbot. The system uses Flask, SQLite, OpenStreetMap, and APIs for smart recommendations, maps, analytics, and reviews.
# EVENT PLANNER AND BUDGET MANAGER

## Overview
Event Planner and Budget Manager is an AI-based web application developed to simplify event planning and budget management. The system helps users manage expenses, analyze budgets, discover nearby venues, and interact with an AI chatbot for planning assistance.

The project integrates venue recommendation, interactive maps, analytics, reviews, and chatbot support into a single platform.

---

# Features

- User Registration and Login
- Expense Tracking and Budget Analysis
- Nearby Venue Recommendation
- Interactive Maps using OpenStreetMap
- AI Chatbot Assistance
- Owner Dashboard for Venue Management
- Review and Rating System
- Budget Analytics and Charts
- Responsive Dashboard UI

---

# Technologies Used

## Frontend
- HTML
- CSS
- Bootstrap
- JavaScript

## Backend
- Python Flask

## Database
- SQLite

## APIs and Libraries
- OpenStreetMap API
- Nominatim API
- Groq API
- Leaflet.js
- Chart.js

---

# Main Modules

## User Authentication
Handles user registration, login, and session management.

## Expense Management
Tracks planned and actual expenses with graphical analytics.

## Venue Recommendation
Recommends nearby venues based on:
- location
- budget
- venue type
- distance calculation

## AI Chatbot
Provides event planning assistance using AI-generated responses.

## Owner Dashboard
Allows venue owners to:
- add venues
- upload images
- manage venue listings

## Review and Rating System
Users can submit ratings and reviews for venues.

---

# Project Workflow

1. User enters location, budget, and venue type.
2. Backend processes requests using Flask.
3. Nominatim API converts location into coordinates.
4. Venue recommendation logic filters nearby venues.
5. OpenStreetMap and Leaflet.js display venue locations.
6. AI chatbot provides planning assistance.
7. Results are displayed on the dashboard.

