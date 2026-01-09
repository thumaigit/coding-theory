# -*- coding: utf-8 -*-
"""
Golden Test Case Runner for DNA Storage Code Definitions
Verifies the definitions_lib against known test cases
"""

import json

# Import the checker
try:
    from definitions_lib import DNAStorageCodeChecker
except ImportError:
    print("Error: Could not import DNAStorageCodeChecker from definitions_lib.py")
    print("Make sure definitions_lib.py is in the same directory as this script")
    exit(1)


class TestRunner:
    """Runner for golden test cases"""
    
    def __init__(self):
        self.checker = DNAStorageCodeChecker()
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_test_case(self, case, l, delta):
        """
        Run a single test case
        
        Args:
            case: Test case dictionary with 'id', 'input', 'expect', 'note'
            l: Window length parameter
            delta: Balance tolerance parameter
        
        Returns:
            (passed, details) tuple
        """
        test_id = case['id']
        input_str = case['input']
        expected = case['expect']
        note = case.get('note', '')
        
        try:
            # Run the checker
            is_balanced, violations = self.checker.is_locally_balanced(input_str, l, delta)
            
            # Check if result matches expectation
            passed = (is_balanced == expected)
            
            details = {
                'id': test_id,
                'input': input_str,
                'length': len(input_str),
                'expected': expected,
                'actual': is_balanced,
                'passed': passed,
                'note': note,
                'violations': violations if violations else None
            }
            
            return passed, details
            
        except Exception as e:
            details = {
                'id': test_id,
                'input': input_str,
                'expected': expected,
                'error': str(e),
                'passed': False
            }
            return False, details
    
    def run_test_suite(self, suite):
        """
        Run an entire test suite
        
        Args:
            suite: Test suite dictionary with 'suite_name', 'parameters', 'cases'
        
        Returns:
            Dictionary with suite results
        """
        suite_name = suite['suite_name']
        params = suite['parameters']
        l = params['l']
        delta = params['delta']
        cases = suite['cases']
        
        print("\n" + "=" * 80)
        print("Running Test Suite: {0}".format(suite_name))
        print("Parameters: l={0}, delta={1}".format(l, delta))
        print("=" * 80)
        
        suite_passed = 0
        suite_failed = 0
        results = []
        
        for case in cases:
            passed, details = self.run_test_case(case, l, delta)
            results.append(details)
            
            if passed:
                suite_passed += 1
                self.passed += 1
                status = "PASS"
                symbol = "[PASS]"
            else:
                suite_failed += 1
                self.failed += 1
                status = "FAIL"
                symbol = "[FAIL]"
                self.errors.append(details)
            
            # Print result
            print("\n{0} Test {1}: {2}".format(
                symbol, details['id'], details.get('note', '')
            ))
            print("  Input: {0} (length {1})".format(
                details['input'], details['length']
            ))
            print("  Expected: {0}, Got: {1}".format(
                details['expected'], details.get('actual', 'ERROR')
            ))
            
            if not passed and 'violations' in details and details['violations']:
                print("  Violations found:")
                for v in details['violations'][:3]:  # Show first 3 violations
                    print("    - {0}".format(v))
                if len(details['violations']) > 3:
                    print("    ... and {0} more".format(len(details['violations']) - 3))
            
            if 'error' in details:
                print("  Error: {0}".format(details['error']))
        
        print("\n{0}Suite Summary: {1}/{2} passed{3}".format(
            "-" * 80 + "\n",
            suite_passed,
            suite_passed + suite_failed,
            "\n" + "-" * 80
        ))
        
        return {
            'suite_name': suite_name,
            'parameters': params,
            'passed': suite_passed,
            'failed': suite_failed,
            'total': suite_passed + suite_failed,
            'results': results
        }
    
    def run_all_tests(self, test_data):
        """
        Run all test suites from JSON data
        
        Args:
            test_data: Dictionary with test suite data
        
        Returns:
            Overall results dictionary
        """
        print("\n" + "=" * 80)
        print("GOLDEN TEST CASE VERIFICATION")
        print("=" * 80)
        
        if 'meta' in test_data:
            print("\nTest Metadata:")
            for key, value in test_data['meta'].items():
                print("  {0}: {1}".format(key, value))
        
        suite_results = []
        
        for suite in test_data.get('test_suites', []):
            result = self.run_test_suite(suite)
            suite_results.append(result)
        
        # Overall summary
        print("\n" + "=" * 80)
        print("OVERALL SUMMARY")
        print("=" * 80)
        print("Total Tests Passed: {0}".format(self.passed))
        print("Total Tests Failed: {0}".format(self.failed))
        print("Total Tests Run: {0}".format(self.passed + self.failed))
        print("Success Rate: {0:.1f}%".format(
            100.0 * self.passed / (self.passed + self.failed) if (self.passed + self.failed) > 0 else 0
        ))
        
        if self.failed > 0:
            print("\n" + "=" * 80)
            print("FAILED TEST DETAILS")
            print("=" * 80)
            for err in self.errors:
                print("\nTest {0}: {1}".format(err['id'], err.get('note', '')))
                print("  Input: {0}".format(err['input']))
                print("  Expected: {0}, Got: {1}".format(
                    err['expected'], err.get('actual', 'ERROR')
                ))
                if 'error' in err:
                    print("  Error: {0}".format(err['error']))
        
        return {
            'total_passed': self.passed,
            'total_failed': self.failed,
            'suite_results': suite_results
        }


