### Abstract
It's a skype leveldb binary values reader. It reads only the entires
with `ff 14 ff 0d` somewhere near to the value start and puts them 
into json array ouput. Didn't have much desire to try to recover the
rest database format along with some bytes preceding `ff 14 ff 0d`.
### How to use it
It's a standalone python3 file which uses `sys.argv`, so  
`python3 skype\_leveldb\_reader.py path\_to\_skype\_leveldb output.json`  
would be sufficent. Then it's possible to open the resulting
json file by any aprporiate software, say firefox.

It's highly recommended that you make a leveldb copy first, then apply
the program _to the copy made_ -- it's more safe.

You may also need to install the python leveldb wrapper [`plyvel`]() along
with the libraries it needs (the leveldb engine binaries itself).
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
`{` for object end, and a byte (or varint) of key-value pairs after,  
`0` for an empty string,  
`a` for a sparse array with integer indices like object key-value pairs,  
followed by a byte (or varint) number of entries, then entries,  
then `@` and number of entries (byte or varint) repeated 2 times  
(for a reason).
### Example
TODO
### Further reading
Skype 8 support database location answer [here](https://answers.microsoft.com/en-us/skype/forum/all/where-are-the-chat-messages-stored-on-the-local/04051ee2-56c2-4761-ba42-ea4bd11668b5?auth=1&page=2)
