import requests
import json

#url of server
url = "http://localhost:5000"
while True:
    cmd = input('Enter "get" or "post" command (or "exit" to quit): ')
    if cmd == 'exit':
        break
    
    if cmd == 'get':
        response = requests.get(url)
        if response.status_code == 200:
            print("GET request successful!")
            print(response.text)
        else:
            print("GET request failed with status code:", response.status_code)

    elif cmd == 'post':
        payload = {"name": "John", "age": 30}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("POST request successful!")
            print(response.text)
        else:
            print("POST request failed with status code:", response.status_code)

    else:
        print('Invalid command')

