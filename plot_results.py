# Take geotiff from results

import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rio
from geopy.geocoders import Nominatim
from rasterio.windows import Window
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.font_manager import FontProperties
from datetime import datetime

# Load the font file
# font_path = '/usr/share/fonts/opentype/CharterBT-Roman.otf'
# charter_font = FontProperties(fname=font_path)

# Convert latitude and longitude to pixel coordinates
def latlon_to_pixel(dataset, lat, lon):
    transform = dataset.transform
    col, row = ~transform * (lon, lat)
    return int(row), int(col)

# Function to get coordinates for a city
def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="era5_downloader")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Could not find coordinates for city: {city_name}")


def save_plots(aurora_data, era5_data, variable, city_name, file_date, date_str, extent):
    axis_font = {'size':'18', 'fontname':'DejaVu Serif'}
    title_font = {'size':'18', 'fontname':'DejaVu Serif', 'color':'black', 'weight':'normal', 'verticalalignment':'bottom'}

    # Determine the common colorbar extent
    vmin = min(aurora_data.min(), era5_data.min())
    vmax = max(aurora_data.max(), era5_data.max())

    # Plot Aurora data
    fig, axs = plt.subplots(1, 1, figsize=(10, 10))
    aurora_plot = axs.imshow(aurora_data, vmin=vmin, vmax=vmax, extent=extent, origin='upper', cmap='plasma')
    axs.set_title(f'{variable} Aurora Prediction {date_str}', **title_font)
    axs.set_xlabel('Longitude', **axis_font)
    axs.set_ylabel('Latitude', **axis_font)
    axs.tick_params(axis='both', labelsize=14)
    divider = make_axes_locatable(axs)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    colorbar = fig.colorbar(aurora_plot, cax=cax)
    colorbar.ax.tick_params(labelsize=14)

    ticks = np.arange(np.ceil(vmin / 10) * 10, vmax, 10)  # Create a set of ticks between vmin and vmax
    colorbar.set_ticks(ticks)  # Set the ticks for the colorbar
    
    # Add °C for temperature variable without changing tick positions
    if 'Temp' in variable:
        colorbar.ax.set_yticklabels([f'{tick:.1f}°C' for tick in ticks])  # Add °C to each tick label

    plt.tight_layout()
    plt.savefig(f'plots/{city_name}_aurora_{file_date}_{variable}.png')


    # Plot ERA5 data
    fig, axs = plt.subplots(1, 1, figsize=(10, 10))
    aurora_plot = axs.imshow(era5_data, vmin=vmin, vmax=vmax, extent=extent, origin='upper', cmap='plasma')
    axs.set_title(f'{variable} HRES Model {date_str}', **title_font)
    axs.set_xlabel('Longitude', **axis_font)
    axs.set_ylabel('Latitude', **axis_font)
    axs.tick_params(axis='both', labelsize=14)
    divider = make_axes_locatable(axs)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    colorbar = fig.colorbar(aurora_plot, cax=cax)
    colorbar.ax.tick_params(labelsize=14)

    ticks = np.arange(np.ceil(vmin / 10) * 10, vmax, 10)  # Create a set of ticks between vmin and vmax
    colorbar.set_ticks(ticks)  # Set the ticks for the colorbar
    
    # Add °C for temperature variable without changing tick positions
    if 'Temp' in variable:
        colorbar.ax.set_yticklabels([f'{tick:.1f}°C' for tick in ticks])  # Add °C to each tick label

    plt.tight_layout()
    plt.savefig(f'plots/{city_name}_hres_{file_date}_{variable}.png')

    # Plot the difference
    diff = era5_data - aurora_data
    vmin = diff.min()
    vmax = diff.max()

    fig, axs = plt.subplots(1, 1, figsize=(10, 10))
    plot = axs.imshow(diff, vmax=vmax, vmin=vmin, extent=extent, origin='upper', cmap='plasma')
    axs.set_title(f'{variable} Error {date_str}', **title_font)
    axs.set_xlabel('Longitude', **axis_font)
    axs.set_ylabel('Latitude', **axis_font)
    axs.tick_params(axis='both', labelsize=14)
    divider = make_axes_locatable(axs)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    colorbar = fig.colorbar(plot, cax=cax)
    colorbar.ax.tick_params(labelsize=14)
    
    ticks = np.linspace(vmin, vmax, 6)  # Create a set of ticks between vmin and vmax
    colorbar.set_ticks(ticks)  # Set the ticks for the colorbar
    
    # Add °C for temperature variable without changing tick positions
    if 'Temp' in variable:
        colorbar.ax.set_yticklabels([f'{tick:.1f}°C' for tick in ticks])  # Add °C to each tick label

    plt.tight_layout()
    plt.savefig(f'plots/{city_name}_error_{file_date}_{variable}.png')


