""" Test module for flystim.screen
"""

import unittest

import hypothesis
from hypothesis import given, strategies

from flystim.screen import Screen


class TestScreen(unittest.TestCase):
    """ Test class for Screen
    """

    @given(
        width=strategies.floats(min_value=0.01),
        height=strategies.floats(min_value=0.01),
        azimuth=strategies.floats(min_value=0, max_value=360),
        offset=strategies.lists(
            strategies.floats(allow_nan=False, allow_infinity=False),
            min_size=3,
            max_size=3
        )
    )
    def test_deserialize_inverts_serialize(self, width, height, azimuth, offset):
        """  Test that deserialize(serialize(s)) = s
        """
        screen = Screen(
            width=width,
            height=height,
            azimuth=azimuth,
            offset=offset
        )

        serialized = screen.serialize()

        reconstructed_screen = Screen.deserialize(serialized)

        self.assertEqual(screen, reconstructed_screen)
