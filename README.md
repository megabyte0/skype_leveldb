### Skype message leveldb value format
 at least the leveldb values that contain `ff 14 ff 0d` also contain some
useful information like messages.
For the leveldb values format after the `ff 14 ff 0d`
it's easy to read and understand, say, after 5 hours of seeing an example
and trying to play with the decoding, for a person with iwad archive
structure reading from scratch, [bencoded](https://en.wikipedia.org/wiki/Bencode)
[.torrent](https://en.wikipedia.org/wiki/Torrent_file) files structure
reading from scratch, swf ABC code de-compiling using docs,
reading mpeg-layer-III chunk header (with docs), midi format (with docs) 
background.

It's highly doubtful that there are any open docs that cover skype leveldb
entire structure, so let it be here. After the `ff 14 ff 0d` bytes (the bytes
are at the very beginning, like at most 3 bytes away from the start)
there is a bencode-similar encoded structure and first goes the control byte.
`o` stands for object, it ends with `{` and one byte
(or a big-endian-[varint](https://en.wikipedia.org/wiki/Variable-length_quantity))
number of key-value pairs in the preceded object,  
the keys and values are interleaved like key0, value0, key1, value1, etc,  
`"` stands for 1-byte-per-character plain ASCII string, followed by
big-endian-varint length and the string itself,  
`c` (or `\x00c`) stands for the same, except for there is 2 bytes per character,
big-endian,  
`A` stands for an array, then the number of items (one byte or varint),
then items,  
`I` for an integer, big-end varint,  
`N` for big-end 8-bytes double (precision floating point),  
`F` for false,  
`T` for true,  
`_` for None (null),  
`{` for object end, and a byte (or varint) of key-value pairs after
