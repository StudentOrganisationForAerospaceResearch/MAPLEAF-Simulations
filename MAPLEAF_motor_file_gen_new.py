#Zachary Gusikoski
#This program reads rocket motor test fire data and creates a mapleaf compatible motor file

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random

outputFileName = 'Motor.txt' #.txt file with the name you want to call the motor file

extend = True
write = True
extension = 2 #seconds
estimation = True
estimationAvgThrust = 5594.2 #from NASA CEA + Reynolds transport theorem or other calculations
oxidizer_flowrate = 2.4 #Hardcoded because the data is being weird. Likely because of the time difference
OFRatio = 7.65
fuelBurnRate = oxidizer_flowrate / OFRatio

def getMOIsSolidCylinder(mass, length, radius):
    MOIxy = (0.25*mass*(radius**2)) + ((1/12)*mass*(length**2))
    MOIz = 0.5*mass*(radius**2)
    return [MOIxy, MOIxy, MOIz]

def getMOIsHollowCylinder(mass, length, innerRadius, outerRadius):
    MOIxy = (mass/12)*((3*((innerRadius**2)+(outerRadius**2)))+(length**2))
    MOIz = (mass/2)*((innerRadius**2)+(outerRadius**2))
    return [MOIxy, MOIxy, MOIz]

diamOfPressureVessel = 0.142875
lengthOfPressureVessel = 1.07188

lenghtOfFuelGrain = 0.290576
outerDiamFuelGrain = 0.15
innerDiamFuelGrain = 0.05715

radiusOfPressureVessel = 0
radiusOfPressureVessel = diamOfPressureVessel / 2

fuelGrainOuterRadius = 0
fuelGrainOuterRadius = outerDiamFuelGrain / 2
fuelGrainInnerRadius = 0
fuelGrainInnerRadius = innerDiamFuelGrain / 2

file_name = 'StaticFireData.txt'

raw_data = pd.read_csv(file_name,  sep=',', index_col=False)

i = 0 
motor_start = 0
j = 0
motor_end = 0
while i < raw_data.size:
    if raw_data['Chamber Pressure (PSI)'][i] >= 15:
        motor_start = i
        break

    i += 1

while j < raw_data.size:
    if (raw_data['Comment'][j] == 'Standby') and (j > motor_start) and (j > 0):
        motor_end = j
        break

    j += 1

print('Fire begins at line', motor_start+2, 'Fire ends at line', motor_end+2)

initial_time = raw_data['Time (s)'][motor_start]


times = []
thrust = []
oxMOI = []
fuelMOI = []
chamberPressure = []

#oxidizer_flowrate = abs((raw_data['Ox Tank Load Cell (kg)'][motor_start] - raw_data['Ox Tank Load Cell (kg)'][motor_end]) / (raw_data['Time (s)'][motor_end] - initial_time))

totalOxMass = abs(raw_data['Ox Tank Load Cell (kg)'][motor_start] - raw_data['Ox Tank Load Cell (kg)'][motor_end])

totalFuelMass = 0
#totalFuelMass = fuelBurnRate*(raw_data['Time (s)'][motor_end]-initial_time)
totalFuelMass = 1.5095 #Hardcoded because the data is being weird

for time in range(motor_start, motor_end+1):
    times.append(raw_data['Time (s)'][time] - initial_time)
    chamberPressure.append(raw_data['Chamber Pressure (PSI)'][time])
    thrust.append((raw_data['Thrust Load Cell (lbf)'][time]-raw_data['Thrust Load Cell (lbf)'][motor_start])*4.4482216)
    oxMOI.append(getMOIsSolidCylinder(totalOxMass - (oxidizer_flowrate*(raw_data['Time (s)'][time]-initial_time)), lengthOfPressureVessel, radiusOfPressureVessel))
    fuelMOI.append(getMOIsHollowCylinder(totalFuelMass - (fuelBurnRate*(raw_data['Time (s)'][time]-initial_time)), lenghtOfFuelGrain, fuelGrainInnerRadius, fuelGrainOuterRadius))

