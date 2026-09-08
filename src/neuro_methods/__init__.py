"""Small, explicit research workflows; catalogued tools are not installed backends."""

__version__ = "0.2.0"

from .catalog import find_methods, get_method, read_card
from .signals import delta_f_over_f, extract_roi_traces, pearson_connectivity
from .workflows import replay, run_config

__all__ = ["find_methods", "get_method", "read_card", "delta_f_over_f",
           "extract_roi_traces", "pearson_connectivity", "run_config", "replay"]
