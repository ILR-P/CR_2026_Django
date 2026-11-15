import urllib.request
import json

BASE = 'https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net'

# Check fight batches
print("=== FIGHT BATCHES ===")
batch = 0
while True:
    try:
        url = BASE + '/fight/' + str(batch)
        r = urllib.request.urlopen(url, timeout=15)
        data = json.loads(r.read())
        fights = data.get('data', [])
        nb = data.get('next_batch')
        print("Fight batch", batch, ":", len(fights), "fights, next_batch=", nb)
        if nb is None or nb == batch:
            break
        batch = nb
    except Exception as e:
        print("Batch", batch, "error:", e)
        break

# Check draft batches
print("\n=== DRAFT BATCHES ===")
batch = 0
while True:
    try:
        url = BASE + '/draft/' + str(batch)
        r = urllib.request.urlopen(url, timeout=15)
        data = json.loads(r.read())
        people = data.get('data', [])
        nb = data.get('next_batch')
        print("Draft batch", batch, ":", len(people), "people, next_batch=", nb)
        if nb is None or nb == batch:
            break
        batch = nb
    except Exception as e:
        print("Batch", batch, "error:", e)
        break
