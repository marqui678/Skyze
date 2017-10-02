'''
Created on 05/09/2017

@author: michaelnew
'''
# 3rd Party Libraries
import os
import sys
import unittest
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal
import pandas as pd
from pandas   import ExcelWriter
from dateutil import parser
from datetime import datetime
import numpy as np


# Skyze Libraries
import settings
from Market import Market




class UnitTestSkyzeAbstract(unittest.TestCase):
    '''
    classdocs

    1. Creates a list of assertion errors rather than stopping after each error.
       See https://stackoverflow.com/questions/4732827/continuing-in-pythons-unittest-when-an-assertion-fails

    '''

    tolerance = 5e-7

    def setUp(self):
        self.assertion_errors = []
        self.start_time = datetime.now()
        self.target_columns_market = [  "Date", "Open","High", "Low", "Close",
                                        "Volume", "MarketCap"]



    def tearDown(self):
        print("\n\n\n")
        try:
            self.assertEqual([], self.assertion_errors)
        except AssertionError as err:
            # Assertion Failure
            print("=== Test Failed === === === === === ")
            print("List of Assertion Errors:")
            for assertion_error in self.assertion_errors:
                print("\n\n=== Name: "+assertion_error[0])
                print(assertion_error[1])
        else:
            # Assertion Passed
            print("=== Test Passed === === === === === ")
            print("PASS: ALL TESTS .. You Rock :)")

        print("\n\nLeft = test results ..... Right = target results")
        return

    def getTestData( self,
                     p_path,
                     p_test_file,
                     p_test_columns):

        # Get the Market data
        mkt = Market.fromTesting(p_test_file)
        mkt_data = mkt.readMarketDataCSV(p_testing=True)
        print("Rows in mkt data: "+str(len(mkt_data)))
        print("\n\n")

        return mkt_data

    def getTestAndResultData(  self,
                                p_path,
                                p_test_file,
                                p_target_file,
                                p_target_columns,
                                p_boolean_columns=None):

        # Get the Market data
        mkt = Market.fromTesting(p_test_file)
        mkt_data = mkt.readMarketDataCSV(p_testing=True)
        print("Rows in mkt data: "+str(len(mkt_data)))

        # Read in the target results
        target_data = self.readTargetResults(   p_path + p_target_file,
                                                p_target_columns)
        print("\n\n")

        # Format boolean columns
        if p_boolean_columns != None:
            for column in p_boolean_columns:
                target_data[column] = target_data[column] == True

        return mkt_data, target_data

    def series_assert(self, p_name, p_test_results, p_target_results):
        ''' Asserts two series on the same column name
            Stores errors (exceptions) in a list so that all tests are run '''

        try:
            # was assert_series_equal which did not work due to floating point precision
            print("\n--- TESTING: " + p_name + ": ", end='')
            #print("Testing: ", end='')
            #print(str(type(p_test_results[p_name].astype(np.float64))) + ": ", end='')
            #print(str(type(p_test_results[p_name].astype(np.float64)[0])))
            #print("Target: ", end='')
            #print(str(type(p_target_results[p_name])) + ": ", end='')
            #print(str(type(p_target_results[p_name][0])))
            assert_series_equal (   p_test_results[p_name].round(2), #.astype(np.float64),
                                    p_target_results[p_name].round(2),
                                    check_exact = False,             # Whether to compare number exactly.
                                    check_less_precise = True,       # False = 5 digits, Ture = 3 digits
                                    obj = p_name
                               )

        except AssertionError as err:
            # Assertion Failure
            # add to the error list
            self.assertion_errors.append([p_name, str(err)])

            # Explore the differences
            # Get the different columns
            diffs = pd.DataFrame({'test' : p_test_results[p_name], 'target' : p_target_results[p_name]})

            # diffs["Different"] = diffs["test"] != diffs["target"]
            # see PEP485 for use of isclose
            # which rows are different?
            # diffs["Different"] = np.isclose(diffs["test"], diffs["target"], rtol=1e-05, atol=1e-08, equal_nan=False)

            # how much different?
            diffs["Amount"] = diffs["test"].astype(np.float64) - diffs["target"].astype(np.float64)

            # Another way to do is close
            diffs["Different"] = diffs["Amount"] > self.tolerance

            #Create some error stats
            error_count = len(diffs.loc[diffs.Different == True])
            data_count = len(p_test_results)
            error_rate = error_count / data_count * 100

            # Print ... let 'em 'ave it
            print("\n--- FAIL: " + p_name + "  errors: " + str(error_count) + " of " + str(data_count) + " ... " + "%.2f" % error_rate)
            print("Testing: ", end='')
            print(str(type(p_test_results[p_name])) + ": ", end='')
            print(str(type(p_test_results[p_name][0])))
            print("Target: ", end='')
            print(str(type(p_target_results[p_name])) + ": ", end='')
            print(str(type(p_target_results[p_name][0])))
            print(diffs.loc[diffs.Different == True].head(10))

        except Exception as err:
            print("Exception HERE")
            print(err)

        else:
            # Assertion Passed
            print("\n+++ PASS: "+p_name)

        return

    def series_assert_diffs(self, p_name, p_test_results, p_target_results):
        """Asserts the diffs of two series are each less than 1e-8"""
        print("\n--- TESTING: " + p_name + ": ", end='')

        # Explore the differences
        # Get the different columns
        diffs = pd.DataFrame({'test' : p_test_results[p_name], 'target' : p_target_results[p_name]})

        # how much different?
        diffs["Amount"] = diffs["test"].astype(np.float64) - diffs["target"].astype(np.float64)

        # Another way to do is close
        diffs["Different"] = abs(diffs["Amount"]) > 5e-8

        # how many differences?
        error_count = len(diffs.loc[diffs.Different == True])

        try:
            self.assertEqual(error_count, 0)

        except AssertionError as err:
            # Assertion Failure
            # add to the error list
            self.assertion_errors.append([p_name, str(err)])

            #Create some error stats
            data_count = len(p_test_results)
            error_rate = error_count / data_count * 100

            # Print ... let 'em 'ave it
            print("\n--- FAIL: " + p_name + "  errors: " + str(error_count) + " of " + str(data_count) + " ... " + "%.2f" % error_rate)
            print("Testing: ", end='')
            print(str(type(p_test_results[p_name])) + ": ", end='')
            print(str(type(p_test_results[p_name][0])))
            print("Target: ", end='')
            print(str(type(p_target_results[p_name])) + ": ", end='')
            print(str(type(p_target_results[p_name][0])))
            print(diffs.loc[diffs.Different == True].head(10))

        except Exception as err:
            print("Exception In Assert Series DIff")
            print(err)

        else:
            # Assertion Passed
            print("\n+++ PASS: "+p_name)

        return

    def dataframe_assert(self, p_name, p_test_results, p_target_results):
        ''' Asserts two dataframes
            Stores errors (exceptions) in a list so that all tests are run '''

        try:
            assert_frame_equal(p_test_results, p_target_results,
            check_exact = False,             # Whether to compare number exactly.
            check_less_precise = True)       # False = 5 digits, Ture = 3 digits)
        except AssertionError as err:
            # Assertion Failure
            self.assertion_errors.append([p_name,str(err)])
            print("DATAFRAME FAIL: "+p_name)
        else:
            # Assertion Passed
            print("DATAFRAME PASS: "+p_name)

        return

    def printTestHeader(self, p_test_file, p_target_file, p_test_columns):
        ''' Prints the test info '''
        print("\n\n======= This is a test of SUPERTREND INDICATOR ==============")
        print("Start time: "+str(self.start_time))
        print("Test data: " + p_test_file + "    \nTarget data: " + p_target_file)
        print("Columns: " + str(len(p_test_columns)) + " ... "+ str(p_test_columns))
        print("Parameters: ")

        return

    def printTestInfo(self, p_output, p_mkt_data, p_target_data, p_file_name):
        if p_output:
            print();print();print(); print("=== Market Data . head === === === === === ")
            print(p_mkt_data.head(5))
            print(); print("=== Market Data . tail === === === === === ")
            print(p_mkt_data.tail(5))

            print("\n\n\n=== Target_data . head  === === === === === ")
            print(p_target_data.head(5))
            print()
            print("=== Target_data . tail === === === === === ")
            print(p_target_data.tail(5))

            # Save market data to excel
            #self.saveTestResults(p_mkt_data, "Test-Output-"+p_file_name, p_testing = True)
        return

    def printTestRun(self, p_output, p_mkt_data):
        if p_output:
            print("\n\n\n=== Test Run . head === === === === === ")
            print(p_mkt_data.head(5))
            print("\n=== Test Run . tail === === === === === ")
            print(p_mkt_data.tail(5))

    def assertBySeries(self, p_output, p_mkt_data, p_target_data, p_target_columns):
        if p_output:
            print(); print()
            print("=== Series Assertion === === === === === ")

            # loop through the series
            for test_column in p_target_columns:
                self.series_assert(test_column, p_mkt_data, p_target_data)

    def assertBySeriesDiffs(self, p_output, p_mkt_data, p_target_data, p_target_columns):
        if p_output:
            print(); print()
            print("=== Series Diff Assertion === === === === === ")

            # loop through the series
            for test_column in p_target_columns:
                self.series_assert_diffs(test_column, p_mkt_data, p_target_data)

    def readTargetResults(self, p_results_file, p_column_names):
        "Opens the file and reads the data"

        # Create the path name
        file_path = os.path.join(settings.results_file_path, "%s.csv" % p_results_file)

        # Add the standard market columns to the beginning of the column list
        column_names = self.target_columns_market + p_column_names
        print(column_names)
        try:
            # Read the target results into a dataframe
            target_results = pd.read_csv(
                                            file_path,
                                            header=None ,
                                            names = column_names,
                                            index_col=False,
                                            skiprows = 1
                                       )
        except IOError as err:
            print("File Error:   " + file_path)
            raise IOError ("FileNotFound","EXCEPTION UnitTestSkyzeAbstract::readTargetResults .... IOError File does not exist")
            return
        except:
            print("AN EXCEPTION - UnitTestSkyzeAbstract::readTargetResults(p_market)")
            print("File path:   " + file_path)
            print(sys.exc_info())
            return
        else:
            # Convert the date column to a date ! ...... Not needed now date is the index
            #target_results['Date'] = pd.to_datetime(target_results['Date'].astype(str), format='%Y%m%d')

            # Move the date column to the index
            target_results.index = [parser.parse(str(d)) for d in target_results["Date"]]
            del target_results["Date"]

            return target_results

    def saveTestResults (  self, p_results,
                            p_file_name,
                            p_file_path = "",
                            p_testing = False
                       ):
        ''' Export to excel file '''

        # set file path
        file_path = p_file_path
        if p_file_path == "":
            if p_testing:
                file_path = settings.testing_file_path
            else:
                file_path = settings.data_file_path

        # Write to Excel
        print("Test Output: "+file_path+"/"+p_file_name+".xlsx")
        writer = ExcelWriter(file_path+"/"+p_file_name+".xlsx")
        p_results.to_excel(writer, 'Results')
        writer.save()

        return
