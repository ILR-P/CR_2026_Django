import urllib.request, urllib.error

HOST = "https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net"
for path in ["/fights", "/fight", "/fight-data", "/fight-events", "/events",
             "/draft", "/soldiers", "/fights-info", "/simulate-fight", "/fight-info"]:
    try:
        with urllib.request.urlopen(HOST + path, timeout=15) as r:
            body = r.read().decode("utf-8", "replace")
            print(f"{path}: {r.status} -> {body[:300]!r}\n")
    except urllib.error.HTTPError as e:
        print(f"{path}: HTTP {e.code}")
    except Exception as e:
        print(f"{path}: {e!r}")