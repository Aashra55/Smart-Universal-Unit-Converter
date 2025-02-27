import os
import streamlit as st
import requests
from dotenv import load_dotenv
import spacy
from word2number import w2n
import re
from spacy.matcher import Matcher
import math

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
        "Micrometers": 1e6,   # 1 meter = 1,000,000 micrometers
        "Nanometers": 1e9,    # 1 meter = 1,000,000,000 nanometers
        "Miles": 0.000621371,
        "Yards": 1.09361,
        "Feet": 3.28084,
        "Inches": 39.3701,
    },
    "Mass": {
        "Kilograms": 1,
        "Grams": 1000,
        "Milligrams": 1e6,
        "Pounds": 2.20462,
        "Ounces": 35.274
    },
    "Time":{
        "Hours":1,
        "Minutes":60,
        "Seconds":3600
    },
    "Area":{
    "Square Meters": 1,               # Base unit
    "Square Kilometers": 1e-6,          # 1 m² = 0.000001 km²
    "Square Centimeters": 10000,        # 1 m² = 10,000 cm²
    "Square Millimeters": 1e6,          # 1 m² = 1,000,000 mm²
    "Square Miles": 3.861e-7,           # 1 m² ≈ 0.0000003861 mi²
    "Square Yards": 1.19599,            # 1 m² ≈ 1.19599 yd²
    "Square Feet": 10.7639,             # 1 m² ≈ 10.7639 ft²
    "Square Inches": 1550.0031,         # 1 m² ≈ 1550.0031 in²
    "Hectares": 0.0001,                # 1 m² = 0.0001 hectares (1 ha = 10,000 m²)
    "Acres": 0.000247105               # 1 m² ≈ 0.000247105 acres (1 acre ≈ 4046.86 m²)
    },
    "Volume":{
    "Cubic Meters": 1,            # Base unit
    "Liters": 1000,               # 1 cubic meter = 1000 liters
    "Milliliters": 1e6,           # 1 cubic meter = 1,000,000 milliliters
    "Cubic Centimeters": 1e6,     # 1 cubic meter = 1,000,000 cubic centimeters (1 cc = 1 mL)
    "Cubic Inches": 61023.7441,   # 1 cubic meter ≈ 61,023.7441 cubic inches
    "Cubic Feet": 35.3147,        # 1 cubic meter ≈ 35.3147 cubic feet
    "Gallons": 264.172,           # 1 cubic meter ≈ 264.172 US gallons
    "Quarts": 1056.69,            # 1 cubic meter ≈ 1056.69 US quarts
    "Pints": 2113.38             # 1 cubic meter ≈ 2113.38 US pints
    },
    "Digital Storage" : {
    "Bytes": 1,                           # Base unit: 1 Byte = 1 Byte
    "Kilobytes": 1/1024,                  # 1 Byte = 1/1024 Kilobytes
    "Megabytes": 1/(1024**2),             # 1 Byte = 1/(1024^2) Megabytes
    "Gigabytes": 1/(1024**3),             # 1 Byte = 1/(1024^3) Gigabytes
    "Terabytes": 1/(1024**4),             # 1 Byte = 1/(1024^4) Terabytes
    "Petabytes": 1/(1024**5),             # 1 Byte = 1/(1024^5) Petabytes
    "Bits": 8                           # 1 Byte = 8 Bits
    },
    "Energy":{
    "Joules": 1,                   # Base unit
    "Kilojoules": 0.001,           # 1 Joule = 0.001 kJ (1 kJ = 1000 Joules)
    "Calories": 1/4.184,           # 1 calorie ≈ 4.184 Joules
    "Kilocalories": 1/4184,        # 1 kilocalorie (food Calorie) = 4184 Joules
    "Watt-hours": 1/3600,          # 1 Wh = 3600 Joules
    "BTU": 1/1055.06               # 1 BTU ≈ 1055.06 Joules
    },
    "Frequency":{
    "Hertz": 1,                   # Base unit: 1 Hz = 1 Hz
    "Kilohertz": 1e-3,            # 1 Hz = 0.001 kHz
    "Megahertz": 1e-6,            # 1 Hz = 0.000001 MHz
    "Gigahertz": 1e-9,            # 1 Hz = 0.000000001 GHz
    "Revolutions per minute": 60  # 1 Hz = 60 RPM
    },
    "Fuel Economy" : {
        "Miles per Gallon (US)": 1,
        "Miles per Gallon (UK)": 1.20095,
        "Kilometers per Liter": 0.425144,
        "Liters per 100 Kilometers": 235.214
        },
    "Data Transfer Rate": {
    "Bits per Second": 1,                        # Base unit
    "Kilobits per Second": 1e3,                  # 1 Kbps = 1,000 bits
    "Megabits per Second": 1e6,                  # 1 Mbps = 1,000,000 bits
    "Gigabits per Second": 1e9,                  # 1 Gbps = 1,000,000,000 bits
    "Bytes per Second": 8,                       # 1 Bps = 8 bits
    "Kilobytes per Second": 8e3,                 # 1 KBps = 8,000 bits
    "Megabytes per Second": 8e6,                 # 1 MBps = 8,000,000 bits
    "Gigabytes per Second": 8e9                  # 1 GBps = 8,000,000,000 bits
    },
    "Plane Angle" : {
    "Radians": 1,                       # Base unit
    "Degrees": 180 / math.pi,             # 1 radian = 57.2958 degrees
    "Gradians": 200 / math.pi,            # 1 radian = 63.662 gradians
    "Turns": 1 / (2 * math.pi),           # 1 radian = 0.15915 turns
    "Arcminutes": 10800 / math.pi,         # 1 radian = 3437.75 arcminutes
    "Arcseconds": 648000 / math.pi         # 1 radian = 206264.81 arcseconds
    },
    "Pressure" : {
    "Pascals": 1,                 # Base unit: 1 Pa = 1 Pa
    "Kilopascals": 1e-3,          # 1 Pa = 0.001 kPa, so kPa factor is 1/1000
    "Bars": 1e-5,                 # 1 Pa = 0.00001 bar, since 1 bar = 100,000 Pa
    "Atmospheres": 1/101325,      # 1 Pa = 1/101325 atm
    "Torr": 1/133.322,            # 1 Pa = 1/133.322 torr (or mmHg)
    "PSI": 1/6894.76              # 1 Pa = 1/6894.76 psi
    },
    "Speed" : {
    "Meters per Second": 1,            # Base unit
    "Kilometers per Hour": 3.6,          # 1 m/s = 3.6 km/h
    "Miles per Hour": 2.23694,           # 1 m/s = 2.23694 mph
    "Feet per Second": 3.28084,          # 1 m/s = 3.28084 ft/s
    "Knots": 1.94384                   # 1 m/s = 1.94384 knots
    },
    "Temperature" : ["Celsius", "Fahrenheit", "Kelvin"],  
    "Currency" : "Dynamic",  # Handled via API
}

