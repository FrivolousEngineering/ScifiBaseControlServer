
# The specific heat is just a ratio. It is loosly based on real values (hence fuel being 0.5 and water being 1).
SPECIFIC_HEAT = {"energy": 0,
                 "fuel": 0.5,
                 "water": 1,
                 "oxygen": 0.25,
                 "data": 0,
                 "dirty_water": 1,
                 "waste": 1,
                 "animal_waste": 1,
                 "plants": 0.39,
                 "plant_oil": 0.5,
                 "food": 0.6,
                 "medicine": 0.3
                 }

GAS_PHASE_CHANGE_TEMPERATURE = {
    "water": 373.15
}

GAS_PHASE_SPECIFIC_HEAT = {
    "water": 540
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
                   "fuel": 7500,
                   "energy": 0,
                   "oxygen": 0,
                   "data": 0,
                   "dirty_water": 0,
                   "waste": 3000,
                   "animal_waste": 3000,
                   "medicine": 0
                   }

SECONDS_PER_TICK = 60