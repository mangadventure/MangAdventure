"""
`Path converters`_ used in URL patterns.

.. _`Path converters`:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/#path-converters
"""


class FloatConverter:
    """Path converter that matches a float number."""
    #: The pattern to match.
    regex = r'\d+(\.\d+)?'

    def to_python(self, value: str) -> float:
        """
        Convert the matched string into the type
        that should be passed to the view function.

        :param value: The matched string.

        :return: The match as a ``float``.
        """
        return float(value)

    def to_url(self, value: str) -> str:
        """
        Convert the Python type into a string to be used in the URL.

        :param value: The matched string.

        :return: The match with trailing zeroes removed.
        """
        return f'{float(value):g}'


__all__ = ['FloatConverter']
