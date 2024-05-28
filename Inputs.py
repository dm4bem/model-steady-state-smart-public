import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import dm4bem

# Inputs
# =========================================================================

start_date = '02-01 12:00:00'
end_date = '02-07 18:00:00'

start_date = '2020-' + start_date
end_date = '2020-' + end_date

print(f'{start_date} \tstart date')
print(f'{end_date} \tend date')

# Weather data
filename = 'weather_data/FRA_AR_Villard.de.Lans.074840_TMYx.2007-2021.epw'
[data, meta] = dm4bem.read_epw(filename, coerce_year=None)
weather = data[["temp_air", "dir_n_rad", "dif_h_rad"]]
del data

# Select weather data from date_start to date_end
weather.index = weather.index.map(lambda t: t.replace(year=2020))
weather = weather.loc[start_date:end_date]

# Temperature sources
# Outdoor air temperature
To = weather['temp_air']

# Indoor air temperature set-point
Ti_day, Ti_night = 20, 16
Ti_sp = pd.Series(20, index=To.index)
Ti_sp = pd.Series(
    [Ti_day if 6 <= hour <= 22 else Ti_night for hour in To.index.hour],
    index=To.index)

# Flow rate sources
# Total solar irradiance
W_mur_ext = 0.30   # m

surface_orientation = {'slope': w0['β'].values[0],
                       'azimuth': w0['γ'].values[0],
                       'latitude': 45}

rad_surf = dm4bem.sol_rad_tilt_surf(
    weather, surface_orientation, w0['albedo'].values[0]) 

Etot = rad_surf.sum(axis=1)

# Window glass properties
α_gSW = 0.38    # short wave absortivity: reflective blue glass
τ_gSW = 0.30    # short wave transmitance: reflective blue glass
S_g = 9         # m², surface area of glass

# Solar radiation absorbed by the outdoor surface of the wall
Φo = w0['α1'].values[0] * w0['Area'].values[0] * Etot

# Solar radiation absorbed by the indoor surface of the wall
Φi = τ_gSW * w0['α0'].values[0] * S_g * Etot

# Solar radiation absorbed by the glass
Φa = α_gSW * S_g * Etot

# Auxiliary (internal) sources
Qa = 0 * np.ones(weather.shape[0])

# Input data set
input_data_set = pd.DataFrame({'To': To, 'Ti_sp': Ti_sp,
                               'Φo': Φo, 'Φi': Φi, 'Qa': Qa, 'Φa': Φa,
                               'Etot': Etot})

input_data_set.to_csv('./toy_model/input_data_set.csv')
print(input_data_set)
