# Alternatives
* If you are not using class-based Python models and have no restrictions on the structure of the JSON representation:
    * [Python's in-built `json` library](https://docs.python.org/3/library/json.html) will work out the box with its 
    default encoder (`JSONEncode`) and decoder (`JSONDecode`).
    * [demjson](https://github.com/dmeranda/demjson) can encode and decode JSON with added syntax checking.
    * [ultrajson](https://github.com/esnme/ultrajson) is claimed as an "ultra fast" JSON encoder and decoder.
    * [py-yajl](https://github.com/rtyler/py-yajl) is yet another "fast" JSON encoder/decoder.
* If you are using class-based Python models but your JSON need not be human readable and you are not concerned with
interoperability:
    * [jsonpickle](https://github.com/jsonpickle/jsonpickle) will automatically serialize objects.
    * [py-importjson](https://github.com/TonyFlury/py-importjson).
* If you want to deserialize flat data files into Python `dict` objects using mapping schema:
    * [jsonmapping](https://github.com/pudo/jsonmapping)
* If you do not mind coupling your Python models to the serialization library:
    * [jsonobject](https://github.com/dimagi/jsonobject).
* If you only wish to serialize models using a mapping schema and are not interested in deserialization or compatibility
with Python's in-built `json` library.
    * [serpy](https://github.com/clarkduvall/serpy) can serialize complex models with arbitrary mappings from fields and
    methods to JSON.