def load_golden_tests(filename):
    """Load test cases from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except IOError as e:
        print("Error loading test file: {0}".format(e))
        return None
    except json.JSONDecodeError as e:
        print("Error parsing JSON: {0}".format(e))
        return None


if __name__ == "__main__":
    # You can either load from file or use inline JSON
    
    # Option 1: Load from file
    test_data = load_golden_tests('golden_test_cases_v2.json')
    
    # Option 2: Inline test data (paste your JSON here)
    # test_data = {
    #   "meta": {
    #     "description": "Enhanced Test Suite with longer random sequences (Length 10-20)",
    #     "generated_by": "M4_Verifier_Assistant"
    #   },
    #   "test_suites": [
    #     {
    #       "suite_name": "Random_Long_Sequences_l4_d1",
    #       "parameters": { "l": 4, "delta": 1 },
    #       "cases": [
    #         { "id": "R_L4_1", "input": "11100101000", "expect": True, "note": "Random valid length 11" },
    #         { "id": "R_L4_2", "input": "000110111101001", "expect": False, "note": "Random invalid length 15" },
    #         { "id": "R_L4_3", "input": "00001100001011", "expect": False, "note": "Random invalid length 14" },
    #         { "id": "R_L4_5", "input": "01010010101001110101", "expect": True, "note": "Random valid length 20" },
    #         { "id": "R_L4_6", "input": "011100011000011111", "expect": False, "note": "Random invalid length 18" },
    #         { "id": "R_L4_10", "input": "10101010001010", "expect": True, "note": "Random valid length 14" },
    #         { "id": "R_L4_14", "input": "11010010100", "expect": True, "note": "Random valid length 11" },
    #         { "id": "R_L4_18", "input": "00100110110100010100", "expect": True, "note": "Random valid length 20" }
    #       ]
    #     },
    #     {
    #       "suite_name": "Random_Long_Sequences_l8_d1",
    #       "parameters": { "l": 8, "delta": 1 },
    #       "cases": [
    #         { "id": "R_L8_1", "input": "001000101011011110", "expect": False, "note": "Invalid: substring weight violation" },
    #         { "id": "R_L8_3", "input": "10001110010011", "expect": True, "note": "Valid length 14" },
    #         { "id": "R_L8_5", "input": "110011000110", "expect": True, "note": "Valid length 12" },
    #         { "id": "R_L8_9", "input": "1010011011000011011", "expect": True, "note": "Valid length 19 (Long string test)" },
    #         { "id": "R_L8_13", "input": "1111000111100000001", "expect": False, "note": "Invalid: '0000000' implies weight too low" },
    #         { "id": "R_L8_15", "input": "001001011001010", "expect": True, "note": "Valid length 15" }
    #       ]
    #     }
    #   ]
    # }
    
    if test_data:
        runner = TestRunner()
        results = runner.run_all_tests(test_data)
        
        # Exit with appropriate code
        exit(0 if runner.failed == 0 else 1)
    else:
        print("No test data loaded!")
        exit(1)