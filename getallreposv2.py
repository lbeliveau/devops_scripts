import json
import pprint
import re
import requests

pp = pprint.PrettyPrinter(indent=4)

repos = []

for page in range (1, 100):
    print("*** Fetching page %d" % page)

    url = "https://gitlab.kaloom.io/api/v4/projects?per_page=100&page=" + str(page)
    response = requests.get(url, headers={'PRIVATE-TOKEN': 'Knbj2iNpu6sLG3jCsQ7B'})
    data = json.loads(response.content)
    #print(json.dumps(data, indent=4, sort_keys=True))

    if len(data) == 0:
        break

    for repo in data:
        #print(json.dumps(repo, indent=4, sort_keys=True))
        #print(repo['web_url'])
        repos.append(repo['http_url_to_repo'])

for elem in sorted(repos):
    #print(elem)
    s = elem.replace("https://gitlab.kaloom.io/", "")
    r = re.split('/', s)
    a = r[0:-1]
    path = '/'.join(a)
    print("mkdir -p {}; pushd {}; git clone --recurse-submodules {}; popd".format(path, path, elem.rstrip('\\')))
