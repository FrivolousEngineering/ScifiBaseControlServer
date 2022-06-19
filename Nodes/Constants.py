
# How much joule does it take to increase the temperature by 1 kelvin of 1 kg of material?
SPECIFIC_HEAT = {"energy": 0,
                 "fuel": 2220,
                 "water": 4190,
                 "oxygen": 919,
                 "data": 0,
                 "dirty_water": 3905,
                 "waste": 800,  # Based on dry soil
                 "animal_waste": 1000,  # A bit different from dry soil
                 "plants": 1480,  # Based on wet soil
                 "plant_oil": 1970,  # Based on Olive oil
                 "food": 2489,  # Specific heat of bread
                 "medicine": 0.3
                 }

GAS_PHASE_CHANGE_TEMPERATURE = {
    "water": 373.15
}

GAS_PHASE_SPECIFIC_HEAT = {
    "water": 2262600
}


# 1 liter of this unit is how much kg?
WEIGHT_PER_UNIT = {"water": 1,
                   "fuel": 0.7,
                   "energy": 0,
                   "oxygen": 0.001429,
                   "data": 0,
                   "dirty_water": 1.1,
                   "waste": 1.2,
                   "animal_waste": 1.2,
                   "plants": 0.408,
                   "plant_oil": 0.92,
                   "food": 0.874,
                   "medicine": 0.9
                   }


COMBUSTION_HEAT = {"water": 0,
                   "fuel": 42000000,  # Based on Diesel
                   "energy": 10000000,  # Not entiiiirely combustion heat. But hey. The energy balancer uses this.
                   "oxygen": 0,
                   "data": 0,
                   "dirty_water": 0,
                   "waste": 16000000,  # Based on wood
                   "animal_waste": 16000000,
                   "medicine": 0
                   }

SECONDS_PER_TICK = 60