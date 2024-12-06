"""
Defines enumerations for various attributes like gender, relationship types, and roles.
"""

from enum import Enum


class GenderEnum(str, Enum):
    """
    Enumerates various gender identities.
    """
    MALE = "male"
    FEMALE = "female"
    TRANSGENDER = "transgender"
    GENDER_NEUTRAL = "gender neutral"
    NON_BINARY = "non binary"
    AGENDER = "agender"
    PANGENDER = "pangender"
    GENDERQUEER = "genderqueer"
    TWO_SPIRIT = "two spirit"
    THIRD_GENDER = "third gender"
    OTHER = "other"
    UNKNOWN = "unknown"


class RelationshipTypeEnum(str, Enum):
    """
    Enumerates legal or recognized relationship types between partners.
    """
    MARRIAGE = "marriage"
    CIVIL_UNION = "civil union"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class RelationshipType(str, Enum):
    """
    Enumerates types of family relationships.
    """
    PARENT = "parent"
    GUARDIAN = "guardian"
    CHILD = "child"
    SIBLING = "sibling"
