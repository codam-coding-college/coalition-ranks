from intra import ic


campus_id = 13
cursus_id = 1

# Filter by campus in specified range of updated_at
payload = {
    "filter[campus_id]":campus_id,
    "range[updated_at]":"2019-01-01T00:00:00.000Z,2020-01-01T00:00:00.000Z"
}

# GET campus_users of specified campus in range
response = ic.get("campus_users", params=payload)
if response.status_code == 200: # Is the status OK?
    data = response.json()

for user in data:
    print(user)