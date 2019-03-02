import plyvel as level

db = level.DB('8469KBucket', create_if_missing=False)

dump = db.iterator()

for x in dump:
    print(x)