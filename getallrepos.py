import json
import pprint
import requests

pp = pprint.PrettyPrinter(indent=4)

repos = []
excluded = []

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
        if repo['path_with_namespace'].startswith('flowfabric') or repo['path_with_namespace'].startswith('cloudedge'):
            repos.append(repo['web_url'])
        else:
            excluded.append(repo['web_url'])

for elem in sorted(repos):
    print(elem)
    
print(" ") 
for elem in sorted(excluded):
    print(elem)
