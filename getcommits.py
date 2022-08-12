import json
import pprint
import requests

pp = pprint.PrettyPrinter(indent=4)

repos = ["cloudedge/buffserv",
    "cloudedge/build-dp-fpga",
    "cloudedge/build-dpdk",
    "cloudedge/common",
    "cloudedge/fpga-sro",
    "cloudedge/gtpserv",
    "cloudedge/intel-sdk-fpga",
    "cloudedge/pfcp",
    "cloudedge/qmdpi",
    "cloudedge/services",
    "cloudedge/test",
    "cloudedge/tools",
    "cloudedge/uclb",
    "cloudedge/upf",
    "cloudedge/upf-dp-bf",
    "cloudedge/upf-dp-fpga",
    "cloudedge/upf-dp-fpga-hw",
    "cloudedge/upf-dp-fpga-sw",
    "cloudedge/upf-dp-x86",
    "cloudedge/upf-pe",
    "cloudedge/upfc",
    "cloudedge/upfu",
    "flowfabric/aa-agent",
    "flowfabric/base-image",
    "flowfabric/basics",
    "flowfabric/bastioninstaller",
    "flowfabric/bato",
    "flowfabric/bnc",
    "flowfabric/bns",
    "flowfabric/build-bess",
    "flowfabric/build-dp-bf",
    "flowfabric/build-go",
    "flowfabric/cert-agent",
    "flowfabric/cli",
    "flowfabric/cni-plugins",
    "flowfabric/cni-plugins-rt",
    "flowfabric/coredns",
    "flowfabric/coredns-provisioning",
    "flowfabric/cpp-config",
    "flowfabric/dataplane-bf",
    "flowfabric/dataplane-common",
    "flowfabric/dataplane-common-hw",
    "flowfabric/dataplane-fpga",
    "flowfabric/dataplane-scripts",
    "flowfabric/dhcp",
    "flowfabric/dhcpd",
    "flowfabric/dls",
    "flowfabric/dnsmasq",
    "flowfabric/dp-bf-protobuf",
    "flowfabric/drivers",
    "flowfabric/etcd",
    "flowfabric/fcs",
    "flowfabric/fps",
    "flowfabric/frr",
    "flowfabric/gui",
    "flowfabric/haproxy",
    "flowfabric/httpd",
    "flowfabric/hwdata",
    "flowfabric/interop",
    "flowfabric/intproxy",
    "flowfabric/k8s-netagent",
    "flowfabric/k8s-nuodb",
    "flowfabric/k8s-podagent",
    "flowfabric/keepalived",
    "flowfabric/kfm",
    "flowfabric/ksdf",
    "flowfabric/ksdf-admin",
    "flowfabric/kvs",
    "flowfabric/kvs-rt-dbg",
    "flowfabric/ldap-server",
    "flowfabric/lg",
    "flowfabric/lnc",
    "flowfabric/log-collector",
    "flowfabric/log-forwarder",
    "flowfabric/msgbus",
    "flowfabric/ncs",
    "flowfabric/ncsfm",
    "flowfabric/ncsvf",
    "flowfabric/netconfig-utils",
    "flowfabric/network-operator",
    "flowfabric/nuodb",
    "flowfabric/nuodb-nuoadm",
    "flowfabric/ocp-installer",
    "flowfabric/racadm",
    "flowfabric/registry",
    "flowfabric/rts",
    "flowfabric/rtsp",
    "flowfabric/syscfg-operator",
    "flowfabric/syslogd-sidecar",
    "flowfabric/uts",
    "flowfabric/vfx",
    "flowfabric/vrouter",
    "flowfabric/vrouter-dp"]

dict = {}

for repo in repos:
    print(repo)
    request = "https://gitlab.kaloom.io/api/v4/projects/" + repo.replace("/", "%2F") + "/repository/commits?since=2021-01-01?ref_name=master?all=true&per_page=10000"
    response = requests.get(request, headers={'PRIVATE-TOKEN': 'Knbj2iNpu6sLG3jCsQ7B'})
    data = json.loads(response.content)
    #print(json.dumps(data, indent=4, sort_keys=True))

    total = 0
    num_commits = len(data)
    for commit in data:
        #print(json.dumps(commit, indent=4, sort_keys=True))
        request = "https://gitlab.kaloom.io/api/v4/projects/" + repo.replace("/", "%2F") + "/repository/commits/" + commit['id'] + "?stats=yes"
        response = requests.get(request, headers={'PRIVATE-TOKEN': 'Knbj2iNpu6sLG3jCsQ7B'})
        data = json.loads(response.content)
        #print(json.dumps(data, indent=4, sort_keys=True))
        total = total + data['stats']['additions']

    dict[repo] = {'num_commits': str(num_commits), 'total': str(total)}

#print(dict)

for key in dict:
    print(key + "," + dict[key]['num_commits'] + "," + dict[key]['total'])
