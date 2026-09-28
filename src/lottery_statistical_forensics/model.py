from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class NullModel:
    game: str
    main_count: int
    main_min: int
    main_max: int

    @property
    def population_size(self) -> int:
        return self.main_max - self.main_min + 1

    def draw(self, rng: Any) -> list[int]:
        return sorted((rng.choice(self.population_size,size=self.main_count,replace=False)+self.main_min).tolist())