#plt.plot(times, chamberPressure)
#plt.show()
header = '''# Motor Definition File: 2019_Definition_Draft

# Amount of white space between each value is not important, there just needs to be some
# Thrust curve will be linearly interpolated between the given values
# Time(s) should be relative to motor ignition      #2,2.5,3,3

# Unburned fuel/oxidizer not currently accounted for, could be added in as a fixed mass?
# Engine/Tank structure mass should be accounted for separately - the motor only accounts for propellant masses
# MOI = Moment of Inertia
    # It is assumed that oxidizer and fuel MOIs are always defined about the current CG of the oxidizer and fuel, respectively
# To represent a solid rocket motor, simply put all of the MOI/CG/Flowrate info in either the fuel or oxidizer columns and set the other one to zero

# Meters, all Z-coordinate, assumed centered
BurnedOxidizerInitialCG     -2.6
BurnedOxidizerLastCG        -3.1
BurnedFuelInitialCG         -3.75
BurnedFuelLastCG            -3.75

#Time(s)   Thrust(N)   OxidizerFlowRate(kg/s)  FuelBurnRate(kg/s) OxMOI(kg*m^2) FuelMOI(kg*m^2) 
'''
extendoThrust = []
extendoTimes = []
timestep = times[2] - times[1]
stabilityCounter = 0
averageThrust = sum(thrust)/len(thrust)
maxThrust = max(thrust)

if extend == True:
    for i in range(len(thrust)-1):
        if ((thrust[i] - thrust[i+1]) < 1) and ((averageThrust+100) < thrust[i] < (maxThrust-500)):
            extendoThrust.append(thrust[i])
            stabilityCounter += 1

        
        if stabilityCounter >= 1000:
            print("Stability reached")
            break


    halfLengthIndex = int(len(thrust)//2)

    for h in range(extension*1000):
        extendoTimes.append((h/1000) + times[halfLengthIndex])

    for a in range(halfLengthIndex, len(times)):
        times[a] += extension


    extendoThrustlLen = len(extendoThrust)
    averageExtendoThrust = sum(extendoThrust)/len(extendoThrust)
    for y in range((extension*1000)-len(extendoThrust)):
        extendoThrust.append(extendoThrust[y])

    halfLengthIndex = int(len(thrust)//2)
    for l in range(len(extendoThrust)):
        thrust.insert(halfLengthIndex, extendoThrust[-l])

    for l in range(len(extendoTimes)):
        times.insert(halfLengthIndex, extendoTimes[-l])

    times[halfLengthIndex - 1 + (extension*1000)] += extension
    times.pop(halfLengthIndex + (extension*1000))
    thrust.pop(halfLengthIndex + (extension*1000))

    plt.plot(times, thrust)
    plt.plot(extendoTimes, extendoThrust)
    plt.show()

    oxMOI2 = []
    fuelMOI2 = []


if estimation == True:
    averageThrustEstimate = sum(thrust)/len(thrust)
    for t in thrust:
        n = t/averageThrustEstimate
        thrust[thrust.index(t)] = n*estimationAvgThrust
    
    plt.plot(times, thrust)
    plt.show()



    if write == True:
        output = open(outputFileName, 'w')
        output.write(header)
        for i in range(len(thrust)):
            

            oxMOI2.append(getMOIsSolidCylinder(totalOxMass - (oxidizer_flowrate*times[i]), lengthOfPressureVessel, radiusOfPressureVessel))
            fuelMOI2.append(getMOIsHollowCylinder(totalFuelMass - (fuelBurnRate*times[i]), lenghtOfFuelGrain, fuelGrainInnerRadius, fuelGrainOuterRadius))

            line = '%s\t%s\t%s\t%s\t(%s %s %s)\t(%s %s %s)\n' % (times[i], thrust[i], oxidizer_flowrate, fuelBurnRate, oxMOI2[i][0], oxMOI2[i][1], oxMOI2[i][2], fuelMOI2[i][0], fuelMOI2[i][1], fuelMOI2[i][2])
            output.write(line)
        output.close()

else:
    plt.plot(times, thrust)
    plt.show()

    if write == True:
        output = open(outputFileName, 'w')
        output.write(header)
        for i in range(0, (motor_end-motor_start)+1):
            line = '%s\t%s\t%s\t%s\t(%s %s %s)\t(%s %s %s)\n' % (times[i], thrust[i], oxidizer_flowrate, fuelBurnRate, oxMOI[i][0], oxMOI[i][1], oxMOI[i][2], fuelMOI[i][0], fuelMOI[i][1], fuelMOI[i][2])
            output.write(line)
        output.close()