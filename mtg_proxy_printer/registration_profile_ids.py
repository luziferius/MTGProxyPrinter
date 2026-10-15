"""Stable registration identities shared by settings, documents and presentation."""

import enum


@enum.unique
class RegistrationProfileId(enum.Enum):
    NONE = "None"
    BULLSEYE = "Bullseye"
    SILHOUETTE = "Cut marker"
    SISER = "Siser"
