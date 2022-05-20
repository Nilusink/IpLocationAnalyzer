"""
File:
ip_tools.py

set of functions for finding ip addresses and getting their location

Author:
Nilusink
"""
from .tools import remove_all
import subprocess

import requests
import json


def ip_geolocation(ip_address: str) -> dict:
    # URL to send the request to
    request_url = 'https://geolocation-db.com/jsonp/' + ip_address.strip()

    # Send request and decode the result
    response = requests.get(request_url)
    result = response.content.decode()

    # Clean the returned string, so it just contains the dictionary data for the IP address
    result = result.split("(")[1].strip(")")

    # Convert this data into a dictionary
    return json.loads(result)


def get_external_ip() -> str:
    return requests.get('https://api.ipify.org').content.decode('utf8')


def get_connections() -> list[dict]:
    result = subprocess.run(["netstat", "-natp"], stdout=subprocess.PIPE)
    cmd = result.stdout.decode('utf-8').split("\n")
    headers = cmd[1].split(" ")

    remove_all(headers, "Address")
    remove_all(headers, "")

    out = []
    for element in cmd[2::]:
        now = element.split(" ")

        remove_all(now, "")

        out.append({
            h.lower(): e for h, e in zip(headers, now)
        })

    return out


def get_foreign_addresses() -> list[tuple, tuple]:
    connections = get_connections()
    out: list = []

    # predefine ips to ignore
    ips: list[str] = [
        "0.0.0.0",
        "127.0.0.1",
    ]

    for connection in connections:
        if connection:
            ip = connection["foreign"].split(":")[0]
            if ip not in ips:
                out.append((ip, connection))
                ips.append(ip)

    return out
