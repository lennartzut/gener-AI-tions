from enum import Enum


class RelationshipTypeEnum(Enum):
    MARRIAGE = "marriage"
    CIVIL_UNION = "civil_union"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class GenderEnum(Enum):
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


class RelationshipType(Enum):
    PARENT = "parent"
    GUARDIAN = "guardian"
    CHILD = "child"
