import pandas as pd

#reading in data
file_name = 'Ouroboros Mass Budget - Ouroboros Mass Budget.csv'

rawData = pd.read_csv(file_name, sep=',', dtype=str)

mapleafFile = '''
# Zachary Gusikoski
# Ouroboros I
#MAPLEAF
# See SimDefinitionTemplate.mapleaf for file format info & description of all options
SimControl{
    timeDiscretization RK45Adaptive
    timeStep 0.01 #sec

    EndCondition Apogee
	#EndConditionValue	300

    loggingLevel    2
    RocketPlot      On

    plot    FlightAnimation CP CG AOA Aero Position Velocity Mach
	}
Environment{
    ConstantMeanWind{
        velocity                    ( 3 0 0 ) #m/s
    }
	LaunchSite{
        elevation               0 #m, Relative to sea level - Impacts the acceleration of gravity at launch        

        # Lat / Lon only influence simulations using the 'Round' or 'WGS84' earth models
        #latitude                49 # Degrees, 90 = North Pole, -90 = South Pole, 0 = Equator
        #longitude               81 # Degrees, 0 = Prime Meridian (Greenwich, England), +'ve is East, -'ve is West

        # A launch rail will prevent the rocket from deviating from the direction specified by Rocket.initialDirection
            # Until it has travelled the length of the launch rail from its starting location
            # The launch rail will also prevent downwards motion
            # A length of 0 = no launch rail
        railLength              13.716 #m

		EarthModel                  Flat

    	#### Atmospheric Properties ####
    	# USStandardAtmosphere or Constant or TabulatedAtmosphere
        # USStandardAtmosphere computes the exact US Standard Atmosphere
    	AtmosphericPropertiesModel  USStandardAtmosphere
    }

	TurbulenceModel             PinkNoise3D
    # turbulenceOffWhenUnderChute True # Increases time step we can take while descending

    PinkNoiseModel{
        # To set the strength of pink noise fluctuations, provide the turbulenceIntensity OR the velocityStdDeviation
            # If both are provided, the turbulenceIntensity is used
        turbulenceIntensity     5 # % velocity standard deviation / mean wind velocity
        velocityStdDeviation    1 # m/s standard deviation of pink noise model

        # Set the random seeds for each pink noise generator for repeatable simulations
            # PinkNoise1D only uses 1, 2D uses 2, 3D uses all 3
        randomSeed1             63583 # Integer
        randomSeed2             63583 # Integer
        randomSeed3             63583 # Integer
    }

	MeanWindModel               SampledRadioSondeData

	SampledRadioSondeData{
        launchMonth             Mar # Three letter month code - uses yearly avg data if absent
        # Place1 name, weighting coefficient 1, Place2 name, weighting coefficient 2, ... - Corresponding radio sonde data files must be in MAPLEAF/Examples/Wind
        locationsToSample       Edmonton 0.48 Glasgow 0.52 
        locationASLAltitudes    710 638 # m ASL - Used to convert ASL altitude data provided in radio sonde files to AGL altitudes
        randomSeed              228010 # Set to remove randomization from sampling, have a repeatable simulation
    }
	}

Rocket{
	name				Ouroboros
	#initialDirection	(0 0 1)
	rotationAxis        (0 0 1) # Any Vector, defined in launch tower ENU frame
    rotationAngle       6 # degrees
	position            (0 0 1.73) # m - initial position above ground level (AGL) of the rocket's CG. Set launch site elevation using Environment.LaunchSite.elevation
    velocity            (0 0 0) # m/s - initial velocity
    angularVelocity     (0 0 0) # rad/s - initial angular velocity - defined in the rocket's LOCAL frame

	Aero{
        # To turn off base drag (for comparisons to wind tunnel data), make sure the rocket doesn't include a Boat tail and set this to false
        addZeroLengthBoatTailsToAccountForBaseDrag      true
      
        # Calculates skin friction based on laminar + transitional flow if not fully turbulent
        fullyTurbulentBL                                true
    }

    FirstStage{
        class           Stage
		stageNumber		1
		position            (0 0 0) #m - Position of stage tip, relative to tip of rocket

'''

#getting header
header = rawData.head(0)

#finding useful data
indices = []
i = 0
while i < rawData['class'].size:
    if (rawData['class'][i] != 'nan') and (type(rawData['class'][i]) != float):
        indices.append(i)
    i += 1