# Dictionary for unit mappings
unit_mappings = {
    # Meters
    "meter": "Meters",
    "meters": "Meters",
    "metre": "Meters",
    "metres": "Meters",
    "m":"Meters",
    
    #Kilometers
    "kilometer": "Kilometers",
    "kilometers": "Kilometers",
    "kilometre": "Kilometers",
    "kilometres": "Kilometers",
    "km":"Kilometers",
    
    # "Centimeters"
    "cm": "Centimeters",
    "centimeter": "Centimeters",
    "centimeters": "Centimeters",
    
    #Milimeters
    "mm": "Millimeters",
    "millimeter": "Millimeters", 
    "millimeters": "Millimeters",
    
    # Micrometers
    "micrometer": "Micrometers",
    "micrometers": "Micrometers",
    "µm": "Micrometers",  
    "um": "Micrometers",  
    
    # Nanometers
    "nanometer": "Nanometers",
    "nanometers": "Nanometers",
    "nm": "Nanometers",
    
    # Miles
    "mile": "Miles",
    "miles": "Miles",
    
    # Yards
    "yard": "Yards",
    "yards": "Yards",
    
    # Feet
    "feet": "Feet",
    "foot": "Feet",
    
    # Inches
    "inch": "Inches", 
    "inches": "Inches",
    
    # Kilograms
    "kg": "Kilograms",
    "kilogram": "Kilograms",
    "kilograms": "Kilograms",
    
    # Grams
    "gram": "Grams",
    "grams": "Grams",
    "gm":"Grams",
    
    # Miligrams
    "mg": "Milligrams",
    "milligram": "Milligrams",
    "milligrams": "Milligrams",
    "pound": "Pounds",
    
    # Pounds and Ounces
    "pounds": "Pounds",
    "ounce": "Ounces",
    "ounces": "Ounces",
    
    # Temperature Units
    "celsius": "Celsius",
    "fahrenheit": "Fahrenheit",
    "kelvin": "Kelvin",
    
    # Hours
    "hour":"Hours",
    "hr":"Hours",
    "hours":"Hours",
    "Hour":"Hours",
    
    # Minutes
    "minute":"Minutes",
    "Minute":"Minutes",
    "minutes":"Minutes",
    "min":"Minutes",
    
    # Seconds
    "second":"Seconds",
    "Second":"Seconds",
    "seconds":"Seconds",
    "s":"Seconds",
    
    # Square Meters
    "square meter": "Square Meters",
    "square meters": "Square Meters",
    "sqm": "Square Meters",
    "m2": "Square Meters",
    
    # Square Kilometers
    "square kilometer": "Square Kilometers",
    "square kilometers": "Square Kilometers",
    "sqkm": "Square Kilometers",
    "km2": "Square Kilometers",
    
    # Square Centimeters
    "square centimeter": "Square Centimeters",
    "square centimeters": "Square Centimeters",
    "sqcm": "Square Centimeters",
    "cm2": "Square Centimeters",
    
    # Square Millimeters
    "square millimeter": "Square Millimeters",
    "square millimeters": "Square Millimeters",
    "sqmm": "Square Millimeters",
    "mm2": "Square Millimeters",
    
    # Square Miles
    "square mile": "Square Miles",
    "square miles": "Square Miles",
    "sqmi": "Square Miles",
    "mi2": "Square Miles",
    
    # Square Yards
    "square yard": "Square Yards",
    "square yards": "Square Yards",
    "sqyd": "Square Yards",
    "yd2": "Square Yards",
    
    # Square Feet
    "square foot": "Square Feet",
    "square feet": "Square Feet",
    "sqft": "Square Feet",
    "ft2": "Square Feet",
    
    # Square Inches
    "square inch": "Square Inches",
    "square inches": "Square Inches",
    "sqin": "Square Inches",
    "in2": "Square Inches",
    
    # Hectares
    "hectare": "Hectares",
    "hectares": "Hectares",
    "ha": "Hectares",
    
    # Acres
    "acre": "Acres", "acres": "Acres",
    
    # Cubic Meters
    "cubic meter": "Cubic Meters",
    "cubic meters": "Cubic Meters",
    "m3": "Cubic Meters",
    "cu m": "Cubic Meters",
    "cubic metre": "Cubic Meters",
    "cubic metres": "Cubic Meters",

    # Liters
    "liter": "Liters",
    "liters": "Liters",
    "l": "Liters",
    "ltr": "Liters",

    # Milliliters
    "milliliter": "Milliliters",
    "milliliters": "Milliliters",
    "ml": "Milliliters",
    "millilitre": "Milliliters",
    "millilitres": "Milliliters",

    # Cubic Centimeters
    "cubic centimeter": "Cubic Centimeters",
    "cubic centimeters": "Cubic Centimeters",
    "cc": "Cubic Centimeters",
    "cm3": "Cubic Centimeters",

    # Cubic Inches
    "cubic inch": "Cubic Inches",
    "cubic inches": "Cubic Inches",
    "in3": "Cubic Inches",

    # Cubic Feet
    "cubic foot": "Cubic Feet",
    "cubic feet": "Cubic Feet",
    "ft3": "Cubic Feet",

    # Gallons
    "gallon": "Gallons",
    "gallons": "Gallons",
    "gal": "Gallons",

    # Quarts
    "quart": "Quarts",
    "quarts": "Quarts",
    "qt": "Quarts",

    # Pints
    "pint": "Pints",
    "pints": "Pints",
    "pt": "Pints",
    
    # Bytes 
    "byte": "Bytes",
    "bytes": "Bytes",
    "B": "Bytes",  

    # Bits 
    "bit": "Bits",
    "bits": "Bits",
    "b": "Bits",

    # Kilobytes
    "kilobyte": "Kilobytes",
    "kilobytes": "Kilobytes",
    "kb": "Kilobytes",
    "kB": "Kilobytes",  

    # Megabytes
    "megabyte": "Megabytes",
    "megabytes": "Megabytes",
    "mb": "Megabytes",
    "MB": "Megabytes",

    # Gigabytes
    "gigabyte": "Gigabytes",
    "gigabytes": "Gigabytes",
    "gb": "Gigabytes",
    "GB": "Gigabytes",

    # Terabytes
    "terabyte": "Terabytes",
    "terabytes": "Terabytes",
    "tb": "Terabytes",
    "TB": "Terabytes",

    # Petabytes
    "petabyte": "Petabytes",
    "petabytes": "Petabytes",
    "pb": "Petabytes",
    "PB": "Petabytes",
    
    # Joules
    "joule": "Joules",
    "joules": "Joules",
    "j": "Joules",
    
    # Kilojoules
    "kilojoule": "Kilojoules",
    "kilojoules": "Kilojoules",
    "kj": "Kilojoules",
    
    # Calories
    "calorie": "Calories",
    "calories": "Calories",
    "cal": "Calories",
    
    # Kilocalories
    "kilocalorie": "Kilocalories",
    "kilocalories": "Kilocalories",
    "kcal": "Kilocalories",
    
    # Watt-hours
    "watt hour": "Watt-hours",
    "watt hours": "Watt-hours",
    "wh": "Watt-hours",
    
    # BTU
    "btu": "BTU",
    "british thermal unit": "BTU",
    "british thermal units": "BTU",
    
    # Hertz
    "hertz": "Hertz",
    "hz": "Hertz",
    
    # Kilohertz
    "kilohertz": "Kilohertz",
    "khz": "Kilohertz",
    
    # Megahertz
    "megahertz": "Megahertz",
    "mhz": "Megahertz",
    
    # Gigahertz
    "gigahertz": "Gigahertz",
    "ghz": "Gigahertz",
    
    # Revolutions per minute
    "revolutions per minute": "Revolutions per minute",
    "rpm": "Revolutions per minute",
    "revs per minute": "Revolutions per minute",
    "r.p.m": "Revolutions per minute",
    
    # Miles per Gallon (US)
    "mpg": "Miles per Gallon (US)",
    "miles per gallon": "Miles per Gallon (US)",
    "us mpg": "Miles per Gallon (US)",
    
    # Miles per Gallon (UK)
    "mpg (uk)": "Miles per Gallon (UK)",
    "uk mpg": "Miles per Gallon (UK)",
    "miles per gallon (uk)" : "Miles per Gallon (UK)",
    
    # Kilometers per Liter
    "km/l": "Kilometers per Liter",
    "kilometers per liter": "Kilometers per Liter",
    "kilometres per litre": "Kilometers per Liter",
    
    # Liters per 100 Kilometers
    "l/100km": "Liters per 100 Kilometers",
    "l/100 km": "Liters per 100 Kilometers",
    "liters per 100 kilometers": "Liters per 100 Kilometers",
    "litres per 100 kilometres": "Liters per 100 Kilometers",
    
        # Bits per Second
    "bps": "Bits per Second",
    "bit per second": "Bits per Second",
    "bits per second": "Bits per Second",
    
    # Kilobits per Second
    "kbps": "Kilobits per Second",
    "kilobit per second": "Kilobits per Second",
    "kilobits per second": "Kilobits per Second",
    
    # Megabits per Second
    "mbps": "Megabits per Second",
    "megabit per second": "Megabits per Second",
    "megabits per second": "Megabits per Second",
    
    # Gigabits per Second
    "gbps": "Gigabits per Second",
    "gigabit per second": "Gigabits per Second",
    "gigabits per second": "Gigabits per Second",
    
    # Bytes per Second
    "Bps": "Bytes per Second",
    "byte per second": "Bytes per Second",
    "bytes per second": "Bytes per Second",
    
    # Kilobytes per Second
    "KBps": "Kilobytes per Second",
    "kilobyte per second": "Kilobytes per Second",
    "kilobytes per second": "Kilobytes per Second",
    
    # Megabytes per Second
    "MBps": "Megabytes per Second",
    "megabyte per second": "Megabytes per Second",
    "megabytes per second": "Megabytes per Second",
    
    # Gigabytes per Second
    "GBps": "Gigabytes per Second",
    "gigabyte per second": "Gigabytes per Second",
    "gigabytes per second": "Gigabytes per Second",
    
    # Radians
    "radian": "Radians",
    "radians": "Radians",
    "rad": "Radians",
    
    # Degrees
    "degree": "Degrees",
    "degrees": "Degrees",
    "°": "Degrees",
    
    # Gradians (also called gons)
    "gradian": "Gradians",
    "gradians": "Gradians",
    "grad": "Gradians",
    "gons": "Gradians",
    "gon": "Gradians",
    
    # Turns
    "turn": "Turns",
    "turns": "Turns",
    
    # Arcminutes (for angle)
    "arcminute": "Arcminutes",
    "arcminutes": "Arcminutes",
    
    # Arcseconds (for angle)
    "arcsecond": "Arcseconds",
    "arcseconds": "Arcseconds",
    
    # Pascals
    "pascal": "Pascals",
    "pascals": "Pascals",
    "pa": "Pascals",
    
    # Kilopascals
    "kilopascal": "Kilopascals",
    "kilopascals": "Kilopascals",
    "kpa": "Kilopascals",
    
    # Bars
    "bar": "Bars",
    "bars": "Bars",
    
    # Atmospheres
    "atmosphere": "Atmospheres",
    "atmospheres": "Atmospheres",
    "atm": "Atmospheres",
    
    # Torr
    "torr": "Torr",
    "mmhg": "Torr",
    
    # PSI
    "psi": "PSI", 
    
    # Meters per Second
    "m/s": "Meters per Second",
    "meters per second": "Meters per Second",
    "meter per second": "Meters per Second",
    
    # Kilometers per Hour
    "km/h": "Kilometers per Hour",
    "kilometers per hour": "Kilometers per Hour",
    "kilometres per hour": "Kilometers per Hour",
    "kph": "Kilometers per Hour",
    
    # Miles per Hour
    "mph": "Miles per Hour",
    "miles per hour": "Miles per Hour",
    
    # Feet per Second
    "ft/s": "Feet per Second",
    "feet per second": "Feet per Second",
    
    # Knots
    "knots": "Knots",
    "knot": "Knots"
}
 
