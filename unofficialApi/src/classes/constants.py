from typing import Final
from dataclasses import dataclass

# Credentials
#NOTE: Es recomendable usar variables de entorno para las credenciales
# en lugar de hardcodearlas en el código
USERNAME: Final[str] = ""
PASSWORD: Final[str] = ""

@dataclass(frozen=True)
class Timeouts:
    """Timeouts configuration in milliseconds"""
    # General timeouts
    WAIT_FOR_ELEMENT: Final[int] = 60_000  # 60 seconds
    
    # Key sending timeouts
    SEND_KEY_MIN: Final[int] = 600
    SEND_KEY_MAX: Final[int] = 2_000
    
    # Sleep timeouts
    SLEEP_MIN: Final[int] = 2_000
    SLEEP_MAX: Final[int] = 6_000
    
    # Tweet fetching timeouts
    FETCH_TWEETS_MIN: Final[int] = 6_000
    FETCH_TWEETS_MAX: Final[int] = 10_000

# Instancia de timeouts para uso global
TIMEOUTS = Timeouts()

# Para importar todo de una manera más limpia:
__all__ = ['USERNAME', 'PASSWORD', 'TIMEOUTS']