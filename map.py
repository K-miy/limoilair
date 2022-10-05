#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import numpy as np
import pandas as pd
import folium
import branca
from folium import plugins
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import geojsoncontour
import scipy as sp
import scipy.ndimage

dir_path = os.path.dirname(os.path.realpath(__file__))

# Setup
temp_mean = 12
temp_std  = 2
debug     = False

# Setup colormap
colors = ['#d7191c',  '#fdae61',  '#ffffbf',  '#abdda4',  '#2b83ba']
vmin   = temp_mean - 2 * temp_std
vmax   = temp_mean + 2 * temp_std
levels = len(colors)
cm     = branca.colormap.LinearColormap(colors, vmin=vmin, vmax=vmax).to_step(levels)

# Create a dataframe with fake data
df = pd.DataFrame({
    'latitude':    np.random.normal(46.82,     0.03,     1000),
    'longitude':   np.random.normal(-71.22,     0.04,     1000),
    'PM2.5': np.random.normal(temp_mean, temp_std, 1000)})

# The original data
x_orig = np.asarray(df.longitude.tolist())
y_orig = np.asarray(df.latitude.tolist())
z_orig = np.asarray(df['PM2.5'].tolist())

# Make a grid
x_arr          = np.linspace(np.min(x_orig), np.max(x_orig), 500)
y_arr          = np.linspace(np.min(y_orig), np.max(y_orig), 500)
x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)

# Grid the values
z_mesh = griddata((x_orig, y_orig), z_orig, (x_mesh, y_mesh), method='linear')

# Gaussian filter the grid to make it smoother
sigma = [5, 5]
z_mesh = sp.ndimage.filters.gaussian_filter(z_mesh, sigma, mode='constant')

# Create the contour
contourf = plt.contourf(x_mesh, y_mesh, z_mesh, levels, alpha=0.5, colors=colors, linestyles='None', vmin=vmin, vmax=vmax)

# Convert matplotlib contourf to geojson
geojson = geojsoncontour.contourf_to_geojson(
    contourf=contourf,
    min_angle_deg=3.0,
    ndigits=5,
    stroke_width=1,
    fill_opacity=0.5)

# Set up the folium plot
geomap = folium.Map([df.latitude.mean(), df.longitude.mean()], zoom_start=10, tiles="cartodbpositron")

# Plot the contour plot on folium
folium.GeoJson(
    geojson,
    style_function=lambda x: {
        'color':     x['properties']['stroke'],
        'weight':    x['properties']['stroke-width'],
        'fillColor': x['properties']['fill'],
        'opacity':   0.6,
    }).add_to(geomap)

# Add the colormap to the folium map
cm.caption = 'PM2.5'
geomap.add_child(cm)

# Fullscreen mode
plugins.Fullscreen(position='topright', force_separate_button=True).add_to(geomap)


# Plot the data
with open(dir_path+'/folium_contour_temperature_map.html','wb') as f:
    geomap.save(f)
    
    
    
def plotHeatMap(df):
    print("=== Plotting data")
    # Prepare Map
    # Remove nulls
    df = df[df.latitude.notnull()]
    df = df[df.longitude.notnull()]
    df = df[df.roomGrossPrice.notnull()]
    # remove outliers
    q_hi = df["roomGrossPrice"].quantile(0.99)
    df = df[(df["roomGrossPrice"] < q_hi)]

    x_start = (df['latitude'].max() + df['latitude'].min()) / 2
    y_start = (df['longitude'].max() + df['longitude'].min()) / 2
    start_coord = (x_start, y_start)
    # Setup colormap
    colors = ['#147d05', '#1ead0a', '#ffff17', '#f28e2c', '#b30003']

    vmin = df["roomGrossPrice"].min()
    vmax = df["roomGrossPrice"].max()
    levels = len(colors)
    cm = branca.colormap.LinearColormap(colors, vmin=vmin, vmax=vmax).to_step(levels)
    map = folium.Map(location=start_coord, zoom_start=14)

    addContourf(map, df, colors, vmin, vmax)

    for index, item in df.iterrows():
        loc = tuple([item["latitude"], item["longitude"]])
        folium.Circle(
            location=loc,
            radius=5,
            fill=True,
            popup="RoomPrice:<br/>" + str(item["roomGrossPrice"]) + "<br/>Rooms:<br/>" + str(item["rooms"]) + "<br/>ID:<br/>" + str(item["id"]),
            color=cm(item["roomGrossPrice"]),
            # fill_opacity=0.7
        ).add_to(map)

    cm.caption = 'Room Price'
    map.add_child(cm)
    folium.LayerControl().add_to(map)
    map.save('test.html')
    print("=== Plotting data finished")
    

def addContourf(map, df, colors, vmin, vmax):
    print("=== adding Contourf")
    # The original data
    x_orig = np.asarray(df.longitude.tolist())
    y_orig = np.asarray(df.latitude.tolist())
    z_orig = np.asarray(df['roomGrossPrice'].tolist())
    # Make a grid
    x_arr = np.linspace(np.min(x_orig), np.max(x_orig), 500)
    y_arr = np.linspace(np.min(y_orig), np.max(y_orig), 500)
    x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)
    # Grid the values
    z_mesh = griddata((x_orig, y_orig), z_orig, (x_mesh, y_mesh), method='linear')

    # Gaussian filter the grid to make it smoother
    sigma = [4, 4]
    z_mesh = ndimage.filters.gaussian_filter(z_mesh, sigma, mode='constant')

    # Create the contour
    contourf = plt.contourf(x_mesh, y_mesh, z_mesh, len(colors), alpha=0.5, colors=colors, linestyles='None', vmin=vmin, vmax=vmax)
    # Convert matplotlib contourf to geojson
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=5,
        stroke_width=1,
        fill_opacity=0.5)
    # Plot the contour plot on folium
    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            'color': x['properties']['stroke'],
            'weight': x['properties']['stroke-width'],
            'fillColor': x['properties']['fill'],
            'opacity': 0.6,
        }).add_to(map)
    print("=== adding Contourf finished")