for index in indices:
    componentData = []
    if rawData['class'][index] == 'Nosecone':
        componentName = rawData['Part'][index]
        componentData.append(componentName)
        componentClass = ['class',rawData['class'][index]]
        componentData.append(componentClass)
        mass = ['mass',rawData['Mass Allotted (kg)'][index]]
        componentData.append(mass)
        outerDiam = ['baseDiameter',rawData['outerDiameter'][index]]
        componentData.append(outerDiam)
        position = ['position','(%s %s %s)' % (rawData['Tip Position x (m)'][index], rawData['Tip Position y (m)'][index], rawData['Tip Position z (m)'][index])]
        componentData.append(position)
        cg = "(%s %s %s)" % (rawData['CGx (m)'][index],rawData['CGy (m)'][index],rawData['CGz (m)'][index])
        cg = ['cg',cg]
        componentData.append(cg)
        aspectRatio = ['aspectRatio',float(rawData['length'][index])/float(rawData['outerDiameter'][index])]
        componentData.append(aspectRatio)
        shape = ['shape','tangentOgive']
        componentData.append(shape)
        surfaceRoughness = ['surfaceRoughness',rawData['surfaceRoughness'][index]]
        componentData.append(surfaceRoughness)

    elif rawData['class'][index] == 'RecoverySystem':
        componentName = rawData['Part'][index]
        componentData.append(componentName)
        componentClass = ['class',rawData['class'][index]]
        componentData.append(componentClass)
        mass = ['mass',rawData['Mass Allotted (kg)'][index]]
        componentData.append(mass)
        position = ['position','(%s %s %s)' % (rawData['Tip Position x (m)'][index], rawData['Tip Position y (m)'][index], rawData['Tip Position z (m)'][index])]
        componentData.append(position)
        cg = "(%s %s %s)" % (rawData['CGx (m)'][index],rawData['CGy (m)'][index],rawData['CGz (m)'][index])
        cg = ['cg',cg]
        componentData.append(cg)
        numstages = ['numstages','1']
        componentData.append(numstages)
        stage1Trigger = ['stage1Trigger','Apogee']
        componentData.append(stage1Trigger)
        stage1TriggerValue = ['stage1TriggerValue','30']
        componentData.append(stage1TriggerValue)
        stage1ChuteArea = ['stage1ChuteArea','2']
        componentData.append(stage1ChuteArea)
        stage1Cd = ['stage1Cd', '1.5']
        componentData.append(stage1Cd)
        stage1DelayTime = ['stage1DelayTime','2']
        componentData.append(stage1DelayTime)

    elif rawData['class'][index] == 'Bodytube':
        componentName = rawData['Part'][index]
        componentData.append(componentName)
        componentClass = ['class','bodytube']
        componentData.append(componentClass)
        mass = ['mass',rawData['Mass Allotted (kg)'][index]]
        componentData.append(mass)
        outerDiam = ['baseDiameter',rawData['outerDiameter'][index]]
        componentData.append(outerDiam)
        position = ['position','(%s %s %s)' % (rawData['Tip Position x (m)'][index], rawData['Tip Position y (m)'][index], rawData['Tip Position z (m)'][index])]
        componentData.append(position)
        cg = "(%s %s %s)" % (rawData['CGx (m)'][index],rawData['CGy (m)'][index],rawData['CGz (m)'][index])
        cg = ['cg',cg]
        componentData.append(cg)
        surfaceRoughness = ['surfaceRoughness',rawData['surfaceRoughness'][index]]
        componentData.append(surfaceRoughness)
        length = ['length', rawData['length'][index]]
        componentData.append(length)
    
    elif rawData['class'][index] == 'Mass':
        componentName = rawData['Part'][index]
        componentData.append(componentName)
        componentClass = ['class',rawData['class'][index]]
        componentData.append(componentClass)
        mass = ['mass',rawData['Mass Allotted (kg)'][index]]
        componentData.append(mass)
        position = ['position','(%s %s %s)' % (rawData['Tip Position x (m)'][index], rawData['Tip Position y (m)'][index], rawData['Tip Position z (m)'][index])]
        componentData.append(position)
        cg = "(%s %s %s)" % (rawData['CGx (m)'][index],rawData['CGy (m)'][index],rawData['CGz (m)'][index])
        cg = ['cg',cg]
        componentData.append(cg)
        moi = ['MOI','(%s %s %s)' % (rawData['MOIx (kg m^2)'][index],rawData['MOIy (kg m^2)'][index],rawData['MOIz (kg m^2)'][index])]
        componentData.append(moi)

    elif rawData['class'][index] == 'FinSet':
        componentName = rawData['Part'][index]
        componentData.append(componentName)
        componentClass = ['class',rawData['class'][index]]
        componentData.append(componentClass)
        mass = ['mass',rawData['Mass Allotted (kg)'][index]]
        componentData.append(mass)
        position = ['position','(%s %s %s)' % (rawData['Tip Position x (m)'][index], rawData['Tip Position y (m)'][index], rawData['Tip Position z (m)'][index])]
        componentData.append(position)
        cg = "(%s %s %s)" % (rawData['CGx (m)'][index],rawData['CGy (m)'][index],rawData['CGz (m)'][index])
        cg = ['cg',cg]
        componentData.append(cg)

        numFins = ['numfins','3']
        componentData.append(numFins)
        finCantAngle = ['finCantAngle','0']
        componentData.append(finCantAngle)
        firstFinAngle = ['firstFinAngle','0']
        componentData.append(firstFinAngle)
        sweepAngle = ['sweepAngle','28']
        componentData.append(sweepAngle)
        rootChord = ['rootChord','0.381']
        componentData.append(rootChord)
        tipChord = ['tipChord','0.178']
        componentData.append(tipChord)
        span = ['span','0.1862']
        componentData.append(span)
        thickness  = ['thickness','0.009906']
        componentData.append(thickness)
        surfaceRoughness = ['surfaceRoughness',rawData['surfaceRoughness'][index]]
        componentData.append(surfaceRoughness)
    
    elif rawData['class'][index] == 'Transition':
        componentName = rawData['Part'][index]
        componentData.append(componentName)
        componentClass = ['class',rawData['class'][index]]
        componentData.append(componentClass)
        mass = ['mass',rawData['Mass Allotted (kg)'][index]]
        componentData.append(mass)
        position = ['position','(%s %s %s)' % (rawData['Tip Position x (m)'][index], rawData['Tip Position y (m)'][index], rawData['Tip Position z (m)'][index])]
        componentData.append(position)
        cg = "(%s %s %s)" % (rawData['CGx (m)'][index],rawData['CGy (m)'][index],rawData['CGz (m)'][index])
        cg = ['cg',cg]
        componentData.append(cg)
        moi = ['MOI','(%s %s %s)' % (rawData['MOIx (kg m^2)'][index],rawData['MOIy (kg m^2)'][index],rawData['MOIz (kg m^2)'][index])]
        componentData.append(moi)
        length = ['length', rawData['length'][index]]
        componentData.append(length)
        startDiam = ['startDiameter',rawData['startDiameter'][index]]
        componentData.append(startDiam)
        endDiam = ['startDiameter',rawData['endDiameter'][index]]
        componentData.append(endDiam)
        surfaceRoughness = ['surfaceRoughness',rawData['surfaceRoughness'][index]]
        componentData.append(surfaceRoughness)
    
    elif rawData['class'][index] == 'BoatTail':
        componentName = rawData['Part'][index]
        componentData.append(componentName)
        componentClass = ['class',rawData['class'][index]]
        componentData.append(componentClass)
        mass = ['mass',rawData['Mass Allotted (kg)'][index]]
        componentData.append(mass)
        position = ['position','(%s %s %s)' % (rawData['Tip Position x (m)'][index], rawData['Tip Position y (m)'][index], rawData['Tip Position z (m)'][index])]
        componentData.append(position)
        cg = "(%s %s %s)" % (rawData['CGx (m)'][index],rawData['CGy (m)'][index],rawData['CGz (m)'][index])
        cg = ['cg',cg]
        componentData.append(cg)
        moi = ['MOI','(%s %s %s)' % (rawData['MOIx (kg m^2)'][index],rawData['MOIy (kg m^2)'][index],rawData['MOIz (kg m^2)'][index])]
        componentData.append(moi)
        length = ['length', rawData['length'][index]]
        componentData.append(length)
        startDiam = ['startDiameter',rawData['startDiameter'][index]]
        componentData.append(startDiam)
        endDiam = ['startDiameter',rawData['endDiameter'][index]]
        componentData.append(endDiam)
        surfaceRoughness = ['surfaceRoughness',rawData['surfaceRoughness'][index]]
        componentData.append(surfaceRoughness)

    else:
        break

    part = componentData[0]
    part = part.replace(" ","")
    partString = "\n%s{\n" % (part)
    mapleafFile = mapleafFile + partString
    for component in range(1,len(componentData)):
        partData = "\t%s\t\t\t%s\n" % (componentData[component][0], componentData[component][1])
        mapleafFile = mapleafFile + partData

    if componentData[1][1] == 'FinSet':
        mapleafFile = mapleafFile + '''
    LeadingEdge{
        shape         Round # Blunt or Round (Even sharp edges always have a small radius)
        #thickness     0.00931 # Used for 'Blunt' edge
        radius        0.00211 # Used for 'Round' edge
    }

    TrailingEdge{
        shape         Round # Tapered (0 base drag), Round (1/2 base drag), Blunt (full base drag)
        #thickness     0.001 # Used for 'Blunt' edge
        radius        0.00211 # Used for 'Round' edge
    }
'''

    mapleafFile = mapleafFile + '\t}\n'

mapleafFile = mapleafFile + r'''
Motor{
        class           Motor
        path            C:\Users\zackg\Documents\Coding\MAPLEAF-master\MAPLEAF\Examples\Motors\Ouroboros_5SecBurn.txt
    }
'''
mapleafFile = mapleafFile + '\n\t}\n}'

print(mapleafFile)
program_datafile = open('testmapleaffile.mapleaf', 'w')
program_datafile.write(mapleafFile)
program_datafile.close()