number_inwords = [
    'one', 'two', 'six', 'ten'
]

patterns = [
        # Fuel Economy patterns
        [{"LOWER": "miles"}, {"LOWER": "per"}, {"LOWER": "gallon"}],
        [{"LOWER": "us"}, {"LOWER": "mpg"}],
        [{"LOWER": "mpg"}],  # covers short form "mpg" (if context permits)
        [{"LOWER": "mpg"}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": "uk"}],
        [{"LOWER": "uk"}, {"LOWER": "mpg"}],
        [{"LOWER": "miles"}, {"LOWER": "per"}, {"LOWER": "gallon"}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": "uk"}],
        [{"LOWER": "km/l"}],
        [{"LOWER": "kilometers"}, {"LOWER": "per"}, {"LOWER": "liter"}],
        [{"LOWER": "kilometres"}, {"LOWER": "per"}, {"LOWER": "litre"}],
        [{"LOWER": "l/100km"}],
        [{"LOWER": "l/100"}, {"LOWER": "km"}],
        [{"LOWER": "liters"}, {"LOWER": "per"}, {"LOWER": "100"}, {"LOWER": "kilometers"}],
        [{"LOWER": "litres"}, {"LOWER": "per"}, {"LOWER": "100"}, {"LOWER": "kilometres"}],
        # Energy patterns (Watt-hour)
        [{"LOWER": "watt"}, {"LOWER": "hour"}],
        [{"LOWER": "watt"}, {"LOWER": "hours"}],
        # Frequency patterns (Revolutions per minute)
        [{"LOWER": "revolutions"}, {"LOWER": "per"}, {"LOWER": "minute"}],
        [{"LOWER": "revs"}, {"LOWER": "per"}, {"LOWER": "minute"}],
        [{"LOWER": "rpm"}]
]

# Conversion History
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []  

def add_to_history(input_value, from_unit, to_unit, result, method):
    st.session_state.conversion_history.append({
        'input': input_value,
        'from_unit': from_unit,
        'to_unit': to_unit,
        'result': result,
        'method': method  # e.g., "Dropdown" or "NLP"
    })
    
def display_history():
    st.sidebar.subheader("Conversion History")
    if st.session_state.conversion_history:
        for record in st.session_state.conversion_history:
            st.sidebar.write(f"{record['input']} {record['from_unit']} → {record['result']:.6f} {record['to_unit']} (via {record['method']})")
    else:
        st.sidebar.write("No conversions yet.")

def extract_units_from_text(text):
    """
    Extracts a numerical value, a 'from' unit, and a 'to' unit from input text.
    Uses the Matcher to capture multi-word expressions (e.g. "us mpg" or "l/100 km")
    and then processes remaining tokens for single-word units.
    Overlapping matches are filtered to avoid duplicates.
    """
    doc = nlp(text)
    matcher = Matcher(nlp.vocab)
    matcher.add("MULTIWORD_UNITS", patterns)
    
    # Get all multi-word matches
    raw_matches = matcher(doc)
    # Sort by start index and descending span length (to prefer longer matches)
    raw_matches = sorted(raw_matches, key=lambda x: (x[1], -(x[2]-x[1])))
    
    # Filter out overlapping matches: keep only matches that don't overlap with already accepted spans
    filtered_matches = []
    occupied = set()
    for match_id, start, end in raw_matches:
        if any(i in occupied for i in range(start, end)):
            continue
        filtered_matches.append((start, end))
        for i in range(start, end):
            occupied.add(i)
    
    # Build detected_units list from filtered multi-word matches
    detected_units = []  # List of tuples: (token_index, unit)
    for start, end in filtered_matches:
        span = doc[start:end]
        unit_str = span.text.lower().strip()
        # Look up the whole span in unit_mappings.
        if unit_str in unit_mappings:
            detected_units.append((start, unit_mappings[unit_str]))
    
    value = None
    # Process individual tokens (skipping those that were part of any multi-word match)
    for i, token in enumerate(doc):
        if i in occupied:
            continue
        token_text = token.text.lower().strip()
        # If token is a number (digit string)
        if re.match(r'^\d+(\.\d+)?$', token_text):
            try:
                value = float(token_text)
            except ValueError:
                pass
        else:
            # Try converting word-based numbers (e.g., "one")
            try:
                converted_value = w2n.word_to_num(token_text)
                value = float(converted_value)
            except Exception:
                pass
            # Check if token itself is a recognized unit
            if token_text in unit_mappings:
                detected_units.append((i, unit_mappings[token_text]))
            # For potential 3-letter currency codes, etc.
            elif len(token_text) == 3 and token_text not in number_inwords and token_text.isalpha():
                detected_units.append((i, token_text.upper()))
    
    # Sort detected units by their token index (to preserve original order)
    detected_units.sort(key=lambda x: x[0])
    final_units = [unit for idx, unit in detected_units]
    
    # Debug output to help you troubleshoot:
    print("\n🔍 Debugging NLP Extraction:", text)
    print("Tokens Detected:", [token.text for token in doc])
    print("Raw Matches (start, end):", raw_matches)
    print("Filtered Multi-word Matches (start, end):", filtered_matches)
    print("Detected Units with Indices:", detected_units)
    print("Final Detected Units:", final_units)
    print("Extracted Value:", value)
    
    # Return the first detected unit as 'from_unit' and the second as 'to_unit'
    from_unit = final_units[0] if len(final_units) > 0 else None
    to_unit = final_units[1] if len(final_units) > 1 else None
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
        return value - 273.15 if to_unit == "Celsius" else (value - 273.15) * 9/5 + 32

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

# Fuel Economy
def convert_fuel_economy(value, from_unit, to_unit):
    """
    Converts fuel economy values between supported units.
    Base unit: Liters per 100 Kilometers (L/100 km)
    """
    # Convert input value to the base unit (L/100 km)
    if from_unit == "Miles per Gallon (US)":
        base_value = 235.214583 / value
    elif from_unit == "Miles per Gallon (UK)":
        base_value = 282.4809363 / value
    elif from_unit == "Kilometers per Liter":
        base_value = 100 / value
    elif from_unit == "Liters per 100 Kilometers":
        base_value = value
    else:
        raise ValueError("Unsupported input unit: " + from_unit)
    
    # Convert from the base unit to the target unit
    if to_unit == "Miles per Gallon (US)":
        result = 235.214583 / base_value
    elif to_unit == "Miles per Gallon (UK)":
        result = 282.4809363 / base_value
    elif to_unit == "Kilometers per Liter":
        result = 100 / base_value
    elif to_unit == "Liters per 100 Kilometers":
        result = base_value
    else:
        raise ValueError("Unsupported output unit: " + to_unit)
    
    return result
print(convert_fuel_economy(30, "Miles per Gallon (US)", "Liters per 100 Kilometers"))

fuel_economy_units = [
    "Miles per Gallon (US)",
    "Miles per Gallon (UK)",
    "Kilometers per Liter",
    "Liters per 100 Kilometers"
]

# Logic for units convesion
def convert_units (category, value, from_unit, to_unit):
    """ Converts units based on the selected category. """
    if category == "Temperature" :
        return convert_temperature(value, from_unit, to_unit)
    elif category == "Currency" :
        return convert_currency(value, from_unit, to_unit)
    elif category == "Fuel Economy": 
        return convert_fuel_economy(value, from_unit, to_unit)
    else: 
        return value * (conversion_factors[category][to_unit] / conversion_factors[category][from_unit])
    
# UI
st.set_page_config(
    page_title = "Smart Universal Unit Converter",
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
    elif category == "Fuel Economy":
        st.subheader("⛽ Fuel Economy Conversion")
        value = st.number_input("Enter value:", min_value=0.0, format="%f")
        from_unit = st.selectbox("From Fuel Economy Unit",fuel_economy_units)
        to_unit = st.selectbox("To Fuel Economy Unit", fuel_economy_units)
        if st.button("Convert") and from_unit and to_unit:
            result = convert_fuel_economy(value, from_unit, to_unit)
            st.success(f"{value} {from_unit} = {result:.4f} {to_unit}")
    else :
        if category == "Temperature":
            st.subheader("🌡️ Temperature Conversion")
        elif category == "Mass":
            st.subheader("⚖️ Mass Conversion")
        elif category == "Time":
            st.subheader("⌚ Time Conversion")
        elif category == "Area":
            st.subheader("🔲 Area Conversion")
        elif category == "Volume":
            st.subheader("🎲 Volume Conversion")
        elif category == "Digital Storage":
            st.subheader("💾 Digital Storage Conversion")
        elif category == "Energy":
            st.subheader("⚡ Energy Conversion")
        elif category == "Frequency":
            st.subheader("📡 Frequency Conversion")
        elif category == "Fuel Economy":
            st.subheader("⛽ Fuel Economy Conversion")
        elif category == "Data Transfer Rate":
            st.subheader("📶 Data Transfer Rate Conversion")
        elif category == "Plane Angle":
            st.subheader("📐 Plane Angle Conevrsion")
        elif category == "Pressure" :
            st.subheader("💨 Pressure Conversion")
        elif category == "Speed" :
            st.subheader("🚀 Speed Conversion")
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
            st.success(f"{value} {from_unit} = {result:.4f} {to_unit}")
            add_to_history(value, from_unit, to_unit, result, "Dropdown")

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
                st.success(f"{value} {from_unit} = {result:.4f} {to_unit}")
                add_to_history(value, from_unit, to_unit, result, "NLP")
            else:
                st.error("Invalid unit conversion.")
display_history()

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


