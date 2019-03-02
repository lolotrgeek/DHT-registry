import plyvel as level
import time
import operator
from ast import literal_eval as make_tuple

db = level.DB('./testdb', create_if_missing=True)


timestamp = str(time.monotonic())
encodedtimevalue = str((timestamp, 'value')).encode('utf-8')
db.put(b'this', encodedtimevalue)

# db.put(b'this', b'thisvalue')
dump = db.iterator(include_key=True, include_value=True)
# data = db.raw_iterator(include_key=True, include_value=True)

# for x in dump:
#     print(x[1].decode('utf-8'))
#     val = x[1].decode('utf-8')
#     strtuple = val.find('(')
#     if strtuple > -1 :
#         tupval = make_tuple(val)
#         print(tupval)
#         print(float(tupval[0]))



def decode_items(value):
    try: 
        val = value.decode('ascii')
        strtuple = val.find('(', 0, 1)
        if strtuple > -1 :
            return make_tuple(val)
        return val
    except:
        return value

def main():
    # for x in dump:
    #     print(decode_items(x[1]))
    
    ikeys = map(lambda item : decode_items(item[0]), db.iterator())
    ibirthday = map(lambda item : float(decode_items(item[1])[0]), db.iterator())
    ivalues = map(lambda item : decode_items(item[1])[1], db.iterator())

    # print('keys: ', list(ikeys))
    # print('birthdays: ', list(ibirthday))
    # print('items: ', list(iitems))
    print(list(zip(ikeys, ibirthday, ivalues)))

    print(list(zip(db.iterator())))

main()