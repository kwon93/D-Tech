from enum import Enum


class Level(str, Enum):
    ENTRY = "신입"
    JUNIOR = "주니어 (1-3년)"
    MIDDLE = "미들 (3-5년)"
    SENIOR = "시니어 (5년+)"
