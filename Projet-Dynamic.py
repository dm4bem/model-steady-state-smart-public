

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 14:38:11 2024

@author: matth
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dm4bem


np.set_printoptions(precision=1)

# Data
# ====
# dimensions
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

# surfaces
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

# volumes
V_A = L1*c1*H # m³
V_B = L2 * c1 * H # m³
V_C = (L1+L2+w_mur_int) * c2 * H # m³


# thermo-physical propertites
λ_concrete = 1.4             # W/(m K) concrete thermal conductivity
ρ_concrete = 2300            # kg/m³ concrete volumic mass
c_concrete = 880             # J/(kg⋅K) concrete specific heat
λ_insulation = 0.027          # W/(m K) insulation thermal conductivity
ρ_insulation = 55            # kg/m³ insulation volumic mass
c_insulation = 1210             # J/(kg⋅K) insulation specific heat
λ_window = 1.4               # W/(m K) window thermal conductivity
ρ_window = 2500            # kg/m³ window volumic mass
c_window = 1210             # J/(kg⋅K) window specific heat

ρ, c = 1.2, 1000    # kg/m³, J/(kg K) density, specific heat air
hi, ho = 8, 25      # W/(m² K) convection coefficients in, out

# short-wave solar radiation absorbed by each wall
E = 200             # W/m²

# outdoor temperature
To = 20              # °C

# ventilation rate (air-changes per hour)
ACH_ext = 5             # volume/h fenetre à moitié ouverte
ACH_int = 0.5             # volume/h porte/fenetre fermée

VA_dot = V_A * ACH_ext / 3600  # volumetric air flow rate
VB_dot = V_B * ACH_ext / 3600  # volumetric air flow rate
VC_dot = V_C * ACH_ext / 3600  # volumetric air flow rate

mA_dot = ρ * VA_dot               # mass air flow rate
mB_dot = ρ * VB_dot               # mass air flow rate
mC_dot = ρ * VC_dot               # mass air flow rate

mAC_dot = L1 * c1 * H * ACH_int / 3600 * ρ
mBC_dot = L2 * c1 * H * ACH_int / 3600 * ρ



# radiative properties
ε_wLW = 0.85    # long wave emmisivity: wall surface (concrete)
ε_gLW = 0.90    # long wave emmisivity: glass pyrex
α_wSW = 0.25    # short wave absortivity: white smooth surface
α_gSW = 0.38    # short wave absortivity: reflective blue glass
τ_gSW = 0.30    # short wave transmitance: reflective blue glass
σ = 5.67e-8     # W/(m²⋅K⁴) Stefan-Bolzmann constant


nq, nθ = 44, 24  # number of flow-rates branches and of temperaure nodes

# Incidence matrix
# ================
A = np.zeros([nq, nθ])

# q0 ... q5 Convection extérieure
A[0, 3] = 1
A[1, 9] = 1
A[2, 15] = 1
A[3, 7] = 1
A[4, 13] = 1
A[5, 19] = 1

# q6...q9 q11...q14 q16...q19 Conduction murs extérieurs
# mur A
A[6, 4], A[6, 3] = 1, -1
A[7, 4] = -1
A[8, 5] = 1
A[9, 6], A[9, 5] = 1, -1

# mur B
A[11, 9], A[11, 10] = 1, -1
A[12, 10] = 1
A[13, 11] = -1
A[14, 11], A[14, 12] = 1, -1

# mur C
A[16, 16], A[16, 15] = 1, -1
A[17, 16] = -1
A[18, 17] = 1
A[19, 18], A[19, 17] = 1, -1

# q10 q15 q20 Conduction vitres extérieures
A[10, 8], A[10, 7] = 1, -1
A[15, 13], A[15, 14] = 1, -1
A[20, 20], A[20,19] = 1, -1

# q21 q23 q25 Convection murs intérieurs
A[21, 0], A[21, 6] = 1, -1
A[23, 12], A[23, 1] = 1, -1
A[25, 2], A[25,18] = 1, -1

# q22 q24 q26 Convection vitres intérieures
A[22, 0], A[22, 8] = 1, -1
A[24, 14], A[24, 1] = 1, -1
A[26, 2], A[26, 20] = 1, -1

# q27 q28 q29 radiation entre vitres et murs
A[27, 6], A[27, 8] = 1, -1
A[28, 12], A[28, 14] = 1, -1
A[29, 20], A[29, 18] = 1, -1

# q30...q41 Conduction/convection intérieure/intérieure
A[30, 0], A[30, 21] = -1, 1 
A[31, 1], A[31, 21] = 1, -1
A[32, 2], A[32, 22] = -1, 1
A[33, 22], A[33, 1] = -1, 1
A[34, 0], A[34, 23] = -1, 1
A[35, 23], A[35, 2] = -1, 1

# q42 q43 q44 Ventillation extérieure
A[36, 0] = 1
A[37, 1] = 1
A[38, 2] = 1

