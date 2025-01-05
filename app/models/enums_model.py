from enum import Enum


class GenderEnum(str, Enum):
    FEMALE = "female"
    MALE = "male"
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


class InitialRelationshipEnum(str, Enum):
    CHILD = "child"
    PARENT = "parent"
    PARTNER = "partner"


class HorizontalRelationshipTypeEnum(str, Enum):
    BIOLOGICAL = "biological"
    STEP = "step"
    ADOPTIVE = "adoptive"
    FOSTER = "foster"
    OTHER = "other"


class VerticalRelationshipTypeEnum(str, Enum):
    MARRIAGE = "marriage"
    CIVIL_UNION = "civil union"
    PARTNERSHIP = "partnership"
