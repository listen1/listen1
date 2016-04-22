#!/usr/bin/env python
import unittest

TEST_MODULES = [
    'list',
    'your',
    'test',
    'modules',
    'test.test_something',
]

def all():
    try:
        return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)
    except AttributeError as e:
        if "'module' object has no attribute 'test_" in str(e):
            # most likely because of an import error
            for m in TEST_MODULES:
                __import__(m, globals(), locals())
        raise

if __name__ == '__main__':
    import tornado.testing
    tornado.testing.main()
