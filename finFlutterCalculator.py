import math

#inputs
#Use metric

root = 0.36
tip = 0.110
span = 0.125
thickness = 0.01
shearModulus = 4891784.65609
heightAtMaxVelocity = 1000


optimize = True

lowerLim = 480
upperLim = 500

iterations = 1000
#if no iteration put 0 for iteration factor, there should be one factor for each parameter
iterationFactors = [0, 0.001, 0, 0, 0, 0]

root *= 39.37
tip *= 39.37
span *= 39.37
thickness *= 39.37
shearModulus /= 6.895
heightAtMaxVelocity *= 3.281

def calculateFlutterSpeed(root, tip, span, thickness, shearModulus, heightAtMaxVelocity):
    s = 0.5*span*(root+tip)
    aspectRatio = (span**2)/s
    lamb = tip/root
    temp = 59-(0.00356*heightAtMaxVelocity)
    pressure = 2116*(((temp+459.7)/518.6)**5.256)/144
    a = (1.4*1716.59*(temp+460))**0.5

    bottomTop = (1.337*(aspectRatio**3)*pressure*(lamb+1)) 
    botomBottom = (2*(aspectRatio+2)*((thickness/root)**3))
    bottom = bottomTop/botomBottom

    flutterSpeed = a*((shearModulus/bottom)**0.5)

    flutterSpeedMetric = flutterSpeed/3.281
    return flutterSpeedMetric



#optimize
if optimize == True:
    parametersToIterate = [root, tip, span, thickness, shearModulus, heightAtMaxVelocity]
    '''
    for i in range(iterations):
        
        for i in range(6):
            parametersToIterate[i] += iterationFactors[i]
        
        print(parametersToIterate[0], parametersToIterate[1], parametersToIterate[2], parametersToIterate[3], parametersToIterate[4], parametersToIterate[5], calculate(parametersToIterate[0], parametersToIterate[1], parametersToIterate[2], parametersToIterate[3], parametersToIterate[4], parametersToIterate[5]))
    '''
    for i in range(6):

        for j in range(iterations):
            parametersToIterate[i] += iterationFactors[i]
            result = calculateFlutterSpeed(parametersToIterate[0], parametersToIterate[1], parametersToIterate[2], parametersToIterate[3], parametersToIterate[4], parametersToIterate[5])
            if lowerLim < result < upperLim:
                break

    print(parametersToIterate[0]/39.37, parametersToIterate[1]/39.37, parametersToIterate[2]/39.37, parametersToIterate[3]/39.37, parametersToIterate[4]*6.895, parametersToIterate[5]/3.281, calculateFlutterSpeed(parametersToIterate[0], parametersToIterate[1], parametersToIterate[2], parametersToIterate[3], parametersToIterate[4], parametersToIterate[5]))

else:
    print("Flutter speed: ", round(calculateFlutterSpeed(root, tip, span, thickness, shearModulus, heightAtMaxVelocity), 2), "m/s")