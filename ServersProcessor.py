import time
import os
import io
import json
import socket
import math

max_conn_time = 50.0  # msec
min_servers = 5
servers_path = "/host/config/steam_data/servers.json"
period = 600  # sec


# read and deserialize servers from servers.json
def readServers():
    servers = None
    with open(servers_path, "r") as f:
        servers = json.load(f)
    return servers


def save_as_file(servers):
    with open(servers_path, "w") as f:
        f.write(json.dumps(servers, indent=4))


def reload():
    print("reloading csgofloat...")
    # os.system("docker restart csgofloat")


def tcp_check(host, port, timeout=10):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)  # seconds
        start = time.time()
        s.connect((host, port))
        end = time.time()
        conn_time = (end - start) * 1000
        print("{}:{}, time:{:.3f}ms   ".format(host, port, conn_time))
        return conn_time
    except Exception as e:
        print(e, ": {}:{} ".format(host, port))
        return float('inf')
    finally:
        if s:
            s.close()


def cal_servers_conn_time():
    servers = readServers()
    ans = []
    for server in servers:
        conn_time = tcp_check(server["host"], server["port"], 2)
        ans.append({
            "host": server["host"],
            "port": server["port"],
            "conn_time": conn_time
        })
    return ans


def filter_servers(servers, filter):
    filtered_servers = []
    servers.sort(key=lambda server: server["conn_time"])
    for server in servers:
        if filter(servers, server):
            filtered_servers.append(server)
    return filtered_servers


# servers are sorted
def filter(servers, server):
    if math.isinf(server["conn_time"]):
        return False
    if server["conn_time"] < max_conn_time or (len(servers) > min_servers and server["conn_time"] < servers[min_servers]["conn_time"]):
        return True
    return False


if __name__ == "__main__":
    while True:
        all_servers = cal_servers_conn_time()
        well_servers = filter_servers(all_servers, filter)
        temp = []
        for server in well_servers:
            print(server)
            temp.append({"host": server["host"], "port": server["port"]})
        if len(temp) > 0:
            save_as_file(temp)
            print("save servers to file:", servers_path)
        # reload()
        time.sleep(period)