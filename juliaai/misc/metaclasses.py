from __future__ import annotations

import configparser
from dataclasses import dataclass
from typing import Optional, Any
from os import path

def read_config() -> configparser.ConfigParser | None:
    if not path.exists('etc/juliaai.properties'):
        print('`etc/juliaai.properties` configuration file not found.')
        return None
    
    cnf_ = configparser.ConfigParser()
    cnf_.read('etc/juliaai.properties')
    return cnf_

class MetaConfig(type):
    def __new__(cls, name: str = None, 
                bases: tuple[type, ...] = None,
                namespace: dict[str, Any] = None) -> None:
        settings: dict = read_config()
        if settings:
            for section, options in settings.items():
                for key, value in options.items():
                    namespace[key] = value
        return super().__new__(cls, name, bases, namespace)

@dataclass
class MetaSettings(metaclass=MetaConfig):
    agent_name: Optional[str]

    bot_activity: Optional[str]
    bot_activity_type: Optional[str]

    command_prefix: Optional[str]

    loss: Optional[str]
    input_length: Optional[int]
    optimizer: Optional[str]    
    output_dim: Optional[int]
    batch_size: Optional[int]
    epochs: Optional[int]
    units: Optional[int]
    rate: Optional[float]
    