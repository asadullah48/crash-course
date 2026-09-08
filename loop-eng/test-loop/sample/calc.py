"""A small, deliberately buggy module for the test-loop project.

Three functions, three seeded bugs. The tests in test_calc.py catch all
three. Nothing here is meant to stay broken -- fix it until the checker
says pass.
"""


def add(a, b):
    return a + b


def average(nums):
    return sum(nums) / len(nums)


def clamp(value, low, high):
    """Push value into [low, high]."""
    if value < low:
        return low
    if value > high:
        return high
    return value
