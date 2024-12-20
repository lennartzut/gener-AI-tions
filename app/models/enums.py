from enum import Enum


class GenderEnum(str, Enum):
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


class LegalRelationshipEnum(str, Enum):
    MARRIAGE = "marriage"
    CIVIL_UNION = "civil union"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class FamilyRelationshipEnum(str, Enum):
    PARENT = "parent"
    CHILD = "child"
    PARTNER = "partner"
