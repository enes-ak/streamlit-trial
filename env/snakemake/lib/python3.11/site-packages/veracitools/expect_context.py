""" Expectation context management for pytest """

import pytest

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["ExpectContext"]


class ExpectContext(object):
    """ Pytest validation context, a framework for varied kinds of expectations. """

    def __init__(self, expected, test_func):
        """
        Create the test context by specifying expectation and function.

        :param object | type expected: expected result or exception
        :param callable test_func: the callable object to test
        """
        self._f = test_func
        self._exp = expected

    def __enter__(self):
        """ Return the instance for use as a callable. """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, *args, **kwargs):
        """ Execute the instance's function, passing given args/kwargs. """
        if isinstance(self._exp, type) and issubclass(self._exp, Exception):
            with pytest.raises(self._exp):
                self._f(*args, **kwargs)
        else:
            assert self._exp == self._f(*args, **kwargs)

