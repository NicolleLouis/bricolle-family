from django.db import models


class ClanName(models.TextChoices):
    BEAR = "BEAR", "Bear"
    BOAR = "BOAR", "Boar"
    DRAGON = "DRAGON", "Dragon"
    EAGLE = "EAGLE", "Eagle"
    GOAT = "GOAT", "Goat"
    HORSE = "HORSE", "Horse"
    HOUND = "HOUND", "Hound"
    LION = "LION", "Lion"
    LYNX = "LYNX", "Lynx"
    OWL = "OWL", "Owl"
    OX = "OX", "Ox"
    RAT = "RAT", "Rat"
    RAVEN = "RAVEN", "Raven"
    SNAKE = "SNAKE", "Snake"
    SQUIRREL = "SQUIRREL", "Squirrel"
    STAG = "STAG", "Stag"
    STOAT = "STOAT", "Stoat"
    TURTLE = "TURTLE", "Turtle"
    WOLF = "WOLF", "Wolf"
