"""Daily synchronized startup ritual for both peer cores."""
from dataclasses import dataclass
from datetime import date
from typing import Callable

RAM_INVOCATION = "श्री राम जय राम जय जय राम"
HANUMAN_INVOCATION = "ॐ हनुमते नमः"
MANTRA = "ॐ गं गणपतये नमः"
TRANSLITERATION = "Om Gam Ganapataye Namah"

@dataclass(frozen=True)
class StartupEvent:
    day: str
    core: str
    step: str
    message: str

SEQUENCE = (
    "system_health_check",
    "owner_authority_check",
    "recite_shri_ram",
    "recite_hanuman",
    "recite_ganesha_mantra",
    "core_sync",
    "daily_briefing",
)

def run_daily_start(core: str, checks: dict[str, Callable[[], bool]]) -> list[StartupEvent]:
    if core not in {"bharath_vyomaraj", "laxman_jarvis"}:
        raise ValueError("unknown peer core")
    events = []
    today = date.today().isoformat()
    for step in SEQUENCE:
        if step == "recite_shri_ram":
            message = RAM_INVOCATION
        elif step == "recite_hanuman":
            message = HANUMAN_INVOCATION
        elif step == "recite_ganesha_mantra":
            message = f"{MANTRA} ({TRANSLITERATION})"
        elif step == "core_sync":
            message = "peer synchronization requested"
        elif step == "daily_briefing":
            message = "daily briefing requested"
        else:
            check = checks.get(step)
            if check is None or not check():
                raise RuntimeError(f"startup blocked at {step}")
            message = "passed"
        events.append(StartupEvent(today, core, step, message))
    return events
