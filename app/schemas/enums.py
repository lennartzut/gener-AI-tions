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


class RelationshipTypeEnumRelationship(str, Enum):
    MARRIAGE = "marriage"
    CIVIL_UNION = "civil_union"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class RelationshipType(str, Enum):
    PARENT = "parent"
    GUARDIAN = "guardian"
    CHILD = "child"