city_name = 'Delhi'

latitude, longitude = get_coordinates(city_name)

print(f"Latitude: {latitude}, Longitude: {longitude}")

# Define the bounding box around the city (adjust as needed)
# Ensure the width (longitude range) is a multiple of 4
lon_min = longitude -  17
lon_max = longitude + 23
lat_min = latitude - 25
lat_max = latitude + 15

print(f"Latitude range: {lat_min} to {lat_max}")
print(f"Longitude range: {lon_min} to {lon_max}")

# Load the geotiff file
# Change the path to the file you want to plot

date_str = '11_06_22_12'

# Convert to datetime format
date_obj = datetime.strptime(date_str, '%d_%m_%y_%H')

# Format to desired output
formatted_date = date_obj.strftime('%dth %B %Y %I:%M %p')


file_aurora = f'results/aurora_{date_str}.tif'
file_era5 = f'results/hres_{date_str}.tif'

# Open the file:
aurora = rio.open(file_aurora)
era5 = rio.open(file_era5)

# Read all the data and save it in a numpy array
aurora_data = aurora.read()
era5_data = era5.read()

# Get the metadata of the file
aurora_meta = aurora.meta
era5_meta = era5.meta

# Get the pixel coordinates for the bounding box
aurora_row_max, aurora_col_min = latlon_to_pixel(aurora, lat_min, lon_min)
aurora_row_min, aurora_col_max = latlon_to_pixel(aurora, lat_max, lon_max)

era5_row_max, era5_col_min = latlon_to_pixel(era5, lat_min, lon_min)
era5_row_min, era5_col_max = latlon_to_pixel(era5, lat_max, lon_max)

extent = [lon_min, lon_max, lat_min, lat_max]

print(f"Aurora: Rows: {aurora_row_min} to {aurora_row_max}, Cols: {aurora_col_min} to {aurora_col_max}")
print(f"ERA5: Rows: {era5_row_min} to {era5_row_max}, Cols: {era5_col_min} to {era5_col_max}")

# Extract the region from the datasets
aurora_region = aurora.read(window=Window(aurora_col_min, aurora_row_min, aurora_col_max - aurora_col_min, aurora_row_max - aurora_row_min))
era5_region = era5.read(window=Window(era5_col_min, era5_row_min, era5_col_max - era5_col_min, era5_row_max - era5_row_min))

#plot temperature
save_plots(aurora_region[0, :, :], era5_region[0, :, :], 'Temperature (2m)', city_name, date_str, formatted_date, extent)



# #Calculate the wind speed and direction using the u and v components
# wind_speed_era5 = np.sqrt(era5_region[1, :, :]**2 + era5_region[2, :, :]**2)
# wind_dir_era5 = (180. + 180./np.pi * np.arctan2(era5_region[1, :, :], era5_region[2, :, :]))%180

# wind_speed_aurora = np.sqrt(aurora_region[1, :, :]**2 + aurora_region[2, :, :]**2)
# wind_dir_aurora = (180. + 180./np.pi * np.arctan2(aurora_region[1, :, :], aurora_region[2, :, :]))%180


# #Plot the wind speed and direction
# fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# # Determine the common colorbar extent
# vmin = min(wind_speed_aurora.min(), wind_speed_era5.min())
# vmax = max(wind_speed_aurora.max(), wind_speed_era5.max())

