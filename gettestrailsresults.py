import csv
import json
import math
import pprint
import re
import requests

from collections import defaultdict
from copy import copy
from requests.auth import HTTPBasicAuth

"""
TestRail REST API wrapper

http://docs.gurock.com/testrail-api2/
https://github.com/openstax/test-automation/blob/master/testrail/testrail.py
"""
class TestRail:
    url = "https://testrail.kaloom.io"
    user = 'testrail-func-user@kaloom.com'
    password = 'KtjgzaOB6ztS9ZnYdmsI-G1A7IMuZIguyOfdcHiKb'
    headers = {'Content-Type': 'application/json'}

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
            response = requests.get(request, headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
            if response.status_code != 200:
                raise Exception("Bad status code {}".format(response.status_code))
            else:
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
        response = requests.get(request, headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
        if response.status_code != 200:
            raise Exception("Bad status code {}".format(response.status_code))
        else:
            return json.loads(response.content)

"""
Confluence REST API wrapper

https://developer.atlassian.com/cloud/confluence/rest/intro/
"""
class Confluence:
    url = "https://kaloom-internal.atlassian.net/wiki/rest/api"
    user = "f_atlassian-automation-user@kaloom.com"
    password = "fCMG5ijqnJx86hKyUt2w3236"
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}

    """
    Get id of a page.
    """
    def getId(self, space, title):
        request = self.url + "/content/?title={}&spaceKey={}".format(title.replace(" ", "%20"), space)
        response = requests.get(request, headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
        if response.status_code != 200:
            raise Exception("Bad status code {}".format(response.status_code))
        else:
            results = json.loads(response.content)
            return results['results'][0]['id']

    """
    Get version of a page.
    """
    def getVersion(self, id):
        request = self.url + "/content/{}/version".format(id)
        response = requests.get(request, headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
        if response.status_code != 200:
            raise Exception("Bad status code {}".format(response.status_code))
        else:
            results = json.loads(response.content)
            return results['results'][0]['number']

    """
    Update the content of an existing page.
    """
    def updatePage(self, id, space, title, version, content):
        print("*** updatePage")
        data = {
            "version": {
                "number": version
            },
            "title": title,
            "type": "page",
            "space": {
                "key": space
            },
            "status": "current",
            "ancestors": [
                {
                    "id": "6587232"
                }
            ],
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            },
            "metadata": {
                "properties": {
                    "editor": {
                        "value": "v2"
                    }
                }
            }
        }

        request = self.url + "/content/{}".format(id)
        response = requests.put(request, data = json.dumps(data), headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
        print(response.content)
        if response.status_code != 200:
            raise Exception("Bad status code {}".format(response.status_code))

    """
    Create a page.
    """
    def createPage(self, space, title, ancestor, content, overwrite=False):
        print("*** createPage")
        data = {
            "title": title,
            "type": "page",
            "space": {
                "key": space
            },
            "status": "current",
            "ancestors": [
                {
                    "id": ancestor
                }
            ],
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            },
            "metadata": {
                "properties": {
                    "editor": {
                        "value": "v2"
                    }
                }
            }
        }

        post = self.url + "/content"
        response = requests.post(post, data = json.dumps(data), headers=self.headers, auth=HTTPBasicAuth(self.user, self.password))
        print(response.content)
        if response.status_code != 200:
            results = json.loads(response.content)

            if "title already exists" in results['message'] and overwrite:
                id = self.getId(space, title)
                version = self.getVersion(id)
                self.updatePage(id, space, title, int(version) + 1, content)
            else:
                raise Exception("Bad status code {}".format(response.status_code))

"""
Flatten dictionnary in a two dimensional matrix 
"""
def toArray(dict):
    flatten = [{'id': k,
                'title': v['title'],
                'tags': v['tags'],
                'count': v['count'],
                'failed': v['failed'],
                'failure_rate': v['failure_rate']} for k, v in dict.items()]

    sortedArray = sorted(flatten, key=lambda x: x['failure_rate'], reverse=True)
    print(json.dumps(sortedArray, indent=4))

    return sortedArray

"""
Export to csv format
"""
def exportCsv(array, filename):
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'title', 'tags', 'count', 'failed', 'failure_rate'])
            writer.writeheader()
            for data in array:
                writer.writerow(data)
    except IOError:
        print("I/O error")


