import graphviz

dot = graphviz.Digraph(graph_attr={'splines': 'ortho', "overlap": "false", "mode":"ipsep", "sep": "+25", "esep": "+20"}, node_attr={'shape': 'box', 'fixedsize': 'true', 'width': '3.5',
           'height': '3'}, engine = "neato")

format = "plain"


dot.node("extractor")
dot.node("fuel_storage")
dot.node("plant_oil_storage")
dot.node("waste_storage")
dot.node("extractor_water_storage")
dot.node("generator_water_tank")
dot.node("e_to_h_valve")
dot.node("h_to_g_valve")
dot.node("h_to_e_valve")
dot.node("g_to_h_valve")
dot.node("water_cooler")
dot.node("hydroponics_water_cooler")
dot.node("generator_cooler")
dot.node("hydroponics_cooled_water_valve")
dot.node("hydroponics_uncooled_water_valve")
dot.node("plant_press")
dot.node("food_storage")
dot.node("plant_storage")
dot.node("hydroponics_water_storage")
dot.node("oxygen_storage")
dot.node("hydroponics_battery")
dot.node("plant_press_battery")
dot.node("hydroponics")
dot.node("waste_generator")
dot.node("generator")
dot.node("solar_panel")
dot.node("main_science_battery")
dot.node("support_battery")
dot.node("computer")
dot.node("database")
dot.node("lights_med")
dot.node("lights_science")
dot.node("science_scanner")
dot.node("med_scanner")
dot.node("health_scanner")
dot.node("medicine_creator")
dot.node("medicine_storage")
dot.node("rain_water_collector")
dot.node("rain_water_tank")
dot.node("purified_water_tank")
dot.node("dirty_water_storage")
dot.node("water_purifier")
dot.node("toilet_waste_storage")
dot.node("toilets")
dot.edge("extractor", "extractor_water_storage")
dot.edge("extractor", "fuel_storage")
dot.edge("extractor", "plant_oil_storage")
dot.edge("extractor", "waste_storage")
dot.edge("fuel_storage", "extractor")
dot.edge("fuel_storage", "generator")
dot.edge("plant_oil_storage", "medicine_creator")
dot.edge("waste_storage", "waste_generator")
dot.edge("extractor_water_storage", "extractor")
dot.edge("extractor_water_storage", "e_to_h_valve")
dot.edge("generator_water_tank", "generator_cooler")
dot.edge("generator_water_tank", "generator")
dot.edge("generator_water_tank", "waste_generator")
dot.edge("generator_water_tank", "g_to_h_valve")
dot.edge("e_to_h_valve", "hydroponics_water_storage")
dot.edge("h_to_g_valve", "generator_water_tank")
dot.edge("h_to_e_valve", "water_cooler")
dot.edge("g_to_h_valve", "hydroponics_water_storage")
dot.edge("water_cooler", "extractor_water_storage")
dot.edge("hydroponics_water_cooler", "hydroponics")
dot.edge("generator_cooler", "generator_water_tank")
dot.edge("hydroponics_cooled_water_valve", "hydroponics_water_cooler")
dot.edge("hydroponics_uncooled_water_valve", "hydroponics")
dot.edge("plant_press", "food_storage")
dot.edge("plant_press", "generator_water_tank")
dot.edge("plant_storage", "plant_press")
dot.edge("plant_storage", "extractor")
dot.edge("hydroponics_water_storage", "h_to_g_valve")
dot.edge("hydroponics_water_storage", "h_to_e_valve")
dot.edge("hydroponics_water_storage", "hydroponics_cooled_water_valve")
dot.edge("hydroponics_water_storage", "hydroponics_uncooled_water_valve")
dot.edge("oxygen_storage", "water_purifier")
dot.edge("hydroponics_battery", "hydroponics")
dot.edge("plant_press_battery", "plant_press")
dot.edge("hydroponics", "plant_storage")
dot.edge("hydroponics", "oxygen_storage")
dot.edge("hydroponics", "hydroponics_water_storage")
dot.edge("waste_generator", "hydroponics_battery")
dot.edge("waste_generator", "plant_press_battery")
dot.edge("waste_generator", "generator_water_tank")
dot.edge("generator", "hydroponics_battery")
dot.edge("generator", "plant_press_battery")
dot.edge("generator", "generator_water_tank")
dot.edge("solar_panel", "main_science_battery")
dot.edge("main_science_battery", "lights_science")
dot.edge("main_science_battery", "lights_med")
dot.edge("main_science_battery", "computer")
dot.edge("main_science_battery", "med_scanner")
dot.edge("main_science_battery", "science_scanner")
dot.edge("main_science_battery", "medicine_creator")
dot.edge("support_battery", "lights_science")
dot.edge("support_battery", "lights_med")
dot.edge("support_battery", "health_scanner")
dot.edge("support_battery", "medicine_creator")
dot.edge("computer", "database")
dot.edge("database", "med_scanner")
dot.edge("database", "science_scanner")
dot.edge("rain_water_collector", "rain_water_tank")
dot.edge("rain_water_tank", "toilets")
dot.edge("purified_water_tank", "toilets")
dot.edge("purified_water_tank", "medicine_creator")
dot.edge("dirty_water_storage", "water_purifier")
dot.edge("water_purifier", "toilet_waste_storage")
dot.edge("water_purifier", "purified_water_tank")
dot.edge("toilet_waste_storage", "hydroponics")
dot.edge("toilet_waste_storage", "health_scanner")
dot.edge("toilets", "dirty_water_storage")

dot.edge("medicine_creator", "medicine_storage")


dot.edge("waste_generator", "generator", style= "invis")
#dot.edges(['AB', 'AL'])

#dot.edge('B', 'L', constraint='false')
dot = dot.unflatten(stagger=1)
dot = dot.unflatten(stagger=1)
dot = dot.unflatten(stagger=1)
dot = dot.unflatten(stagger=1)


print(dot.render())

print(dot.source)