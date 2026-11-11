"""Аэрогусь «Готурбо» — реализация публичного интерфейса из SPEC.md."""


class CrazyVehicleError(Exception):
    """Базовое исключение безумных транспортных средств."""


class TurboGooseError(CrazyVehicleError):
    """Базовое доменное исключение аэрогуся."""


class GooseNoEnergy(TurboGooseError):
    """Запаса зерновой энергии недостаточно для перелёта."""


class GooseCannotTravelThere(TurboGooseError):
    """Аэрогусь не может перемещаться в указанной среде."""


class TurboGoose:
    """Одноместный летающий гусь с зерновым источником энергии.

    Все публичные атрибуты доступны только для чтения; состояние изменяется
    исключительно методами ``move``, ``refuel`` и ``land``.
    """

    def __init__(
        self,
        name: str,
        mass_kg: float,
        wing_span_m: float,
        max_speed_kmh: float,
        energy: float = 100.0,
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name.strip():
            raise ValueError("name must not be empty")
        if mass_kg <= 0:
            raise ValueError("mass_kg must be positive")
        if wing_span_m <= 0:
            raise ValueError("wing_span_m must be positive")
        if max_speed_kmh <= 0:
            raise ValueError("max_speed_kmh must be positive")
        if not 0 <= energy <= 100:
            raise ValueError("energy must be between 0 and 100")

        self._name = name
        self._mass_kg = mass_kg
        self._wing_span_m = wing_span_m
        self._max_speed_kmh = max_speed_kmh
        self._energy = energy
        self._position_km = 0.0
        self._is_flying = False

    @property
    def name(self) -> str:
        """Имя аэрогуся."""
        return self._name

    @property
    def mass_kg(self) -> float:
        """Масса, кг."""
        return self._mass_kg

    @property
    def wing_span_m(self) -> float:
        """Размах крыльев, м."""
        return self._wing_span_m

    @property
    def max_speed_kmh(self) -> float:
        """Максимальная скорость полёта, км/ч."""
        return self._max_speed_kmh

    @property
    def energy(self) -> float:
        """Оставшийся запас зерновой энергии."""
        return self._energy

    @property
    def position_km(self) -> float:
        """Суммарная пройденная дистанция, км."""
        return self._position_km

    @property
    def is_flying(self) -> bool:
        """Находится ли аэрогусь в полёте."""
        return self._is_flying

    @staticmethod
    def _validate_trip(distance_km: float, medium: str) -> None:
        """Проверяет аргументы в порядке, заданном контрактом."""
        if distance_km <= 0:
            raise ValueError("distance_km must be positive")
        if medium != "air":
            raise GooseCannotTravelThere("Готурбо умеет летать, а не ползать.")

    def move(self, distance_km: float, medium: str = "air") -> float:
        """Летит указанную дистанцию и возвращает время перелёта в часах."""
        self._validate_trip(distance_km, medium)
        required_energy = distance_km * 2
        if required_energy > self._energy:
            raise GooseNoEnergy("Готурбо вымотался: сначала покорми гуся!")

        self._position_km += distance_km
        self._energy -= required_energy
        self._is_flying = True
        return distance_km / self._max_speed_kmh

    def can_overcome(self, obstacle: str) -> bool:
        """Определяет возможность преодоления препятствия без изменения состояния."""
        if obstacle == "building":
            return self._is_flying and self._energy >= 10
        if obstacle == "storm":
            return self._wing_span_m > 1.5 and self._energy >= 25
        if obstacle == "power_line":
            return False
        raise ValueError("unknown obstacle")

    def calculate_energy(self, distance_km: float, medium: str = "air") -> float:
        """Возвращает расчётный расход энергии без изменения состояния."""
        self._validate_trip(distance_km, medium)
        return distance_km * 2

    def refuel(self, amount: float) -> None:
        """Пополняет запас зерновой энергии максимум до 100 единиц."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._energy = min(100.0, self._energy + amount)

    def land(self) -> None:
        """Переводит гуся в состояние покоя, не изменяя энергию и дистанцию."""
        self._is_flying = False

    def get_status(self) -> dict:
        """Возвращает независимый снимок публичного состояния."""
        return {
            "name": self._name,
            "energy": self._energy,
            "position_km": self._position_km,
            "is_flying": self._is_flying,
            "wing_span_m": self._wing_span_m,
        }
