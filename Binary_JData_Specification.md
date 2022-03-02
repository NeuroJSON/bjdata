Binary JData: A portable interchange format for complex binary data
============================================================

- **Status of this document**: Request for comments
- **Maintainer**: Qianqian Fang <q.fang at neu.edu>
- **License**: Apache License, Version 2.0
- **Version**: 1 (Draft 2)
- **Last Stable Release**: [Version 1 (Draft 2)](https://github.com/NeuroJSON/bjdata/blob/Draft_2/Binary_JData_Specification.md)
- **Abstract**:

> The Binary JData (BJData) Specification defines an efficient serialization 
protocol for unambiguously storing complex and strongly-typed binary data found 
in diverse applications. The BJData specification is the binary counterpart
to the JSON format, both of which are used to serialize complex data structures
supported by the JData specification (http://openjdata.org). The BJData spec is 
derived and extended from the Universal Binary JSON (UBJSON, http://ubjson.org) 
specification (Draft 12). It adds supports for N-dimensional packed arrays and 
extended binary data types.

## Table of Content

- [Introduction](#introduction)
- [License](#license)
- [Format Specification](#format-specification)
  - [Format overview](#format_overview)
  - [Type summary](#type_summary)
  - [Value types](#value_types)
  - [Container types](#container_types)
  - [Optimized format](#container_optimized)
- [Recommended File Specifiers](#recommended-file-specifiers)
- [Acknowledgement](#acknowledgement)

Introduction
------------------------------

The Javascript Object Notation (JSON) format, formally known as the ECMA-404 
or ISO21778:2017 standard, is ubiquitously used in today's web and native 
applications. JSON presents numerous advantages, such as human readability, 
generality for accommodating complex hierarchical data, self-documentation, and 
abundant existing free and commercial libraries. However, its utility is largely 
restricted to the storage of lightweight textural data, and has very limited presence 
in many data-intensive and performance-demanding applications, such as database
backends, medical imaging, and scientific data storage.
 
The lack of support for strongly-typed and binary data has been one of the main 
barriers towards widespread adoption of JSON in these domains. In recent years, 
efforts to address these limitation have resulted in an array of versatile binary 
JSON formats, such as BSON (Binary JSON, http://bson.org), UBJSON (Universal Binary 
JSON, http://ubjson.org), MessagePack (https://msgpack.org), CBOR (Concise Binary 
Object Representation, [RFC 7049], https://cbor.io) etc. These binary JSON 
counterparts are broadly used in speed-sensitive data processing applications and
address various needs from a diverse range of applications.
 
To better champion findable, accessible, interoperable, and reusable 
([FAIR principle](https://www.nature.com/articles/sdata201618)) data in 
scientific data storage and management, we have created the **OpenJData Initiative**
(http://openjdata.org) to develop a set of open-standards for portable, human-readable 
and high-performance data annotation and serialization aimed towards enabling
scientific researchers, IT engineers, as well as general data users to efficiently 
annotate and store complex data structures arising from diverse applications.
 
The OpenJData framework first converts complex data structures, such as N-D
arrays, trees, tables and graphs, into easy-to-serialize, portable data annotations
via the **JData Specification** (https://github.com/NeuroJSON/jdata) and then serializes 
and stores the annotated JData constructs using widely-supported data formats. 
To balance data portability, readability and efficiency, OpenJData defines a 
**dual-interface**: a text-based format **syntactically compatible with JSON**,
and a binary-JSON format to achieve significantly smaller file sizes and faster 
encoding/decoding.
 
The Binary JData (BJData) format is the **official binary interface** for the JData 
specification. It is derived from the widely supported UBJSON Specification 
Draft 12 (https://github.com/ubjson/universal-binary-json), and adds native
support for **N-dimensional packed arrays** - an essential data structure for
scientific applications - as well as extended binary data types, including unsigned
integer types and half-precision floating-point numbers. The new data constructs
also allow a BJData file to store binary arrays larger than 4 GB in size, which
is not currently possible with MessagePack (maximum data record size is limited
to 4 GB) and BSON (maximum total file size is 4 GB).
 
A key rationale for basing the BJData format upon UBJSON as opposed to 
other more popular binary JSON-like formats, such as BSON, CBOR and MessagePack, 
is UBJSON's **quasi-human-readability** - a unique characteristic that is 
absent from almost all other binary formats. This is because all data semantic 
elements in a UBJSON/BJData file, e.g. the "name" fields and data-type markers, 
are defined in human-readable strings. The resulting binary files are not only
capable of storing complex and hierarchical binary data structures, but also 
directly readable using an editor with minimal or no processing. We anticipate that
such a unique capability, in combination with the highly portable JData annotation 
keywords, makes a data file self-explanatory, easy to reuse, and easy to 
inter-operate in complex applications.


License
------------------------------

The Binary JData Specification is licensed under the
[Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0.html).


Format Specification
------------------------------

## <a name="format_overview"/>Format overview

A single construct with two optional segments (length and data) is used for all 
types:
```
[type, 1-byte char]([integer numeric length])([data])
```
Each element in the tuple is defined as:
- **type** - A 1-byte ASCII char (**_Marker_**) used to indicate the type of 
the data following it.

- **length** (_optional_) - A positive, integer numeric type (`uint8`, `int8`, 
`uint16`, `int16`, `uint32`, `int32`, `uint64` or `int64`) specifying the length 
of the following data payload.

- **data** (_optional_) - A contiguous byte-stream containing serialized binary  
data representing the actual binary data for this type of value.

### Notes
- Some values are simple enough that just writing the 1-byte ASCII marker into 
the stream is enough to represent the value (e.g. `null`), while others have a 
type that is specific enough that no length is needed as the length is implied 
by the type (e.g. `int32`). Yet others still require both a type and a length to 
communicate their value (e.g. `string`). In addition, some values (e.g. `array`) 
have additional (_optional_) parameters to improve decoding efficiency and/or 
to reduce the size of the encoded value even further.

- The BJData specification (since Draft-2) requires that all numeric values must be
written in the **Little-Endian order**. This is a breaking change compared to 
BJData Draft-1 and UBJSON Draft-12, where numeric values are in Big-Endian order.

- The `array` and `object` data types are **container** types, similar to JSON
arrays and objects. They help partition and organize data records of all types, 
including container types, into composite and complex records.

- Using a [strongly-typed](#container_optimized) container construct can further 
reduce data file sizes as it extracts common data type markers to the header. It
also helps a parser to pre-allocate necessary memory buffers before reading the 
data payload.

In the following sections, we use a **block-notation** to illustrate the layout
of the encoded data. In this notation, the data type markers and individual 
data payloads are enclosed by a pair of `[]`, strictly for illustration purposes.
Both illustration markers `[` and `]` as well as the whitespaces between these 
data elements, if present, shall be ignored when performing the actual data storage.



## <a name="type_summary"/>Type summary

Type | Total size | ASCII Marker(s) | Length required | Data (payload)
---|---|---|---|---
[null](#value_null) | 1 byte | *Z* | No | No
[no-op](#value_noop) | 1 byte | *N* | No | No
[true](#value_bool) | 1 byte | *T* | No | No
[false](#value_bool) | 1 byte | *F* | No | No
[int8](#value_numeric) | 2 bytes | *i* | No | Yes
[uint8](#value_numeric) | 2 bytes | *U* | No | Yes
[int16](#value_numeric) | 3 bytes | *I* (upper case i) | No | Yes
[uint16](#value_numeric)* | 3 bytes | *u* | No | Yes
[int32](#value_numeric) | 5 bytes | *l* (lower case L) | No | Yes
[uint32](#value_numeric)* | 5 bytes | *m* | No | Yes
[int64](#value_numeric) | 9 bytes | *L* | No | Yes
[uint64](#value_numeric)* | 9 bytes | *M* | No | Yes
[float16/half](#value_numeric)* | 3 bytes | *h* | No | Yes
[float32/single](#value_numeric) | 5 bytes | *d* | No | Yes
[float64/double](#value_numeric) | 9 bytes | *D* | No | Yes
[high-precision number](#value_numeric) | 1 byte + int num val + string byte len | *H* | Yes | Yes
[char](#value_char) | 2 bytes | *C* | No | Yes
[string](#value_string) | 1 byte + int num val + string byte len | *S* | Yes | Yes (if not empty)
[array](#container_array) | 2+ bytes | *\[* and *\]* | Optional | Yes (if not empty)
[object](#container_object) | 2+ bytes | *{* and *}* | Optional | Yes (if not empty)

\* Data type markers that are not defined in the UBJSON Specification (Draft 12)


## <a name="value_types"/>Value types

### <a name="value_null"/>Null
The `null` value is equivalent to the `null` value from the JSON specification.

#### Example
In JSON:
```json
{
    "passcode": null
}
```

In BJData (using block-notation):
```
[{]
    [i][8][passcode][Z]
[}]
```

---
### <a name="value_noop"/>No-Op
There is no equivalent to the `no-op` value in the original JSON specification. When 
decoding, No-Op values should be skipped.

The intended usage of the `no-op` value is as a valueless signal between a 
producer (most likely a server) and a consumer (most likely a client) to indicate 
activity, for example, as a keep-alive signal so that a client knows a server is 
still working and hasn't hung or timed out.

---
### <a name="value_bool"/>Boolean
A Boolean type is equivalent to the Boolean value (`true` or `false`) defined in 
the JSON specification.

#### Example
In JSON:
```json
{
    "authorized": true,
    "verified": false
}
```

In BJData (using block-notation):
```
[{]
    [i][10][authorized][T]
    [i][8][verified][F]
[}]
```

---
### <a name="value_numeric"/>Numeric
Unlike in JSON, which has a single _Number_ type (used for both integers and 
floating point numbers), BJData defines multiple types for integers. The 
minimum/maximum of values (inclusive) for each integer type are as follows:

Type | Signed | Minimum | Maximum
---|---|---|---
int8 | Yes | -128 | 127
uint8 | Yes | 0 | 255
int16 | No | -32,768 | 32,767
uint16| Yes | 0 | 65,535
int32 | No | -2,147,483,648 | 2,147,483,647
uint32| Yes | 0 | 4,294,967,295
int64 | No | -9,223,372,036,854,775,808 | 9,223,372,036,854,775,807
uint64| Yes | 0 | 18,446,744,073,709,551,615
float16/half | Yes | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-2008_revision) | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-2008_revision)
float32/single | Yes | See [IEEE 754 Spec](http://en.wikipedia.org/wiki/IEEE_754-1985) | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-1985)
float64/double | Yes | See [IEEE 754 Spec](http://en.wikipedia.org/wiki/IEEE_754-1985) | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-1985)
high-precision number | Yes | Infinite | Infinite

**Notes**:
- Numeric values of `+infinity`, `-infinity` and `NaN` are to be encoded using their respective 
IEEE 754 binary form; **this is different** from the UBJSON specification where `NaN`
and infinity are converted to [`null`](#value_null).
- It is advisable to use the smallest applicable type when encoding a number.

#### Integer
All integer types (`uint8`, `int8`, `uint16`, `int16`, `uint32`, `int32`, `uint64` and 
`int64`) are written in **Little-Endian order** (this is different from UBJSON, where all
integers are written in Big-Endian order).

#### Float
All float types (`half`, `single`, `double` are written in **Little-Endian order** 
(this is different from UBJSON which does not specify the endianness of floats).

- `float16` or half-precision values are written in [IEEE 754 half precision floating point 
format](https://en.wikipedia.org/wiki/IEEE_754-2008_revision), which has the following 
structure:
  - Bit 15 (1 bit) - sign
  - Bit 14-10 (5 bits) - exponent
  - Bit 9-0 (10 bits) - fraction (significant)

- `float32` or single-precision values are written in [IEEE 754 single precision floating point 
format](http://en.wikipedia.org/wiki/IEEE_754-1985), which has the following 
structure:
  - Bit 31 (1 bit) - sign
  - Bit 30-23 (8 bits) - exponent
  - Bit 22-0 (23 bits) - fraction (significant)

- `float64` or double-precision values are written in [IEEE 754 double precision floating point 
format](http://en.wikipedia.org/wiki/IEEE_754-1985), which has the following 
structure:
  - Bit 63 (1 bit) - sign
  - Bit 62-52 (11 bits) - exponent
  - Bit 51-0 (52 bits) - fraction (significant)


#### High-Precision
These are encoded as a string and thus are only limited by the maximum string 
size. Values **must** be written out in accordance with the original [JSON 
number type specification](http://json.org).

#### Examples
Numeric values in JSON:
```json
{
    "int8": 16,
    "uint8": 255,
    "int16": 32767,
    "uint16": 32768,
    "int32": 2147483647,
    "int64": 9223372036854775807,
    "uint64": 9223372036854775808,
    "float32": 3.14,
    "float64": 113243.7863123,
    "huge1": "3.14159265358979323846",
    "huge2": "-1.93+E190",
    "huge3": "719..."
}
```

In BJData (using block-notation):
```
[{]
    [i][4][int8][i][16]
    [i][5][uint8][U][255]
    [i][5][int16][I][32767]
    [i][6][uint16][u][32768]
    [i][5][int32][l][2147483647]
    [i][5][int64][L][9223372036854775807]
    [i][6][uint64][M][9223372036854775808]
    [i][7][float32][d][3.14]
    [i][7][float64][D][113243.7863123]
    [i][5][huge1][H][i][22][3.14159265358979323846]
    [i][5][huge2][H][i][10][-1.93+E190]
    [i][5][huge3][H][U][200][719...]
[}]
```

---
### <a name="value_char"/>Char
The `char` type in BJData is an unsigned byte meant to represent a single 
printable ASCII character (decimal values 0-127). It **must not** have a 
decimal value larger than 127. It is functionally identical to the `uint8` type, 
but semantically is meant to represent a character and not a numeric value.

#### Example
Char values in JSON:
```json
{
    "rolecode": "a",
    "delim": ";",
}
```

BJData (using block-notation):
```
[{]
    [i][8][rolecode][C][a]
    [i][5][delim][C][;]
[}]
```

---
### <a name="value_string"/>String
The `string` type in BJData is equivalent to the `string` type from the JSON 
specification apart from the fact that BJData string value **requires** UTF-8 
encoding.

#### Example
String values in JSON:
```json
{
    "username": "andy",
    "imagedata": "...huge string payload..."
}
```

BJData (using block-notation):
```
[{]
    [i][8][username][S][i][4][andy]
    [i][9][imagedata][S][l][2097152][...huge string payload...]
[}]
```


## <a name="container_types"/>Container types
See also [optimized format](#container_optimized) below.

### <a name="container_array"/>Array
The `array` type in BJData is equivalent to the `array` type from the JSON 
specification. 

The child elements of an array are ordered and can be accessed by their indices.

#### Example
Array in JSON:
```json
[
    null,
    true,
    false,
    4782345193,
    153.132,
    "ham"
]
```

BJData (using block-notation):
```
[[]
    [Z]
    [T]
    [F]
    [l][4782345193]
    [d][153.132]
    [S][i][3][ham]
[]]
```

---
### <a name="container_object"/>Object
The `object` type in BJData is equivalent to the `object` type from the JSON 
specification. Since value names can only be strings, the *S* (string) marker 
**must not** be included since it is redundant.

The child elements of an object are ordered and can be accessed by their names.

#### Example

Object in JSON:
```json
{
    "post": {
        "id": 1137,
        "author": "Andy",
        "timestamp": 1364482090592,
        "body": "The quick brown fox jumps over the lazy dog"
    }
}
```

BJData (using block-notation):
```
[{]
    [i][4][post][{]
        [i][2][id][I][1137]
        [i][6][author][S][i][4][Andy]
        [i][9][timestamp][L][1364482090592]
        [i][4][body][S][i][43][The quick brown fox jumps over the lazy dog]
    [}]
[}]
```

## <a name="container_optimized"/>Optimized Format
Both container types (`array` and `object`) support optional parameters that can 
help optimize the container for better parsing performance and smaller size.

### Type - *$*
When a _type_ is specified, all value types stored in the container (either 
array or object) are considered to be of that singular _type_ and, as a result, 
_type_ markers are omitted for each value within the container. This can be 
thought of as providing the ability to create a strongly-typed container in BJData.

A major different between BJData and UBJSON is that the _type_ in a BJData
strongly-typed container is limited to **non-zero-fixed-length data types**, therefore,
only integers (`i,U,I,u,l,m,L,M`), floating-point numbers (`h,d,D`) and char (`C`)
are qualified. All zero-length types (`T,F,Z,N`), variable-length types(`S, H`)
and container types (`[,{`) shall not be used in an optimized _type_ header.
This restriction is set to reduce the security risks due to potentials of
buffer-overflow attacks using [zero-length markers](https://github.com/nlohmann/json/issues/2793),
hampered readability and dimished benefit using variable/container
types in an optimized format.

The requirements for _type_ are

- If a _type_ is specified, it **must** be one of `i,U,I,u,l,m,L,M,h,d,D,C`.
- If a _type_ is specified, it **must** be done so before a _count_.
- If a _type_ is specified, a _count_ **must** be specified as well. (Otherwise 
it is impossible to tell when a container is ending, e.g. did you just parse 
*]* or the `int8` value of 93?)

#### Example (uint8 type):
```
[$][U]
```

---
### Count - *\#*
When a _count_ is followed by a single non-negative integer record, i.e. one of
`i,U,I,u,l,m,L,M`, it specifies the total child element count. This allows the 
parser to pre-size any internal construct used for parsing, verify that the 
promised number of child values were found, and avoid scanning for any terminating 
bytes while parsing. 

- A _count_ can be specified without a _type_.

#### Example (count of 64):
```
[#][i][64]
```

### Optimized N-dimensional array of uniform type
When both _type_ and _count_ are specified and the _count_ marker `#` is followed 
by `[`, the parser should expect the following sequence to be a 1-D `array` with 
zero or more (`Ndim`) integer elements (`Nx, Ny, Nz, ...`). This specifies an 
`Ndim`-dimensional array of uniform type specified by the _type_ marker after `$`. 
The array data are serialized in the **row-major format**.

For example, the below two block sequences both represent an `Nx*Ny*Nz*...` array of
uniform numeric type:

```
[[] [$] [type] [#] [[] [$] [Nx type] [#] [Ndim type] [Ndim] [Nx Ny Nz ...]  [Nx*Ny*Nz*...*sizeof(type)]
  or
[[] [$] [type] [#] [[] [Nx type] [nx] [Ny type] [Ny] [Nz type] [Nz] ... []] [Nx*Ny*Nz*...*sizeof(type)]
```
where `Ndim` is the number of dimensions, and `Nx`, `Ny`, and `Nz` ... are 
all non-negative numbers specifying the dimensions of the N-dimensional array.
`Nz/Ny/Nz/Ndim` types must be one of the integer types (`i,U,I,u,l,m,L,M`). 
The binary data of the N-dimensional array is then serialized into a 1-D vector
in the **row-major** element order (similar to C, C++, Javascript or Python) .


#### Example (a 2x3x4 `uint8` array):
The following 2x3x4 3-D `uint8` array 
```
[
     [
          [1,9,6,0],
          [2,9,3,1],
          [8,0,9,6]
      ],
      [
          [6,4,2,7],
          [8,5,1,2],
          [3,3,2,6]
      ]
]
```
shall be stored as
```
 [[] [$][U] [#][[] [$][U][#][3] [2][3][4]
    [1][9][6][0] [2][9][3][1] [8][0][9][6] [6][4][2][7] [8][5][1][2] [3][3][2][6]
```


### Additional rules
- A _count_ **must** be >= 0.
- A _count_ can be specified by itself.
- If a _count_ is specified, the container **must not** specify an end-marker.
- A container that specifies a _count_ **must** contain the specified number of 
child elements.
- If a _type_ is specified, it **must** be done so before _count_.
- If a _type_ is specified, a _count_ **must** also be specified. A _type_ 
cannot be specified by itself.
- A container that specifies a _type_ **must not** contain any additional 
_type_ markers for any contained value.

---
### Array Examples
Optimized with _count_
```
[[][#][i][5] // An array of 5 elements.
    [d][29.97]
    [d][31.13]
    [d][67.0]
    [d][2.113]
    [d][23.8889]
// No end marker since a count was specified.
```
Optimized with both _type_ and _count_
```
[[][$][d][#][i][5] // An array of 5 float32 elements.
    [29.97] // Value type is known, so type markers are omitted.
    [31.13]
    [67.0]
    [2.113]
    [23.8889]
// No end marker since a count was specified.
```

---
### Object Examples
Optimized with _count_
```
[{][#][i][3] // An object of 3 name:value pairs.
    [i][3][lat][d][29.976]
    [i][4][long][d][31.131]
    [i][3][alt][d][67.0]
// No end marker since a count was specified.
```
Optimized with both _type_ and _count_
```
[{][$][d][#][i][3] // An object of 3 name:float32-value pairs.
    [i][3][lat][29.976] // Value type is known, so type markers are omitted.
    [i][4][long][31.131]
    [i][3][alt][67.0]
// No end marker since a count was specified.
```

Recommended File Specifiers
------------------------------

For Binary JData files, the recommended file suffix is **`".bjd"`**.
The MIME type for a Binary JData document is **`"application/jdata-binary"`**

Acknowledgement
------------------------------

The BJData spec is derived from the Universal Binary JSON (UBJSON, http://ubjson.org) 
specification (Draft 12) developed by Riyad Kalla and other UBJSON contributors.

The initial version of this MarkDown-formatted specification was derived from the 
documentation included in the [Py-UBJSON](https://github.com/Iotic-Labs/py-ubjson/blob/dev-contrib/UBJSON-Specification.md) 
repository (Commit 5ce1fe7).

This specification was developed as part of the NeuroJSON project (http://neurojson.org) 
with funding support from the US National Institute of Health (NIH) under
grant [U24-NS124027](https://reporter.nih.gov/project-details/10308329).
