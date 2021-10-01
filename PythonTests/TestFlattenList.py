# Created/tested using python3.9 interpreter
import unittest


# Method to flatten nested array of integers
def flatten(nestedarray):
    if len(nestedarray) == 0:
        return nestedarray
    # Checking for sub arrays in the list
    # if 1st element not a sublist, append and check next element recursively
    if not isinstance(nestedarray[0], list):
        return nestedarray[:1] + flatten(nestedarray[1:])
    # if 1st element is a sublist, flatten, append and check next element recursively
    return flatten(nestedarray[0]) + flatten(nestedarray[1:])


# Unit test for flatten method
class TestFlattenedArray(unittest.TestCase):
    # Nested Array of Integers Unit Test
    def test_flattenTest(self):
        nestedarray = [[1, 2, [3]], 4]
        flattenedarray = [1, 2, 3, 4]
        self.assertEqual(flatten(nestedarray), flattenedarray)


if __name__ == '__main__':
    unittest.main()
