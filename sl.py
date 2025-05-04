import json

def load(filename, prefix=''):
    with open(prefix + filename, 'r', encoding="utf-8") as file:
        return json.load(file)

def save(filename, data, prefix=''):
    savedata = load(filename, prefix)
    with open(prefix + filename, 'w', encoding="utf-8") as file:
        try:
            json.dump(data, file, indent=4, ensure_ascii=False)
        except:
            save(filename, savedata, prefix)
