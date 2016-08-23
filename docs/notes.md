# Notes
* Decoders and encoders work for iterable collections of instances in the same way as they do for single instances.
* Encoders will serialize `None` to `null` and visa-versa for decoders.
* Encoders will only encode objects into JSON objects (`{}`). A custom `JSONEncoder` must be used to encode Python 
objects that should be represented in any other way (e.g. as a JSON list (`[]`)).
* Ensure your serializers are not vulnerable to attack if you are serializing JSON from an untrusted source.