# q45, q46 Ventillation intérieure
A[39, 1],A[39, 2] = 1,-1
A[40, 2],A[40, 0] = 1,-1

# q47 q48  q49 Régulateur de température
A[41, 0] = 1
A[42, 1] = 1
A[43, 2] = 1


# Conductance matrix
# ==================
G = np.zeros(A.shape[0])

# G0 ... G2 : outdoor convection wall
G[0] = ho * S_A_mur_ext
G[1] = ho * S_B_mur_ext
G[2] = ho * S_C_mur_ext

# G3 ... G5 : outdoor convection glasses
G[3] = ho * S_fenetre
G[4] = ho * S_fenetre
G[5] = ho * S_fenetre*2

# G6...G19 : conduction outdoor wall
# : conduction outdoor wall beton
G[6] = 1 / (w_mur_ext_beton/2 / λ_concrete ) * S_A_mur_ext
G[7] = 1 / (w_mur_ext_beton/2 / λ_concrete ) * S_A_mur_ext
G[11] = 1 / (w_mur_ext_beton/2 / λ_concrete ) * S_B_mur_ext
G[12] = 1 / (w_mur_ext_beton/2 / λ_concrete ) * S_B_mur_ext
G[16] = 1 / (w_mur_ext_beton/2 / λ_concrete ) * S_C_mur_ext
G[17] = 1 / (w_mur_ext_beton/2 / λ_concrete ) * S_C_mur_ext

# : conduction outdoor wall insulation
G[8] = 1 / (w_mur_ext_insulation/2 / λ_insulation ) * S_A_mur_ext
G[9] = 1 / (w_mur_ext_insulation/2 / λ_insulation ) * S_A_mur_ext
G[13] = 1 / (w_mur_ext_insulation/2 / λ_insulation ) * S_B_mur_ext
G[14] = 1 / (w_mur_ext_insulation/2 / λ_insulation ) * S_B_mur_ext
G[18] = 1 / (w_mur_ext_insulation/2 / λ_insulation ) * S_C_mur_ext
G[19] = 1 / (w_mur_ext_insulation/2 / λ_insulation ) * S_C_mur_ext


# G10 G15 G20 : conduction for the window
G[10] = 1 / ( w_vitre / λ_window ) * S_fenetre
G[15] = 1 / ( w_vitre / λ_window ) * S_fenetre
G[20] = 1 / ( w_vitre / λ_window ) * 2*S_fenetre


# G21...G26 : indoor convection
G[21]= hi * S_A_mur_int
G[22]= hi * S_fenetre
G[23]= hi * S_B_mur_int
G[24]= hi * S_fenetre
G[25]= hi * S_C_mur_int
G[26]= hi * 2*S_fenetre

# G27 ... G29 : long wave radiation
Tm = 20 + 273   # K, mean temp for radiative exchange

F_A = S_fenetre / S_A_mur_int
GLW_mur_A = 4 * σ * Tm**3 * ε_wLW / (1 - ε_wLW) * S_A_mur_int
GLW_mur_vitre_A = 4 * σ * Tm**3 * F_A * S_A_mur_int
GLW_vitre_A = 4 * σ * Tm**3 * ε_gLW / (1 - ε_gLW) * S_fenetre
G[27] = 1 / (1 / GLW_mur_A + 1 / GLW_mur_vitre_A + 1 / GLW_vitre_A)

F_B = S_fenetre / S_B_mur_int
GLW_mur_B = 4 * σ * Tm**3 * ε_wLW / (1 - ε_wLW) * S_B_mur_int
GLW_mur_vitre_B = 4 * σ * Tm**3 * F_B * S_B_mur_int
GLW_vitre_B = 4 * σ * Tm**3 * ε_gLW / (1 - ε_gLW) * S_fenetre
G[28] = 1 / (1 / GLW_mur_B + 1 / GLW_mur_vitre_B + 1 / GLW_vitre_B)

F_C = 2*S_fenetre / S_C_mur_int
GLW_mur_C = 4 * σ * Tm**3 * ε_wLW / (1 - ε_wLW) * S_C_mur_int
GLW_mur_vitre_C = 4 * σ * Tm**3 * F_C * S_C_mur_int
GLW_vitre_C = 4 * σ * Tm**3 * ε_gLW / (1 - ε_gLW) * 2*S_fenetre
G[29] = 1 / (1 / GLW_mur_C + 1 / GLW_mur_vitre_C + 1 / GLW_vitre_C)

# G30 ... G41 : internal convection, conduction, internal conduction

#A-B
#convection
G[30] = hi * S_AB + 1 / (w_mur_int / 2*λ_concrete ) * S_AB
G[31] = hi * S_AB + 1 / (w_mur_int / 2*λ_concrete ) * S_AB


#B-C
#convection
G[32] = hi * S_BC + 1 / (w_mur_int / 2*λ_concrete ) * S_BC
G[33] = hi * S_BC + 1 / (w_mur_int / 2*λ_concrete ) * S_BC

