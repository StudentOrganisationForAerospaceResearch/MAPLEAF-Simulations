#Zachary Gusikoski
#This program reads rocket motor test fire data and creates an openRocket compatible motor file
#save the output file into the thrust curve folder in the directory open rocket runs from
#folder location is likely something like C:\Users\YourName\AppData\Roaming\OpenRocket\ThrustCurves

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

outputFileName = 'ouroboros7SecondBurnMotor.eng' #.eng file
timeStep = 1 #how large the time between used data is

extend = True
extension = 2 #seconds
write = True

#these should all be strings
motorName = 'O5500'
motorDiam = '130' #mm
motorLength = '800' #mm
delays = 'P' #seconds
propWeight = '5.5' #kg
totalWeight = '10' #kg
manufacturer = 'RV'

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

for time in range(motor_start, motor_end+1):
    thrust.append((raw_data['Thrust Load Cell (lbf)'][time]-raw_data['Thrust Load Cell (lbf)'][motor_start])*4.4482216)
    times.append(raw_data['Time (s)'][time] - initial_time)

if write == True:
    output = open(outputFileName, 'w')
    header = '; SOAR openRocket hybrid-type\n; From static fire\n; Created by Zachary Gusikoski\n'
    motorDimension = '%s %s %s %s %s %s %s\n' % (motorName, motorDiam, motorLength, delays, propWeight, totalWeight, manufacturer)

    output.write(header)
    output.write(motorDimension)
    output.write('   0.0001  0.1\n') #openRocket doesn't accept 0 thrust at time 0


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


for i in range(1, len(thrust), timeStep):
    if thrust[i] < 0.10:
        thrust[i] = 0.10

    times[i] = round(times[i], 3)
    thrust[i] = round(thrust[i], 3)

    if times[i] == 0:
        times.pop(i)
        thrust.pop(i)

    if write == True:
        line = '   %s  %s\n' % (times[i], thrust[i])
        output.write(line)


if write == True:
    output.write('   %s  0' % round(times[len(times)-1] + 0.001,3))
    output.write('\n;')
    output.close()