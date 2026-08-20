# SkyHues-Weather-App
A Python desktop weather app with a Tkinter GUI, Open-Meteo API integration, and CSV search history.

SkyHues Weather is a desktop weather application built with Python and Tkinter. Users can search for a city and view its current temperature and wind speed through a simple graphical interface. The application uses Open-Meteo's geocoding and weather APIs to retrieve location and weather data, and stores successful searches in a CSV history file with timestamps.

== Technologies == 
.Python
.Tkinter / ttk — graphical user interface
.Open-Meteo API — geocoding and weather data
.CSV — search-history storage
.JSON — API response handling
.urllib — HTTP/API requests
.Pathlib — file management

==  Main features == 
🌍 Search weather by city
📍 Automatic conversion of city names to latitude/longitude
🌡️ Current temperature display
💨 Current wind-speed display
🖥️ Desktop GUI with a custom dark theme
⌨️ Press Enter to search
📋 CSV search history with timestamps
⚠️ Error handling for invalid cities and failed requests
⏱️ 5-second network timeout for API requests
