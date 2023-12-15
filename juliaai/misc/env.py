from __future__ import annotations

from typing import Optional
from juliaai.utility import AbstractUtilityClass

from dataclasses import dataclass

from os import path, environ
from dotenv import load_dotenv
if not path.exists('.env'):
    raise FileNotFoundError("You haven't created the .env file, please create it immediately for the correct operation; 1")
load_dotenv('.env')


@dataclass
class ENV(AbstractUtilityClass):
    TOKEN: str = environ.get('TOKEN')
    