#A-C
#convection
G[34] = hi * S_AC + 1 / (w_mur_int / 2*λ_concrete ) * S_AC
G[35] = hi * S_AC + 1 / (w_mur_int / 2*λ_concrete ) * S_AC

# G24 ... G28 : Ventilation
G[36] = mA_dot*c
G[37] = mB_dot*c
G[38] = mC_dot*c
G[40] = mAC_dot*c
G[39] = mBC_dot*c


# Vector of temperature sources
# =============================
b = np.zeros(A.shape[0])
  
b[0:6] = To        # setpoints room A,B & C
b[36:39] = To     # outdoor temperature for ventilation


# Capacity Matrix
# =============================
C = np.zeros(A.shape[1])
# C0 ... C2 : Air
C[0] = ρ*c*V_A
C[1] = ρ*c*V_B
C[2] = ρ*c*V_C
# C4 C10 C16 : Béton
C[4] = ρ_concrete*c_concrete*S_A_mur_ext*c1
C[10] = ρ_concrete*c_concrete*S_B_mur_ext*c1
C[16] = ρ_concrete*c_concrete*S_C_mur_ext*c2
# C5 C11 C17 : Paroi isolante
C[5] = ρ_insulation*c_insulation*S_A_mur_ext*c1
C[11] = ρ_insulation*c_insulation*S_B_mur_ext*c1
C[17] = ρ_insulation*c_insulation*S_C_mur_ext*c2
# C7 C13 C19 : Vitre
C[7] = ρ_window*c_window*S_fenetre*L_vitre
C[13] = ρ_window*c_window*S_fenetre*L_vitre
C[19] = ρ_window*c_window*2*S_fenetre*L_vitre


# Vector of flow-rate sources
# =============================
f = np.zeros(A.shape[1])

#solar radiation _ wall
f[3] = α_wSW*S_A_mur_ext*E
f[9] = α_wSW*S_B_mur_ext*E
f[15] = α_wSW*S_C_mur_ext*E

#solar radaition _ glasses
f[7] = α_gSW*S_fenetre*E
f[13] = α_gSW*S_fenetre*E
f[19] = α_gSW*2*S_fenetre*E


# Indexes of outputs
# ==================
indoor_air = [0,1,2]   # indoor air temperature nodes
controller = range(41,44)  # controller branches


#results in steady state
# ==================
print(f"Maximum value of conductance: {np.max(G):.0f} W/K")

b[controller] = 20, 20, 20  # °C setpoint temperature of the rooms
G[controller] = 0 # Kp-controller gain
  
θ = np.linalg.inv(A.T @ np.diag(G) @ A) @ (A.T @ np.diag(G) @ b  )

q = np.diag(G) @ (-A @ θ + b)

print("To =",To,'°C')
print("All 3 rooms controlled")

print("θ:", θ[indoor_air], "°C")

print("q:", q[controller], "W") 


# state-space representation

y = np.zeros(A.shape[1])        # nodes
y[[0]] = 1
y[[1]] = 1 
y[[2]] = 1               # nodes (temperatures) of interest
pd.DataFrame(y, index=θ)

q_1 = [f'q{i}' for i in range(nq)]
θ_1 = [f'θ{j}' for j in range(nθ)]

A_pd = pd.DataFrame(A, index=q_1, columns=θ_1)
G_pd = pd.Series(G, index=q_1)
C_pd = pd.Series(C, index=θ_1)
b_pd = pd.Series(b, index=q_1)
f_pd = pd.Series(f, index=θ_1)
y_pd = pd.Series(y, index=θ_1)

TC = {"A": A_pd,"G": G_pd,"C": C_pd,"b": b_pd,"f": f_pd,"y": y_pd}

[As, Bs, Cs, Ds, us] = dm4bem.tc2ss(TC)

θ_2=[]
q_2=[]
b_non_nul = []
for i in range(len(b_pd)) :
    if b_pd[i] != 0 :
        θ_2.append(f'θ{i}')
        b_non_nul.append(b_pd[i])

f_non_nul = []
for i in range(len(f_pd)) :
    if f_pd[i] != 0 :
        q_2.append(f'q{i}')
        f_non_nul.append(f_pd[i])


f_non_nul_array = np.array(f_non_nul)
b_non_nul_array = np.array(b_non_nul)

uss = np.hstack([b_non_nul, f_non_nul])           # input vector for state space

liste= θ_2 + q_2
uss_pd = pd.DataFrame(uss, index=(liste))

print(f'uss = {uss_pd}')

inv_As = pd.DataFrame(np.linalg.inv(As), columns=As.index, index=As.index)
yss = (-Cs @ inv_As @ Bs + Ds) @ uss

yss = float(yss.values[0])
print(f'yss = {yss:.2f} °C')


# step response
deltaT = 500    # s, imposed time step
