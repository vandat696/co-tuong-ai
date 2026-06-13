"""Shared evaluation value types."""

from dataclasses import dataclass


@dataclass
class TaperedScore:
    mg: int = 0
    eg: int = 0

    def add(self, mg, eg):
        self.mg += mg
        self.eg += eg

    def tapered(self, phase):
        phase = max(0, min(16, phase))
        return (self.mg * phase + self.eg * (16 - phase)) // 16
