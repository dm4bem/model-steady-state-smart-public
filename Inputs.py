import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import dm4bem

# Data building
# =========================================================================
# Dimensions
L1, L2, c1, c2 = 4, 6, 3, 4  # m
H = 3        # m
H_vitre = 1   # m
L_vitre = 1  # m
W_mur_ext = 0.30   # m
w_mur_ext_beton = 0.20   # m
w_mur_ext_insulation = 0.1 # m
w_mur_int = 0.3 # m
w_vitre = 0.02 # m

# Pièce B prend en compte w_int !!!!

# Surfaces
S_A_mur_ext = (L1+(c1-L_vitre))*H + L_vitre*(H-H_vitre) + W_mur_ext*2*H
S_A_mur_int = S_A_mur_ext - W_mur_ext*2*H
S_B_mur_ext = ((L2-L_vitre)+c1+2*W_mur_ext+w_mur_int)*H + L_vitre*(H-H_vitre)
S_B_mur_int = (S_B_mur_ext - 2*W_mur_ext+w_mur_int)*H
S_C_mur_ext = (L1+L2+w_mur_int-2*L_vitre+2*c2+4*W_mur_ext)*H + 2*L_vitre*(H-H_vitre)
S_C_mur_int = S_C_mur_ext - 4*W_mur_ext*H
S_fenetre = H_vitre*L_vitre
S_AB = c1*H
S_AC = L1*H
S_BC = L2*H

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
surface_orientation = {'slope': 90,    # 90° is vertical, 90° downward
                       'azimuth': 0,    # 0° South, positive westward
                       'latitude': 45}    # °, North Pole 90° positive

albedo = 0.2
rad_surf = dm4bem.sol_rad_tilt_surf(
    weather, surface_orientation, albedo) 

Etot = rad_surf.sum(axis=1)

# Window glass properties
α_gSW = 0.38    # short wave absortivity: reflective blue glass
τ_gSW = 0.30    # short wave transmitance: reflective blue glass
S_g = 9         # m², surface area of glass

# Outdoor wall properties
α0_wSW = 0.25    # short wave absortivity: indoor white smooth surface
α1_wSW = 0.30    # short wave absortivity: outdoor concrete wall

# Solar radiation absorbed by the outdoor surface of the wall
Φo = α1_wSW * (S_A_mur_ext + S_B_mur_ext +S_C_mur_ext) * Etot

# Solar radiation absorbed by the indoor surface of the wall
Φi = τ_gSW * α0_wSW * S_fenetre * Etot

# Solar radiation absorbed by the glass
Φa = α_gSW * S_fenetre * Etot

# Auxiliary (internal) sources
Qa = 0 * np.ones(weather.shape[0])

# Input data set
input_data_set = pd.DataFrame({'To': To, 'Ti_sp': Ti_sp,
                               'Φo': Φo, 'Φi': Φi, 'Qa': Qa, 'Φa': Φa,
                               'Etot': Etot})

print(input_data_set)


print("To =",To[0])
