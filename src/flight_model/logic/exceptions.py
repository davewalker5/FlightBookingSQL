"""
This module defines custom exceptions used by the flight model business logic
"""


class InvalidOperationError(Exception):
    pass


class MissingBoardingCardPluginError(Exception):
    def __init__(self, message, card_format=None):
        super().__init__(message)
        self._card_format = card_format

    @property
    def card_format(self):
        return self._card_format

    def __str__(self):
        return f"'{self.args[0]}' for card format '{self._card_format}'"

    def __repr__(self):
        return f"MissingBoardingCardPluginError({self.args[0]!r}, {self._card_format!r})"
