# authentication/const.py
from django.db import models

# Keep your gender if you use it elsewhere
MALE = 'm'
FEMALE = 'f'
OTHER = 'o'

GENDER = {MALE: 'Male', FEMALE: 'Female', OTHER: 'Other'}

# Roles by NAME, not ID
ADMIN = "Admin"
DOCTOR = "Doctor"
PATIENT = "Patient"

ROLE_NAMES = [ADMIN, DOCTOR, PATIENT]


class Gender(models.TextChoices):
    MEN = 'M', 'Men'
    WOMEN = 'W', 'Women'
