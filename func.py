# Required imports
import datetime
import json
import urllib.request
import webbrowser
import os
import logging
import sys
import pandas as pd
from pymongo import MongoClient
from config import config_values

# Plotting Library
import matplotlib
matplotlib.use('Agg') # backend for writing graphs to a file. 
import matplotlib.pyplot as plt 

# use five_Day_forecast.drop() to clear the collection. 
# Connect to MongoDB server via client
client = MongoClient()
db = client.test

# Collections
five_day_forecast = db.five_day_forecast # 5 days/3 hour forecast
sixteen_day_forecast = db.sixteen_day_forecast # 16 days/daily forecast
weather_maps = db.weather_maps # weather maps

# convert time to HH:MM:SS
def modify_time(time):
    converted_time = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%I:%M %p')
    return converted_time


# URL builder for API call to OpenWeatherMap
def url_builder_days(city, country):
    user_api = '2caff9e767d0e868acf776c7f31c4b93'  # API for openweathermap
    unit = 'metric'  #Fahrenheit: imperial, Celsius: metric, Kelvin: default
    api = 'http://api.openweathermap.org/data/2.5/forecast?q={city},{country}'.format(city=city, country=country)
    full_api_url = api + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url


# URL builder for Weather maps
def url_builder_maps(layer, z, x, y):
    user_api = '2caff9e767d0e868acf776c7f31c4b93'
    api_maps = 'https://tile.openweathermap.org/map/{layer}/{z}/{x}/{y}.png?'.format(layer=layer, z=z, x=x, y=y)
    full_api_url_maps = api_maps + '&APPID=' + user_api
    return full_api_url_maps


# Saving the maps locally and insert maps into mongodb weather_maps collection
def get_save_map(full_api_url_maps, city, country):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    weather_maps_dir = os.path.join(current_dir, 'maps')
    if not os.path.exists(weather_maps_dir):
        os.mkdir(weather_maps_dir)

    binary_image_data = urllib.request.urlopen(full_api_url_maps).read() # converting maps to binary data. 
    f = open(weather_maps_dir + '/' + city + '_' + country + '.png', 'wb')
    f.write(binary_image_data)
    f.close()

    map_dict = {'city': city, 'country': country, 'image': binary_image_data}
    weather_maps.insert(map_dict)

# Main function to start the program. 
def start_main(type):
    if type == 'five_days':
        for value in config_values['locations']:
            url_days = url_builder_days(value['city'], value['country'])
            get_save_forecast(url_days)

    elif type == 'sixteen_days':
        print('Only for paid users')# only for paid users

    elif type == 'weather_maps':
        for i, value in enumerate(config_values['locations']):
            # x = x tile, y = y tile, z = zoom level
            url_maps = url_builder_maps('precipitation_new', value['z'], value['x'], value['y']) # we can use temp_new, clouds_new,etc
            get_save_map(url_maps, value['city'], value['country'])
            # open each map into separate tabs
            webbrowser.open_new_tab(url_maps)

# Saving five day/3 hrs forecast data into five_day_forecast collection. 
def get_save_forecast(full_api_url):
    url = urllib.request.urlopen(full_api_url)
    output = url.read().decode('utf-8')
    raw_api_dict = json.loads(output)
    url.close()
    update_dict = {'city': raw_api_dict['city']['name'],
                   'country': raw_api_dict['city']['country']}
    dt_txts = []
    temparatures = []
    for record in raw_api_dict['list']:
        record.update(update_dict)
        five_day_forecast.insert(record) # insert into db
        check_weather(record) # print alerts and weather
        dt_time = datetime.datetime.strptime(record['dt_txt'], "%Y-%m-%d %H:%M:%S")
        dt_txts.append(dt_time.strftime('%d %b, %H'))
        temparatures.append(record['main']['temp'])
        
    # For saving and inserting graphs
    current_dir_graph = os.path.dirname(os.path.abspath(__file__))
    graph_dir = os.path.join(current_dir_graph, 'graphs')
    if not os.path.exists(graph_dir):
        os.mkdir(graph_dir)
    plt.figure(figsize=(13, 9))
    plt.plot(dt_txts,temparatures)
    plt.title(update_dict['city'])
    plt.axis([0,max(dt_txts),0,max(temparatures)])
    plt.xticks(dt_txts, rotation=90)
    for i, txt in enumerate(temparatures):
        plt.annotate(txt, (dt_txts[i], temparatures[i]))
    plt.savefig(graph_dir+'\%s_%s_tempVSdate.png' % (update_dict['city'], update_dict['country']))


# print weather information. 
def check_weather(record):
    for weather in record['weather']:
        # Print alert if rainy or snowy
        if weather['main'] != 'Clear':
            print("Weather: {desc} in {city} at {time} on {day}"
                         .format(desc=weather['description'], city=record['city'],
                                time=modify_time(record.get('dt')), day=record['dt_txt']))

    temp = round(record['main']['temp'])
    # Print alert if temperature is freezing or below freezing
    if  temp <= 0:
        print("ALERT: Freezing temperature at {temp} kelvin in {city}"
                     .format(temp=record['main']['temp'], city=record['city']))

# Fetch five days 3 hrs forecast from the the mongodb and convert to csv from dataframe
def fetch_five_day_forecast():
    df = pd.DataFrame(list(five_day_forecast.find()))
    df.to_csv('five_day_forecast.csv', index = False)

# Fetch five days 3 hrs forecast from the the mongodb and convert to csv from dataframe
def fetch_sixteen_day_forecast():
    df = pd.DataFrame(list(sixteen_day_forecast.find()))
    df.to_csv('five_day_forecast.csv', index = False)