"""
Export summary array to confluence table
"""
def exportTable(description, array):
    #print(array)
    content = """
    <h1>{}</h1>
    <table class="wrapped fixed-table">
    <colgroup><col style="width: 80px;"/><col style="width: 400px;"/><col style="width: 200px;"/><col style="width: 80px;"/><col style="width: 80px;"/><col style="width: 80px;"/></colgroup>
    <tbody>
    <tr>
    <th>Id</th>
    <th>Title</th>
    <th>Tags</th>
    <th>Count</th>
    <th>Failed</th>
    <th>Failure rate(%)</th>
    </tr>
    """.format(description)
    for i in array:
        #print(i)
        content += """
        <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """.format(i['id'], i['title'], i['tags'], i['count'], i['failed'], i['failure_rate'])
    content += "</tbody></table>"
    return content

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    testRail = TestRail()
    runs = testRail.get_runs(1, 10, 25)
    #print(json.dumps(data, indent=4, sort_keys=True))

    testsNonCandidateSummaryQL1 = defaultdict(lambda: {
                    'title': '',
                    'tags': '',
                    'count': 0,
                    'failed': 0,
                    'failure_rate': 0})
    testsCandidateSummaryQL1 = copy(testsNonCandidateSummaryQL1)
    testsNonCandidateSummaryQL2 = copy(testsNonCandidateSummaryQL1)
    testsCandidateSummaryQL2 = copy(testsNonCandidateSummaryQL1)

    testsSummary = {
        "QL1": {
            "NonCandidate": testsNonCandidateSummaryQL1,
            "Candidate": testsCandidateSummaryQL1
        },
        "QL2": {
            "NonCandidate": testsNonCandidateSummaryQL2,
            "Candidate": testsCandidateSummaryQL2
        }
    }

    # For all runs
    for run in runs:
        print("*** Run: " + run.get('description'))
        print(json.dumps(run, indent=4, sort_keys=True))
        tests = testRail.get_tests(run.get('id'))
        ##print("*** size tests: {}".format(len(tests)))
        ####print(json.dumps(tests, indent=4, sort_keys=True))

        # For all tests executed in a run
        for test in tests:
            #print(json.dumps(test, indent=4, sort_keys=True))

            if re.search('ql1', test['custom_tags'], re.IGNORECASE):
                key1 = "QL1"
            elif re.search('ql2', test['custom_tags'], re.IGNORECASE):
                key1 = "QL2"
            else:
                continue
            key2 = "Candidate" if re.search('candidate', test['custom_tags'], re.IGNORECASE) else "NonCandidate"
            #print(key1)
            #print(key2)

            summary = testsSummary.get(key1).get(key2)

            #print(summary)
            count = summary[test['case_id']]['count'] + 1
            failed = summary[test['case_id']]['failed']
            if test['status_id'] == TestRail.FAILED:
                failed = failed + 1

            summary[test['case_id']] = {
                'title': test['title'],
                'tags': test['custom_tags'],
                'count': count,
                'failed': failed,
                'failure_rate': round((failed / count) * 100, 2)}

    #exportCsv(toArray(testsSummary), "non-candidates.csv")
    #exportCsv(toArray(testsCandidateSummary), "candidates.csv")

    #content = exportTable("QL1 Non-candidates", toArray(testsNonCandidateSummaryQL1))
    #confluence = Confluence() 
    #confluence.createPage("RPT", "Test Editor v2 Page from API", "6587232", content, overwrite=True)

