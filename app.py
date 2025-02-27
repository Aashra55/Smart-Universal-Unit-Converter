import os
import streamlit as st
import requests
from dotenv import load_dotenv
import spacy
from word2number import w2n
import re

# Load environment variables from .env file
load_dotenv()

# Load NLP model
nlp = spacy.blank("en")

# Conversion factors for different units
conversion_factors = {
    "Length": {
        "Meters": 1,
        "Kilometers": 0.001,
        "Centimeters": 100,
        "Millimeters": 1000,
        "Miles": 0.000621371,
        "Yards": 1.09361,
        "Feet": 3.28084,
        "Inches": 39.3701
    },
    "Weight": {
        "Kilograms": 1,
        "Grams": 1000,
        "Milligrams": 1e6,
        "Pounds": 2.20462,
        "Ounces": 35.274
    },
    "Temperature" : ["Celsius", "Fahrenheit", "Kelvin"],  
    "Currency" : "Dynamic"  # Handled via API
}

# Dictionary for unit mappings
unit_mappings = {
    "meter": "Meters", "meters": "Meters", "metre": "Meters", "metres": "Meters", "m":"Meters",
    "kilometer": "Kilometers", "kilometers": "Kilometers", "kilometre": "Kilometers", "kilometres": "Kilometers", "km":"Kilometers",
    "cm": "Centimeters", "centimeter": "Centimeters", "centimeters": "Centimeters",
    "mm": "Millimeters", "millimeter": "Millimeters", "millimeters": "Millimeters",
    "mile": "Miles", "miles": "Miles",
    "yard": "Yards", "yards": "Yards", "feet": "Feet", "foot": "Feet",
    "inch": "Inches", "inches": "Inches", "kg": "Kilograms", "kilogram": "Kilograms",
    "kilograms": "Kilograms", "gram": "Grams", "grams": "Grams", "mg": "Milligrams",
    "milligram": "Milligrams", "milligrams": "Milligrams", "pound": "Pounds",
    "pounds": "Pounds", "ounce": "Ounces", "ounces": "Ounces", "celsius": "Celsius",
    "fahrenheit": "Fahrenheit", "kelvin": "Kelvin"
}
    
def extract_units_from_text(text):
    """Extracts value, from_unit, and to_unit from user input."""
    doc = nlp(text)

    value = None
    detected_units = []  # Store detected units

    print(f"\n🔍 Debugging NLP Extraction: {text}")
    print(f"Tokens Detected: {[token.text for token in doc]}")

    for token in doc:
        token_text = token.text.lower().strip()
        is_number = False  # Flag to mark if this token is a number

        # First, check if token is a numeric string using regex (e.g., "5" or "5.0")
        if re.match(r'^\d+(\.\d+)?$', token_text):
            try:
                value = float(token_text)
                is_number = True
            except ValueError:
                pass  # Should rarely happen
        else:
            # If not a plain number, try converting word-based numbers (e.g., "five")
            try:
                converted_value = w2n.word_to_num(token_text)
                value = float(converted_value)
                is_number = True
            except ValueError:
                pass  # Not a number word, ignore

        # Only check for unit if the token wasn't identified as a number
        if not is_number:
            # Check if token is a valid unit from unit_mappings
            if token_text in unit_mappings:
                detected_units.append(unit_mappings[token_text])
            # Detect currency codes (e.g., USD, EUR)
            elif len(token_text) == 3 and token_text.isalpha() and token_text.upper() not in unit_mappings:
                detected_units.append(token_text.upper())

    print(f"🔎 Extracted Value: {value}, Units: {detected_units}")

    # Assign detected units properly
    from_unit = detected_units[0] if len(detected_units) > 0 else None
    to_unit = detected_units[1] if len(detected_units) > 1 else None

    return value, from_unit, to_unit


# Load NLP model
nlp = spacy.blank("en")

def extract_units_from_text(text):
    """Extracts value, from_unit, and to_unit from user input."""
    doc = nlp(text)

    value = None
    detected_units = []  # Store detected units

    print(f"\n🔍 Debugging NLP Extraction: {text}")
    print(f"Tokens Detected: {[token.text for token in doc]}")  # Show all tokens

    for token in doc:
        token_text = token.text.lower().strip()

        # First, check if token is a numeric string using regex (e.g., "5" or "5.0")
        if re.match(r'^\d+(\.\d+)?$', token_text):
            try:
                value = float(token_text)
            except ValueError:
                pass  # Should rarely happen
        else:
            # If not a plain number, try converting word-based numbers (e.g., "five")
            try:
                converted_value = w2n.word_to_num(token_text)
                value = float(converted_value)
            except ValueError:
                pass  # Not a number word, ignore

        # Check if token is a valid unit from unit_mappings
        if token_text in unit_mappings:
            detected_units.append(unit_mappings[token_text])
        # Detect currency codes (e.g., USD, EUR)
        elif len(token_text) == 3 and token_text.isalpha() and token_text.upper() not in unit_mappings:
            detected_units.append(token_text.upper())

    print(f"🔎 Extracted Value: {value}, Units: {detected_units}")

    # Assign detected units properly
    from_unit = detected_units[0] if len(detected_units) > 0 else None
    to_unit = detected_units[1] if len(detected_units) > 1 else None

    return value, from_unit, to_unit

    
