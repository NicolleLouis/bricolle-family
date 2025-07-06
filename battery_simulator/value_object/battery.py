from dataclasses import dataclass


@dataclass
class Battery:
    COST_PER_KWH = 115 # €/kWh
    CYCLE_LIFESPAN = 3000

    nominal_capacity: int # kWh
    state_of_charge: float = 0 # kWh


    def remaining_energy(self) -> float:
        if self.state_of_charge > self.nominal_capacity:
            raise ValueError("More energy stored than possible")

        return self.nominal_capacity - self.state_of_charge
