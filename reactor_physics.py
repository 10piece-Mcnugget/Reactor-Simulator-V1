import json

class Reactor:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            config = json.load(f)

        self.max_power = config["max_power_mw"]
        self.rod_step = config["rod_step_pct"]
        self.coolant_step = config["coolant_step_pct"]
        self.max_safe_reactivity = config["max_safe_reactivity"]
        self.name = config["reactor_name"]
        self.reference_temp = config["reference_temp_c"]
        self.boiling_temp = config["boiling_temp_c"]
        self.rod_position = config["initial_state"]["rod_position_pct"]
        self.coolant_flow = config["initial_state"]["coolant_flow_pct"]
        self.coolant_temp = config["initial_state"]["coolant_temp_c"]
        self.power = config["initial_state"]["power_mw"]

        self.coefficients = config["coefficients"]
        self.enabled_effects = config["enabled_effects"]

        self.reactivity = 0
        self.void_fraction = 0

    def tick(self, dt):
        if self.coolant_temp > self.boiling_temp:
            self.void_fraction = (self.coolant_temp - self.boiling_temp) * self.coefficients["void_growth_rate"]
        else:
            self.void_fraction = 0

        self.reactivity = (100- self.rod_position) * self.coefficients["rod_worth"]

        if self.enabled_effects["temperature_feedback"]:
            self.reactivity = self.reactivity + self.coefficients["temperature_feedback"]*(self.coolant_temp - self.reference_temp)
        if self.enabled_effects["void_feedback"]:
            self.reactivity = self.reactivity + self.coefficients["void_feedback"] * self.void_fraction

        self.power = self.power * (1 + self.reactivity * self.coefficients["power_gain"]*dt)
        self.power = min(self.power, self.max_power)
        self.power = max(self.power, 0)
        self.coolant_temp = self.coolant_temp + (self.coefficients["heat_generation"] * self.power - self.coefficients["coolant_heat_removal"]*self.coolant_flow * (self.coolant_temp - self.reference_temp))*dt
       
    def insert_rods(self):
        self.rod_position = min(self.rod_position + self.rod_step, 100)

    def withdraw_rods(self):
        self.rod_position = max(self.rod_position - self.rod_step, 0)

    def scram(self):
        self.rod_position = 100
        self.reactivity = 0
        # decay heat is not modeled yet, power will not isntantly drop in real life
        self.power = 0
    
    def increase_coolant(self):
        self.coolant_flow = min(self.coolant_flow + self.coolant_step, 100)
    
    def decrease_coolant(self):
        self.coolant_flow = max(self.coolant_flow - self.coolant_step, 0)


reactor = Reactor("reactor_config.json")

for i in range(20):
    reactor.tick(1)
    print(reactor.power, reactor.coolant_temp, reactor.reactivity, reactor.void_fraction)