# Logic for temperature conversion
def convert_temperature (value, from_unit, to_unit):
    """ Handles temperature converison separately. """
    if from_unit == to_unit :
        return value
    if from_unit == "Celsius" :
        return value * 9/5 + 32 if to_unit == "Fahrenheit" else value + 273.15
    if from_unit == "Fahrenheit" :
        return (value - 32) * 5/9 if to_unit == "Celsius" else (value -32) * 5/9 + 273.15
    if from_unit == "Kelvin" :
        return value - 273.15 if to_unit == "Clesius" else (value - 273.15) * 9/5 + 32

# Logic for currency conversion
def convert_currency(value, from_currency, to_currency):
    """Fetch real-time exchange rates using ExchangeRate-API."""
    API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
    
    if not API_KEY:
        return "Error: API key is missing!"
      
    from_currency = from_currency.upper()  # Ensure uppercase
    to_currency = to_currency.upper()
      
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency.upper()}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            return f"API Error: {data['error-type']}"
        
        if to_currency.upper() not in data["conversion_rates"]:
            return "Invalid currency code!"
        
        exchange_rate = data["conversion_rates"][to_currency.upper()]
        return value * exchange_rate

    except Exception as e:
        return f"Error: {str(e)}"

# Logic for units convesion
def convert_units (category, value, from_unit, to_unit):
    """ Converts units based on the selected category. """
    if category == "Temperature" :
        return convert_temperature(value, from_unit, to_unit)
    elif category == "Currency" :
        return convert_currency(value, from_unit, to_unit)
    else: 
        return value * (conversion_factors[category][to_unit] / conversion_factors[category][from_unit])
    
# UI
st.set_page_config(
    page_title = "Universal Unit Converter",
    page_icon = '🔄',
    layout = 'wide'
)
# Dark Mode Toggle
dark_mode = st.toggle("🌙 Dark Mode")

st.title("🧠 Smart Universal Unit Converter with NLP & Dropdowns")

tab1, tab2 = st.tabs(["🔽 Dropdown Selection", "🧠 NLP Text Input"])

with tab1:
    st.sidebar.header("Select Conversion Type")
    category = st.sidebar.selectbox("Choose a category" , list(conversion_factors.keys()))

    if category == "Currency" :
        st.subheader("💰 Currency Conversion")
        st.write("⚠️ Currency conversions require an internet connection!")
        value = st.number_input("Enter amount:", min_value=0.0, format="%f")
        from_unit = st.text_input("From Currency (e.g., USD, EUR, GBP)")
        to_unit = st.text_input("To Currency (e.g., USD, EUR, GBP)")
        if st.button("Convert") and from_unit and to_unit:
            try : 
                result = convert_currency(value, from_unit.upper(), to_unit.upper())
                st.success(f"{value} {from_unit.upper()} = {result:.2f} {to_unit.upper()}")
            except :
                st.error("Invalid currency code or API issue.")
    else :
        if category == "Temperature":
            st.subheader("🌡️ Temperature Conversion")
        elif category == "Weight":
            st.subheader("⚖️ Weight Conversion")
        else :
            st.subheader("📏 Length Conversion")
        value = st.number_input("Enter value:", format="%f")
        if category == "Temperature" :
            from_unit = st.selectbox("From Unit", conversion_factors["Temperature"])
            to_unit = st.selectbox("To Unit", conversion_factors["Temperature"])
        else :
            from_unit = st.selectbox("From Unit", list(conversion_factors[category].keys()))
            to_unit = st.selectbox("To Unit", list(conversion_factors[category].keys()))
        if st.button("Convert"):
            result = convert_units(category, value, from_unit, to_unit)
            st.success(f"{value} {from_unit} = {result:.6f} {to_unit}")
    
with tab2:
    st.write("Type your conversion in plain English (e.g., 'Convert 5 meters to feet')")
    user_input = st.text_input("Enter conversion query:")

    if st.button("Convert using NLP"):
        value, from_unit, to_unit = extract_units_from_text(user_input)

        if value is None :
            st.error("❌ Could not detect a numerical value. Please enter a valid number.")
        elif from_unit is None :
            st.error("❌ Could not detect the 'From' unit. Please try again.")
        elif to_unit is None :
            st.error("❌ Could not detect the 'To' unit. Please try again.")
        else:
            category = None
            for cat, units in conversion_factors.items():
                if from_unit in units and to_unit in units:
                    category = cat
                    break
                
            # Add Currency Detection  
            if category is None and len(from_unit) == 3 and len(to_unit) == 3:  
              category = "Currency"
    
            if category:
                result = convert_units(category, value, from_unit, to_unit)
                st.success(f"{value} {from_unit} = {result:.6f} {to_unit}")
            else:
                st.error("Invalid unit conversion.")
    
    


# Apply CSS for Dark Mode
if dark_mode:
    st.markdown(
        """
        <style>
            body {
                background-color: #121212;
                color: white;
            }
            .stApp {
                background-color: #121212;
            }
            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: #1E1E1E !important;
            }
            /* Top Navbar */
            header {
                background-color: #121212 !important;
            }
            /* Inputs (Text, Number, TextArea) */
            input, textarea {
                background-color: #333 !important;
                color: white !important;
                border-radius: 5px !important;
                border: 1px solid #555 !important;
            }
            /* Titles & Headers */
            h1, h2, h3, h4, h5, h6, p {
                color: white !important;
            }           
            /* Buttons */
            .stButton>button {
                background-color: #D72638 !important;  /* Deep Red */
                color: white !important;
                border-radius: 10px !important;
                transition: 0.3s;
            }      
            .stButton>button:hover {
                background-color: #B71C30 !important; /* Darker Red */
            }  
            </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
            body {
                background-color: white;
                color: black;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
