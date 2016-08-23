# Performance
If you are performing serialization, chances are that you are going to be doing/have done I/O. Given how relatively slow
the I/O will be, the performance of this library, compared with that of any other (including the endless JSON
libraries touted as "ultra fast"), **is not going to be of realistic concern** given reasonable amounts of data.

However, if you happen to be serializing huge numbers of objects and need it done extraordinarily fast (in Python?), 
bare in mind that use of JSON encoders/decoders produced by this library will add a small amount of overhead on-top of 
the in-built JSON serialization methods. In addition, the complexity of the mappings used will influence the performance
(i.e. if the value of a JSON property is calculated from an object method that deduces the answer to life, the universe 
and everything, serialization is going to be rather slow).