# print(vmin, vmax)

# # Plot the wind speed
# wind_speed_aurora_plot = axs[0].imshow(wind_speed_aurora, vmin=vmin, vmax=vmax)
# axs[0].set_title('Wind Speed Aurora')
# fig.colorbar(wind_speed_aurora_plot, ax=axs[0])

# wind_speed_era5_plot = axs[1].imshow(wind_speed_era5, vmin=vmin, vmax=vmax)
# axs[1].set_title('Wind Speed ERA5')
# fig.colorbar(wind_speed_era5_plot, ax=axs[1])

# #The difference in wind speed
# diff_speed = wind_speed_era5 - wind_speed_aurora
# diff_speed_plot = axs[2].imshow(diff_speed)
# axs[2].set_title('Difference Wind Speed')
# fig.colorbar(diff_speed_plot, ax=axs[2])

# plt.show()


# # Extract u and v components for quiver plot
# u_aurora = aurora_region[2, :, :]
# v_aurora = aurora_region[1, :, :]
# u_era5 = era5_region[2, :, :]
# v_era5 = era5_region[1, :, :]

# # Get the affine transformation from the dataset
# transform = aurora.transform

# # Create arrays for the x and y coordinates
# cols, rows = np.meshgrid(
#     np.arange(u_aurora.shape[1]), 
#     np.arange(u_aurora.shape[0])
# )
# x_coords, y_coords = rio.transform.xy(transform, rows, cols, offset='center')

# # Convert to numpy arrays for plotting
# x_coords = np.array(x_coords)
# y_coords = np.array(y_coords)

# # Plot wind speed and direction as quiver plots with real-world coordinates
# fig, axs = plt.subplots(1, 2, figsize=(15, 5))

# # Aurora wind vectors
# axs[0].quiver(x_coords, y_coords, u_aurora, v_aurora, color="blue")
# axs[0].set_title('Wind Vectors Aurora')
# axs[0].set_xlabel('Longitude')
# axs[0].set_ylabel('Latitude')

# # ERA5 wind vectors
# axs[1].quiver(x_coords, y_coords, u_era5, v_era5, color="red")
# axs[1].set_title('Wind Vectors ERA5')
# axs[1].set_xlabel('Longitude')
# axs[1].set_ylabel('Latitude')

# plt.tight_layout()
# plt.show()

# #Polt wind direction as a quiver plot
# fig, axs = plt.subplots(1, 2, figsize=(15, 5))

# # Plot the wind direction make sure you provide correct values for the x and y components
# axs[0].quiver(np.arange(wind_dir_aurora.shape[1]), np.arange(wind_dir_aurora.shape[0]), wind_dir_aurora, wind_speed_aurora, scale=1)
# axs[0].set_title('Wind Direction Aurora')

# axs[1].quiver(np.arange(wind_dir_era5.shape[1]), np.arange(wind_dir_era5.shape[0]), wind_dir_era5, wind_speed_era5, scale=1)
# axs[1].set_title('Wind Direction ERA5')

# plt.show()

# # Plot the data
# fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# # Determine the common colorbar extent
# vmin = min(aurora_data[i, :, :].min(), era5_data[i, :, :].min())
# vmax = max(aurora_data[i, :, :].max(), era5_data[i, :, :].max())

# print(vmin, vmax)

# # Plot the aurora data
# aurora_plot = axs[0].imshow(aurora_data[i, :, :], vmin=vmin, vmax=vmax)
# axs[0].set_title('Aurora Variables')
# fig.colorbar(aurora_plot, ax=axs[0])

# # Plot the era5 data
# era5_plot = axs[1].imshow(era5_data[i, :, :], vmin=vmin, vmax=vmax)
# axs[1].set_title('ERA5 Variables')
# fig.colorbar(era5_plot, ax=axs[1])

# #Plot difference
# diff = era5_data[i, :, :] - aurora_data[i, :, :]
# diff_plot = axs[2].imshow(diff)
# axs[2].set_title('Difference')
# fig.colorbar(diff_plot, ax=axs[2])


# plt.show()