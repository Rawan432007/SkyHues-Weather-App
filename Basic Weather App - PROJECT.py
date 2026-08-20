import csv
import json
import tkinter as tk
from tkinter import messagebox, ttk
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION & CONSTANTS ---
HISTORY_FILE = Path("weather_history.csv") # File where we store search history in the variable

# Open-Meteo API endpoints (free weather and geocoding services)
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search" 
WEATHER_URL = "https://api.open-meteo.com/v1/forecast" 

# Headers so the API knows what app is making the request
# NAME OF THE APP: SkyHuesWeatherApp
HEADERS = {
    "User-Agent": "SkyHuesWeatherApp/1.0"
    }

# --- FUNCTIONS ---
def get_coordinates(city: str): 
    """Converts a city name (ex. 'London') into geographic coordinates (latitude & longitude)."""
    # Package parameters in the 'params' dictionary into URL format: ?name=Dubai&count=1&language=en&format=json
    params = urllib.parse.urlencode(
        {"name": city, "count": 1, "language": "en", "format": "json"}
    )
    req = urllib.request.Request(f"{GEO_URL}?{params}", headers=HEADERS)    

    # Network request with a 5 second timeout limit 
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())

    results = data.get("results")
    if not results:
        return None, None, None, None # If no results are found, return None for all values
    
    # If results are found, extract the first match and return its latitude, longitude, name, and country
    match = results[0]
    return (
        match.get("latitude"),
        match.get("longitude"),
        match.get("name"),
        match.get("country", "Unknown"),
    )

def get_weather(latitude: float, longitude: float) -> dict:
    """Gets real-time weather using latitude and longitude."""
    params = urllib.parse.urlencode(
        {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
    )
    
    req = urllib.request.Request(f"{WEATHER_URL}?{params}", headers=HEADERS)

    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())

    # Return only the current weather dictionary block
    return data.get("current_weather", {})


def log_search(
    city: str, country: str, temp: float, wind: float
):
    """Appends successful searches into a CSV text file."""
    file_exists = HISTORY_FILE.exists() # Check if the history file already exists
    
    # Open the history file in append mode, and write the search data
    with open(HISTORY_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f) # Create a CSV writer object to write rows into the file
        
        # If the file doesn't exist, write the header row first
        if not file_exists:
            writer.writerow(["Logged_At", "City", "Country", "Temp_C", "Wind_KMH"])

        # Write the actual search data row
        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Timestamp of the search
                city,
                country,
                temp,
                wind,
            ]
        )

# --- GUI, GRAPHICAL USER INTERFACE (TKINTER) ---   

