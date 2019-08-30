# Required imports
from pymongo import MongoClient
from config import config_values
import pandas as pd

# Plotting Library
import matplotlib
matplotlib.use('Agg') # backend for writing graphs to a file. 
import matplotlib.pyplot as plt

# Connect to MongoDB server via client
client = MongoClient()
db = client.test

# Collections
five_day_forecast = db.five_day_forecast # 5 days/3 hour forecast
sixteen_day_forecast = db.sixteen_day_forecast # 16 days/daily forecast
weather_maps = db.weather_maps # weather maps






