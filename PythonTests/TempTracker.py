### Created/tested using python3.9 interpreter
#  
#  Creating a simple temperature tracker program where users can enter temperature (in Fahrenheit as integers) 
#  And get the Max, Min, Median value of temperatures
#
###
import unittest


# Class for keeping track of recorded temperatures
class TemperatureTracker(object):
    # initialize constructor
    def __init__(self):
        self.templist = []

    # temperature insert method
    # Required parm: temperature int or list of int
    # Optional parm: list of already recorded temperature where new temperatures will be appended.
    def insert(self, temperatures, *args):
        self.templist = [temp for temp in args]
        # If optional parm is coming is as a list, flatten list
        if any(isinstance(temp, list) for temp in self.templist):
            # call method to flatten nested list
            self.templist = self.flat(self.templist)
        # Handle case where optional parm is not provided
        if not self.templist:
            # Handle case where int is passed in as temperatures (no optional parm provided)
            if not isinstance(temperatures, list):
                self.templist = [temperatures]
                return self.templist
            # Handle case where temperature is passed in as a list (no optional parm provided)
            self.templist = temperatures
            return self.templist
        # Handle case where optional parm IS provided
        # And where int is passed in as temperatures
        if not isinstance(temperatures, list):
            self.templist.append(temperatures)
            return self.templist
        # Handle case where optional parm IS provided
        # And a list is passed is as temperatures
        if any(isinstance(temp, list) for temp in temperatures):
            temperatures = flat(temperatures)
        return self.templist + temperatures

    # Method to get the maximum recorded temperature
    def get_max(self, templist):
        return max(templist)

    # Method to get the minimum recorded temperature
    def get_min(self, templist):
        return min(templist)

    # Method to get the average of all the recorded temperatures - returns float
    def get_mean(self, templist):
        return float(sum(templist)/len(templist))

    # Flatten nested list helper method
    def flat(self, templist):
        if len(templist) == 0:
            return templist
        if isinstance(templist[0], list):
            return self.flat(templist[0]) + self.flat(templist[1:])
        return templist[:1] + self.flat(templist[1:])


# Unittests for Temperature Tracker class methods
class TestInsertSingleTempWithTempRecord(unittest.TestCase):
    def test_InsertSingleTempWithTempRecord(self):
        tracker = TemperatureTracker()
        record = [88, 122, 111, 75, 99]
        actual = tracker.insert(88, record)
        expected = [88, 122, 111, 75, 99, 88]

        self.assertEqual(expected, actual)


class TestInsertMultipleTempWithMultipleParms(unittest.TestCase):
    def test_InsertMultipleTempWithMultipleParms(self):
        tracker = TemperatureTracker()
        actual = tracker.insert(88, 122, 111, 75, 99, 88)
        expected = [122, 111, 75, 99, 88, 88]

        self.assertEqual(expected, actual)



class TestInsertSingleTempNoTempRecord(unittest.TestCase):
    def test_InsertSingleTempWithNoTempRecord(self):
        tracker = TemperatureTracker()
        actual = tracker.insert(96)
        expected = [96]

        self.assertEqual(expected, actual)


class TestInsertListTempWithMultipleTempRecord(unittest.TestCase):
    def test_InsertListTempWithMultipleTempRecord(self):
        tracker = TemperatureTracker()
        record = [76, 94, 115]
        record2 = [91, 113, 75]
        actual = tracker.insert([88, 122, 111], record, record2)
        expected = [76, 94, 115, 91, 113, 75, 88, 122, 111]

        self.assertEqual(expected, actual)


class TestInsertListTempWithTempRecord(unittest.TestCase):
    def test_InsertListTempWithTempRecord(self):
        tracker = TemperatureTracker()
        record = [88, 122, 111]
        actual = tracker.insert([75, 99], record)
        expected = [88, 122, 111, 75, 99]

        self.assertEqual(expected, actual)


class TestGetMaxTemp(unittest.TestCase):
    def test_GetMaxTemp(self):
        tracker = TemperatureTracker()
        record = [88, 122, 111, 75, 99]
        templist = tracker.insert([96, 83], record)
        actual = tracker.get_max(templist)
        expected = 122

        self.assertEqual(expected, actual)


class TestGetMinTemp(unittest.TestCase):
    def test_GetMinTemp(self):
        tracker = TemperatureTracker()
        record = [88, 122, 111, 75, 99]
        templist = tracker.insert([96, 83], record)
        actual = tracker.get_min(templist)
        expected = 75

        self.assertEqual(expected, actual)


class TestGetMedianTemp(unittest.TestCase):
    def test_GetMinTemp(self):
        tracker = TemperatureTracker()
        record = [88, 122, 111, 75, 99]
        templist = tracker.insert([96, 83], record)
        actual = tracker.get_mean(templist)
        expected = 96.28571428571429

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