# Main Application Class
class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__() # Initialize the Tkinter root window

        # Window Configuration
        self.title("SkyHues - Weather")  # Text shown in window title
        self.geometry("380x460")          # Window size (width x height) in pixels
        self.configure(bg="#181825")  # Window background color (dark theme) in hex code
        self.resizable(False, False)    # Lock window size to prevent resizing (Width, Height)
        
        # Built-in ttk styling for widgets (buttons, labels, etc.)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Build all visible components of the GUI and set default weather view
        self.setup_ui()
        
        # Default city weather when the app launches
        self.search_weather("Dubai")  # Default view

    def setup_ui(self):
        """ For Buttons, Text Entries, and Labels on the screen. """
    
        # 1. App Header
        header_lbl = tk.Label( # Label is the text shown on the screen, in this case the app name
            self,                           # Main window is the parent of this label
            text=" SkyHues Weather",        # Displayed text
            font=("Segoe UI", 16, "bold"),  
            fg="#cdd6f4",                 # Text color (foreground) in hex code
            bg="#181825",                 # Background color in hex code
        )
        # pack() places element on screen. pady adds vertical space (top, bottom) around element
        header_lbl.pack(pady=(22, 12))
                      
        # 2. Search Controls
        # Frame groups Entry box and Search button
        search_frame = tk.Frame(self, bg="#181825")
        search_frame.pack(pady=8)
        
        self.city_entry = tk.Entry( # Text input field for user to type city name
            search_frame,           # Inside search_frame container
            font=("Segoe UI", 11),  
            width=20,               # Text field width in characters
            justify="center",       # Center-align the text in the field 
            bg="#313244",         # Background color of the text field in hex code
            fg="#cdd6f4",         # Text color (foreground) in hex code
            insertbackground="#cdd6f4", # Cursor color in hex code
            relief="flat",                # Flat border style (no 3D effect)
        )
        # grid() places element in a grid layout. ipady adds internal vertical padding (inside the element). padx adds horizontal space (left, right) around element
        self.city_entry.grid(row=0, column=0, ipady=6, padx=(0, 8))
        
        # bind triggers search when user hits "Enter" key on keyboard
        self.city_entry.bind("<Return>", lambda e: self.search_weather())
        
    
        search_btn = tk.Button( # Button triggers search when clicked
            search_frame,                  # Inside search_frame container
            text="Search",                 
            font=("Segoe UI", 9, "bold"),
            bg="#89b4fa",                # Background color of the button in hex code
            fg="#11111b",                # Text color (foreground) in hex code
            activebackground="#b4befe",  # Background color when button is clicked in hex code
            relief="flat",
            padx=12,                       # Horizontal padding inside the button
            command=self.search_weather,   # Function to call when button is clicked
        )
        search_btn.grid(row=0, column=1, ipady=4)

        # 3. Weather Card
        # Dark frame box to highlight temperature & wind readings
        card = tk.Frame(
            self, 
            bg="#1e1e2e", 
            bd=1,                           # Border width in pixels
            relief="solid", 
            highlightbackground="#45475a" # Border color in hex code
        )
        # expand=True allows card to take up available vertical space
        card.pack(pady=20, padx=25, fill="both", expand=True)

        # Label for City, Country output
        self.location_lbl = tk.Label(
            card,                  # Placed inside card container
            text="Searching...",
            font=("Segoe UI", 13, "bold"),
            fg="#f5e0dc",
            bg="#1e1e2e",
            wraplength=300,        # Wrap text to fit within 300 pixels width
        )
        self.location_lbl.pack(pady=(24, 4))
        
        # Dynamic label for Temperature output
        self.temp_lbl = tk.Label(
            card,
            text="-- °C",
            font=("Segoe UI", 32, "bold"),
            fg="#a6e3a1",
            bg="#1e1e2e",
        )
        self.temp_lbl.pack(pady=8)
        
        # Dynamic label for Wind Speed output
        self.wind_lbl = tk.Label(
            card,
            text="Wind: -- km/h",
            font=("Segoe UI", 10),
            fg="#bac2de",
            bg="#1e1e2e",
        )
        self.wind_lbl.pack(pady=(0, 20))

    def search_weather(self, target_city: str = None):
        """Action handler that runs network requests and updates text labels on screen."""
        # Use target_city if provided (startup), otherwise read input field text
        city = target_city or self.city_entry.get().strip()
        
        # Input check: if the user didn't type anything, show a warning message and exit the function early
        if not city:
            messagebox.showwarning("Warning", "Please enter a city name.")
            return

        try:
            # Step 1: Query location coordinates (latitude, longitude)
            lat, lon, name, country = get_coordinates(city)
            
            # If location query returns empty results
            if lat is None:
                messagebox.showerror(
                    "Error", f"Could not find coordinates for '{city}'."
                )
                return
            # Step 2: Query current weather metrics 
            weather = get_weather(lat, lon)
            temp = weather.get("temperature", "N/A")
            wind = weather.get("windspeed", "N/A")

            # Step 3: Update GUI labels with the fetched data
            # .config() updates the text of the label widgets with the new weather information
            self.location_lbl.config(text=f"{name}, {country}")
            self.temp_lbl.config(text=f"{temp} °C")
            self.wind_lbl.config(text=f"Wind: {wind} km/h")

            # Step 4: Log the search to the CSV history file
            log_search(name, country, temp, wind)

        except Exception as err:
            # Catch network timeouts or missing parameters and alert user via popup box
            messagebox.showerror("Error", f"Failed to fetch weather data:\n{err}")

# --- APPLICATION ENTRY POINT ---
if __name__ == "__main__":
    app = WeatherApp()      # Instantiate the WeatherApp class, which initializes the GUI and sets up the application
    app.mainloop()          # Keep application running and responsive to user interactions until the user closes the window