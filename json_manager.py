import json

# Made by Joshua Thompson

### Returns dictionary data from the json file
def ReadFile(filePath):
    with open(filePath, 'r') as f:
        data = json.load(f)
        f.close()
        return data

### Saves dictionary data to a json file
def WriteFile(filePath, data):
    with open(filePath, 'w') as f:
        newData = json.dumps(data, indent=4)
        f.write(newData)
        f.close()        