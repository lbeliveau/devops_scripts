import csv
import json
import math
import pprint
import requests

from collections import defaultdict
from requests.auth import HTTPBasicAuth

"""
TestRail REST API wrapper

http://docs.gurock.com/testrail-api2/
https://github.com/openstax/test-automation/blob/master/testrail/testrail.py
"""
class TestRail:
    url="https://testrail.kaloom.io"
    user='testrail-func-user@kaloom.com'
    password='KtjgzaOB6ztS9ZnYdmsI-G1A7IMuZIguyOfdcHiKb'
    headers={'Content-Type': 'application/json'}

    # Limit is 250 entries per request
    entriesPerRequest = 250

    PASSED = 1
    BLOCKED = 2
    UNTESTED = 3
    RETEST = 4
    FAILED = 5

    """
    Utility method to send one or multiple GET requests based on the maximum number of entries
    specified. Testrail support getting a maximum of 250 entries per request.

    Returns an array containing the concatenation of all the replies.
    """
    def _getRequestNumEntries(self, url, numEntries):
        array = []

        # Calculate number of pages/requests based on limit of entries per
        # request
        numPages = 1
        if numEntries > self.entriesPerRequest:
            numPages = math.ceil(numEntries / self.entriesPerRequest)

        # Number of items in the array
        num = 0
        for page in range (0, numPages):
            # If last page/request, calculate the number of entries to get based
            # on numEntries
            limit = self.entriesPerRequest
            if numEntries - num < self.entriesPerRequest:
                limit = numEntries - num

            request = url + "&offset={}&limit={}".format(page * self.entriesPerRequest, limit)
            #print(request)
            response = requests.get(request, headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
            data = json.loads(response.content)

            array = array + data
            num = num + len(data)

        return array

    """
    Returns a list of test runs for a project.
    """
    def get_runs(self, project, suite, numEntries):
        return self._getRequestNumEntries(self.url + "/index.php?/api/v2/get_runs/{}&suite_id={}".format(project, suite),
            numEntries)

    """
    Returns a list of tests for a test run.
    """
    def get_tests(self, runId):
        request = self.url + "/index.php?/api/v2/get_tests/{}".format(runId)
        #print(request)
        response = requests.get(request, headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
        return json.loads(response.content)

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    testRail = TestRail()
    runs = testRail.get_runs(1, 10, 250)
    #print(json.dumps(data, indent=4, sort_keys=True))

    results = defaultdict(lambda: {
                    'title': '',
                    'tags': '',
                    'count': 0,
                    'failed': 0,
                    'failure_rate': 0})

    # For all runs
    for run in runs:
        #print(json.dumps(run, indent=4, sort_keys=True))
        tests = testRail.get_tests(run.get('id'))
        #print(json.dumps(tests, indent=4, sort_keys=True))

        # For all tests executed in a run
        for test in tests:
            count = results[test['case_id']]['count'] + 1
            failed = results[test['case_id']]['failed']
            if test['status_id'] == TestRail.FAILED:
                failed = failed + 1
            results[test['case_id']] = {
                'title': test['title'],
                'tags': test['custom_tags'],
                'count': count,
                'failed': failed,
                'failure_rate': round((failed / count) * 100, 2)}

    # Flatten dictionnary for exporting in csv
    flatten = [{'id': k,
                'title': v['title'],
                'tags': v['tags'],
                'count': v['count'],
                'failed': v['failed'],
                'failure_rate': v['failure_rate']} for k, v in results.items()]

    dict = sorted(flatten, key=lambda x: x['failure_rate'], reverse=True)
    print(json.dumps(dict, indent=4))

    csv_file = "results.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'title', 'tags', 'count', 'failed', 'failure_rate'])
            writer.writeheader()
            for data in dict:
                writer.writerow(data)
    except IOError:
        print("I/O error")

