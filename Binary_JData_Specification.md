Binary JData: A portable interchange format for complex binary data
============================================================

- **Maintainer**: Qianqian Fang <q.fang at neu.edu>
- **License**: Apache License, Version 2.0
- **Version**: 1 (Draft 4-preview)
- **URL**: https://neurojson.org/bjdata/
- **Status**: Under development
- **Development**: https://github.com/NeuroJSON/bjdata
- **Acknowledgement**: This project is supported by US National Institute of Health (NIH)
  grant [U24-NS124027 (NeuroJSON)](https://neurojson.org)
- **Abstract**:

> The Binary JData (BJData) Specification defines an efficient serialization 
protocol for unambiguously storing complex and strongly-typed binary data found 
in diverse applications. The BJData specification is the binary counterpart
to the JSON format, both of which are used to serialize complex data structures
supported by the JData specification (https://neurojson.org/jdata). The BJData spec is 
derived and extended from the Universal Binary JSON (UBJSON, https://ubjson.org) 
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
  - [Structure-of-arrays (SoA)](#strucutre-of-arrays)
    - [SoA container syntax](#soa_syntax)
    - [Row- and column-major SoA](#row-major_column-major)
    - [Nested containers in schema](#nested_container_in_schema)
    - [N-dimensional SoA](#nd_soa)
    - [SoA example](#nd_soa)
    - [Permitted type markers in SoA schema](#schema_marker_table)
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
JSON formats, such as BSON (Binary JSON, https://bson.org), UBJSON (Universal Binary 
JSON, https://ubjson.org), MessagePack (https://msgpack.org), CBOR (Concise Binary 
Object Representation, [RFC 7049], https://cbor.io) etc. These binary JSON 
counterparts are broadly used in speed-sensitive data processing applications and
address various needs from a diverse range of applications.
 
To better champion findable, accessible, interoperable, and reusable 
([FAIR principle](https://www.nature.com/articles/sdata201618)) data in 
scientific data storage and management, we have created the **NeuroJSON Project**
(https://neurojson.org) to develop a set of open-standards for portable, human-readable 
and high-performance data annotation and serialization aimed towards enabling
neuroimaging researchers, scientific researchers, IT engineers, as well as general 
data users to efficiently annotate and store complex data structures arising 
from diverse applications.
 
The NeuroJSON data sharing framework first converts complex data structures, such as N-D
arrays, trees, tables and graphs, into easy-to-serialize, portable data annotations
via the **JData Specification** (https://github.com/NeuroJSON/jdata) and then serializes 
and stores the annotated JData constructs using widely-supported data formats. 
To balance data portability, readability and efficiency, NeuroJSON defines a 
**dual-interface**: a text-based format **syntactically compatible with JSON**,
and a binary-JSON format to achieve significantly smaller file sizes and faster 
encoding/decoding.
 
The Binary JData (BJData) format is the **official binary interface** for the JData 
Specification. It is derived from the widely supported UBJSON Specification 
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
[Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html).


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
[byte](#value_byte) | 2 bytes | *B* | No | Yes
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
float32/single | Yes | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-1985) | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-1985)
float64/double | Yes | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-1985) | See [IEEE 754 Spec](https://en.wikipedia.org/wiki/IEEE_754-1985)
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
(this is different from UBJSON which does not specify the Endianness of floats).

- `float16` or half-precision values are written in [IEEE 754 half precision floating point 
format](https://en.wikipedia.org/wiki/IEEE_754-2008_revision), which has the following 
structure:
  - Bit 15 (1 bit) - sign
  - Bit 14-10 (5 bits) - exponent
  - Bit 9-0 (10 bits) - fraction (significant)

- `float32` or single-precision values are written in [IEEE 754 single precision floating point 
format](https://en.wikipedia.org/wiki/IEEE_754-1985), which has the following 
structure:
  - Bit 31 (1 bit) - sign
  - Bit 30-23 (8 bits) - exponent
  - Bit 22-0 (23 bits) - fraction (significant)

- `float64` or double-precision values are written in [IEEE 754 double precision floating point 
format](https://en.wikipedia.org/wiki/IEEE_754-1985), which has the following 
structure:
  - Bit 63 (1 bit) - sign
  - Bit 62-52 (11 bits) - exponent
  - Bit 51-0 (52 bits) - fraction (significant)


#### High-Precision
These are encoded as a string and thus are only limited by the maximum string 
size. Values **must** be written out in accordance with the original [JSON 
number type specification](https://json.org).

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
### <a name="value_byte"/>Byte
The `byte` type in BJData is functionally identical to the `uint8` type, 
but semantically is meant to represent a byte and not a numeric value. In
particular, when used as the strong type of an array container it provides
a hint to the parser that an optimized data storage format may be used as
opposed to a generic array of integers.

See also [optimized format](#container_optimized) below.

#### Example
Byte values in JSON:
```json
{
    "binary": [222, 173, 190, 239]
    "val": 123,
}
```

BJData (using block-notation):
```
[{]
    [i][6][binary] [[] [$][B] [#][i][4] [222][173][190][239]
    [i][3][val][B][123]
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
only integers (`i,U,I,u,l,m,L,M`), floating-point numbers (`h,d,D`), char (`C`) and byte (`B`)
are qualified. All zero-length types (`T,F,Z,N`), variable-length types(`S, H`)
and container types (`[,{`) shall not be used in an optimized _type_ header.
This restriction is set to reduce the security risks due to potentials of
buffer-overflow attacks using [zero-length markers](https://github.com/nlohmann/json/issues/2793),
hampered readability and diminished benefit using variable/container
types in an optimized format.

The requirements for _type_ are

- If a _type_ is specified, it **must** be one of `i,U,I,u,l,m,L,M,h,d,D,C,B`.
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

### Optimized binary array
When an array of _type_ `B` is specified the parser shall use an optimized data storage
format to represent binary data where applicable, as opposed to a generic array of integers.
Similarly, explicit binary data should be serialized as such to allow for parsers to
make use of the optimization.

If such a data storage format is not available, an array of integers shall be used.

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

To store an N-dimensional array that is serialized using the **column-major** element
order (as used in MATLAB and FORTRAN), the _count_ marker `#` should be followed by
an array of a single element, which must be a 1-D array of integer type as the
dimensional vector above. Either of the arrays can be in optimized or non-optimized
form. For example, either of the following 

```
[[] [$] [type] [#] [[] [[] [$] [Nx type] [#] [Ndim type] [Ndim] [Nx Ny Nz ...] []]  [a11 a21 a31 ... a21 a22 ...]
  or
[[] [$] [type] [#] [[] [[] [Nx type] [nx] [Ny type] [Ny] [Nz type] [Nz] ... []] []] [a11 a21 a31 ... a21 a22 ...]
```
represents the same column-major N-dimensional array of `type` and size `[Nx, Ny, Nz, ...]`.


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
shall be stored using **row-major** serialized form as
```
 [[] [$][U] [#][[] [$][U][#][3] [2][3][4]
    [1][9][6][0] [2][9][3][1] [8][0][9][6] [6][4][2][7] [8][5][1][2] [3][3][2][6]
```
or **column-major** serialized form as
```
 [[] [$][U] [#][[] [[] [$][U][#][3] [2][3][4] []]
    [1][6][2][8] [8][3][9][4] [9][5][0][3] [6][2][3][1] [9][2][0][7] [1][2][6][6]
```

### Additional rules
- A _count_ **must** be >= 0.
- A _count_ can be specified alone.
- If a _count_ is specified, the container **must not** specify an end-marker.
- A container that specifies a _count_ **must** contain the specified number of 
child elements.
- If a _type_ is specified, it **must** be done so before _count_.
- If a _type_ is specified, a _count_ **must** also be specified. A _type_ 
cannot be specified alone.
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


## <a name="structure-of-arrays"/>Structure-of-Arrays (SoA)

BJData supports **Structure-of-Arrays (SoA)**, as a special type of optimized container 
to store packed object data in either row-major or column-major orders.

### <a name="soa_syntax"/>SoA Container Syntax

#### Core Syntax

```
[[][$]  [{]<schema>[}]  [#]<count>  <payload>    // row-major (interleaved)
[{][$]  [{]<schema>[}]  [#]<count>  <payload>    // column-major (columnar)
```

where:
- `[` or `{` - container type (determines memory layout)
- `$` - optimized type marker  
- `{<schema>}` - payload-less object defining the record structure
- `#` - count marker
- `<count>` - 1D integer OR ND dimension array
- `<payload>` - tightly packed data

#### Schema Definition

The schema is a **payload-less object**: keys followed by type markers only, no values.

```
schema        = '{' 1*(field-def) '}'
field-def     = name type-spec
name          = int-type length string-bytes
type-spec     = fixed-type | bool-type | null-type | string-spec | highprec-spec
              | nested-schema | array-spec
fixed-type    = 'U' | 'i' | 'u' | 'I' | 'l' | 'm' | 'L' | 'M' | 'h' | 'd' | 'D' | 'C' | 'B'
bool-type     = 'T'                        ; boolean (1 byte: T or F in payload)
null-type     = 'Z'                        ; null (0 bytes in payload)
string-spec   = fixed-string | dict-string | offset-string
fixed-string  = 'S' int-type length        ; fixed-size string
dict-string   = '[' '$' 'S' '#' count 1*(string-value)   ; dictionary-based string
offset-string = '[' '$' int-type ']'       ; offset-table-based variable string
highprec-spec = fixed-highprec | dict-highprec | offset-highprec
fixed-highprec= 'H' int-type length        ; fixed-size high-precision number
dict-highprec = '[' '$' 'H' '#' count 1*(highprec-value) ; dictionary-based high-prec
offset-highprec = '[' '$' int-type ']'     ; offset-table-based variable high-prec (same as string)
nested-schema = '{' 1*(field-def) '}'
array-spec    = '[' 1*(type-spec) ']'      ; fixed array with explicit element types
```

**Key rules:**
1. Fixed-length numeric types: `U i u I l m L M h d D C B`
2. `T` in schema means "boolean type" - each value is 1 byte (`T` or `F` marker) in payload
3. `Z` in schema means "null field" - no bytes in payload (placeholder/reserved field)
4. Strings (`S`) and high-precision numbers (`H`) support three storage modes:
   - **Fixed-length:** `S <int-type> <length>` or `H <int-type> <length>`
   - **Dictionary-based:** `[$S#<count><str1><str2>...` or `[$H#<count><val1><val2>...`
   - **Offset-table-based:** `[$<int-type>]`
5. Nested objects `{...}` are allowed if all fields use supported types
6. No optimized containers can be used inside the schema, except in the case of serving as
   dictionary/offset-table markers for variable-length strings, as described in #4 above
7. `F` and `N` are not used in schema (use `T` for boolean, `Z` for null)

---

### <a name="variable_length_strings"/>Variable and fixed-length string storage

#### Mode 1: Fixed-length storage (`S`/`H` with length)

In a **schema context**, `S` and `H` followed by an integer define fixed-length strings or high-precision numbers:
```
{ i4 name S i 16 }       ; "name" is a 16-byte fixed string
{ i5 value H i 32 }      ; "value" is a 32-byte fixed high-precision number
```

In the payload, each record contributes exactly the specified bytes - no length prefix. 
Strings shorter than the length are right-padded with null bytes (0x00).

**Use case:** Strings with known maximum length (codes, IDs, short labels).

---

#### Mode 2: Dictionary-based storage (`[$S#<n>...` or `[$H#<n>...`)

A dictionary for mapping string-value rows/columns should be indicated by
a payload-less optimized string-array.

**Use case:** Repeated/categorical string values with low cardinality.

**Schema syntax:**
```
[$S#<count><str1><str2>...
[$H#<count><val1><val2>...
```

where each string/value is encoded as a standard BJData string or high-precision number 
(with length prefix). No closing `]` is needed because the count is specified.

**Example schema:**
```
{
  i6 status [$S#i 3                    ; dictionary with 3 string values
    i 6 active                         ; index 0: "active"
    i 8 inactive                       ; index 1: "inactive"  
    i 7 pending                        ; index 2: "pending"
}
```

**Payload encoding:** Each record stores a single integer index referencing the dictionary.
The index type is automatically determined as the smallest unsigned integer type that can 
represent the dictionary size:
- count ≤ 255: `U` (uint8, 1 byte)
- count ≤ 65535: `u` (uint16, 2 bytes)
- count ≤ 4294967295: `m` (uint32, 4 bytes)
- otherwise: `M` (uint64, 8 bytes)

**Benefits:**
- Excellent compression for low-cardinality categorical data
- O(1) lookup for string values
- Payload remains fixed-size per record

---

#### Mode 3: Offset-table-based storage (`[$<type>]`)

An offset-table based storage is used for storing string vectors of variable lengths.
It first concatenates all strings into a single linear buffer, and assigns an integer as
the offset from the begining of the buffer for each string element. The use of 
offset-table should be indicated by an payload-less optimized array containing only the
optimized type `[$<type>]`.


**Use case:** Diverse strings with highly variable lengths (names, descriptions, free text).

**Schema syntax:**
```
[$<offset-type>]
```

Where `<offset-type>` is an integer type (`i`, `U`, `I`, `u`, `l`, `m`, `L`, `M`) 
specifying the byte-offset type stored in the payload.

**Example schema:**
```
{
  i2 id m                    ; uint32 (4 bytes in payload)
  i4 name [$l]               ; variable string with int32 offsets
  i5 value d                 ; float64 (8 bytes in payload)
}
```

**Storage structure:**

The offset-table-based string field stores an offset index in the fixed payload area.
After all record payloads, an offset table and concatenated string buffer are appended:

```
┌─────────────────────────────────────────────────────────────────┐
│ Schema Header                                                   │
├─────────────────────────────────────────────────────────────────┤
│ Fixed-size payload (N records)                                  │
│   - Each string field position stores a sequential index (0..N-1)│
│   - Other fields store actual values                            │
├─────────────────────────────────────────────────────────────────┤
│ Offset Table: (N+1) offsets of <offset-type>                    │
│   [0, end1, end2, ..., end_N]                                    │
├─────────────────────────────────────────────────────────────────┤
│ String Buffer: concatenated strings (no length prefixes)        │
│   str1 ∥ str2 ∥ str3 ∥ ... ∥ str_N                               │
└─────────────────────────────────────────────────────────────────┘
```

**Decoding string i:**
```
offset_start = offset_table[i]
offset_end = offset_table[i+1]
string_i = string_buffer[offset_start:offset_end]
```

**Multiple variable-length fields:** When a schema contains multiple offset-table-based 
fields, their offset tables and string buffers are appended in schema field order.

**Empty strings:** Represented by consecutive identical offsets in the offset table.

**Benefits:**
- Efficient for highly variable string lengths
- No wasted padding bytes
- Random access via offset table
- String buffer can be memory-mapped

---

### Boolean type (`T`)

In normal BJData, `T` and `F` are zero-length value markers:
```
T                        ; true (no payload)
F                        ; false (no payload)
```

In a **schema context**, `T` means "boolean type" - a 1-byte field:
```
{ i6 active T }          ; "active" is a boolean field
```

In the payload, each boolean value is stored as a single byte: `T` (0x54) for true, 
`F` (0x46) for false.

---

### Null type (`Z`)

In a **schema context**, `Z` means "null/placeholder field" with **zero bytes** in payload:
```
{ 
  i2 id m                ; uint32 (4 bytes)
  i8 reserved Z          ; placeholder (0 bytes)
  i4 data d              ; float64 (8 bytes)
}
```

This is useful for:
- Reserved fields for future expansion
- Marking fields that exist in the schema but carry no data
- Sparse structures where some fields are always null

---

### <a name="row-major_column-major"/>Row-Major vs Column-Major Layout

Using existing container markers:

| Syntax | Layout | Description |
|--------|--------|-------------|
| `[$` | **Row-major (Interleaved)** | Array of records - each complete record stored sequentially |
| `{$` | **Column-major (Columnar)** | Object of arrays - all values of each field stored together |

#### Row-Major: `[$`

```
[$  {<schema>}  #<count>  <interleaved-payload>
```

Payload order: `<record₁><record₂><record₃>...`

**Example:** 3 particles with `{x:float64, y:float64, id:uint32, active:bool}`
```
[ $ { i1 x d  i1 y d  i2 id m  i6 active T } # i 3
  <x₁:8><y₁:8><id₁:4><active₁:1>  <x₂:8><y₂:8><id₂:4><active₂:1>  ...
```
Payload: 3 × 21 bytes = 63 bytes, interleaved

#### Column-major layout: `{$`

```
{$  {<schema>}  #<count>  <columnar-payload>
```

Payload order: `<all field₁ values><all field₂ values>...`

**Example:** Same 3 particles
```
{ $ { i1 x d  i1 y d  i2 id m  i6 active T } # i 3
  <x₁:8><x₂:8><x₃:8>  <y₁:8><y₂:8><y₃:8>  <id₁:4><id₂:4><id₃:4>  <T><F><T>
```
Payload: (3×8) + (3×8) + (3×4) + (3×1) = 63 bytes, columnar

**Why this design:**
- `[` = "ordered sequence" → sequence of records (row-major)
- `{` = "named fields" → fields as separate arrays (column-major)
- No new markers needed

---

### <a name="nested_container_in_schema"/>Nested Containers in Schema

#### Nested objects

```
{
  i4 name S i 32           ; 32-byte fixed string
  i8 position {            ; nested object (24 bytes total)
    i1 x d
    i1 y d  
    i1 z d
  }
  i6 active T              ; boolean (1 byte)
  i5 flags U               ; uint8 (1 byte)
}
```

Record size: 32 + 24 + 1 + 1 = 58 bytes

#### Fixed-length arrays in schema

Use array syntax with repeated type markers:

```
{
  i2 id m                  ; uint32 (4 bytes)
  i3 pos [d d d]           ; array of 3 float64 (24 bytes)
  i5 color [U U U U]       ; array of 4 uint8 (4 bytes)
  i5 flags [T T T T]       ; array of 4 booleans (4 bytes)
}
```

Record size: 4 + 24 + 4 + 4 = 36 bytes

For longer arrays, repeat the type marker:
```
{
  i4 data [d d d d d d d d d d]   ; array of 10 float64 (80 bytes)
}
```

#### Nested Arrays with Mixed Types

```
{
  i6 vertex [d d d]        ; position: 3 float64 (24 bytes)
  i6 normal [h h h]        ; normal: 3 float16 (6 bytes)
  i5 color [U U U U]       ; RGBA: 4 uint8 (4 bytes)
  i7 visible T             ; visibility: boolean (1 byte)
}
```

Record size: 24 + 6 + 4 + 1 = 35 bytes

---

### <a name="nd_soa"/>N-Dimensional SoA

Both `[$` and `{$` support ND dimensions:

```
[$  {<schema>}  #[<dim₁> <dim₂> ...]  <payload>
{$  {<schema>}  #[<dim₁> <dim₂> ...]  <payload>
```

**Example:** 4×3 grid of particles (row-major)
```
[ $ { i1 x d  i1 y d  i6 active T } # [ i 4  i 3 ]
  <12 records in row-major order>
```

Total: 12 records × 17 bytes = 204 bytes

---

### <a name="soa_example"/>SoA Examples

#### Example 1: Fixed-Length Fields Only

**Data:** 2 sensors

```json
[
  {"id": 1, "pos": {"x": 1.0, "y": 2.0}, "val": [0.1, 0.2, 0.3], "on": true},
  {"id": 2, "pos": {"x": 3.0, "y": 4.0}, "val": [0.4, 0.5, 0.6], "on": false}
]
```

**Row-major encoding:**
```
Byte  Hex   Meaning
----  ----  -------
0     5B    [ (array-style SoA = row-major)
1     24    $
2     7B    { (schema start)
3     69    i (int8 key length)
4     02    2
5-6   6964  "id"
7     6D    m (uint32)
8     69    i
9     03    3
10-12 706F73 "pos"
13    7B    { (nested object start)
14    69    i
15    01    1
16    78    "x"
17    64    d (float64)
18    69    i
19    01    1
20    79    "y"
21    64    d (float64)
22    7D    } (nested object end)
23    69    i
24    03    3
25-27 76616C "val"
28    5B    [ (array start)
29    64    d (float64)
30    64    d
31    64    d
32    5D    ] (array end)
33    69    i
34    02    2
35-36 6F6E  "on"
37    54    T (boolean type)
38    7D    } (schema end)
39    23    #
40    69    i
41    02    2 (count = 2)
--- PAYLOAD (2 records × 45 bytes) ---
42-45       id₁: uint32 = 1
46-53       pos.x₁: float64 = 1.0
54-61       pos.y₁: float64 = 2.0
62-69       val₁[0]: float64 = 0.1
70-77       val₁[1]: float64 = 0.2
78-85       val₁[2]: float64 = 0.3
86          on₁: T (true)
87-90       id₂: uint32 = 2
91-98       pos.x₂: float64 = 3.0
99-106      pos.y₂: float64 = 4.0
107-114     val₂[0]: float64 = 0.4
115-122     val₂[1]: float64 = 0.5
123-130     val₂[2]: float64 = 0.6
131         on₂: F (false)
```

Record size: 4 + 8 + 8 + 24 + 1 = 45 bytes  
Total: 42 (header) + 90 (payload) = 132 bytes

---

#### Example 2: Variable-Length String Fields

**Data:** 3 users with variable-length names and categorical status

```json
[
  {"id": 1, "status": "active", "name": "Alice", "code": "U001"},
  {"id": 2, "status": "pending", "name": "Bob", "code": "U002"},
  {"id": 3, "status": "active", "name": "Dr. Christopher Williams", "code": "U003"}
]
```

**Schema (block notation):**
```
[{]
  [i][2][id][m]                        ; uint32 (4 bytes)
  [i][6][status][$][S][#][i][3]        ; dictionary with 3 values
    [i][6][active]                     ; index 0
    [i][8][inactive]                   ; index 1
    [i][7][pending]                    ; index 2
  [i][4][name][$][l][]]                ; offset-based variable string (int32 offsets)
  [i][4][code][S][i][4]                ; fixed 4-byte string
[}]
```

**Record payload size:** 4 (id) + 1 (status index) + 4 (name offset index) + 4 (code) = 13 bytes

**Memory layout (row-major):**
```
┌──────────────────────────────────────────────────────────────┐
│ HEADER (schema + count = 3)                                  │
├──────────────────────────────────────────────────────────────┤
│ Record 1: [id=1] [status_idx=0] [name_idx=0] [code="U001"]   │  13 bytes
│ Record 2: [id=2] [status_idx=2] [name_idx=1] [code="U002"]   │  13 bytes
│ Record 3: [id=3] [status_idx=0] [name_idx=2] [code="U003"]   │  13 bytes
├──────────────────────────────────────────────────────────────┤
│ Name Offset Table (4 × int32):                               │
│   [0, 5, 8, 32]                                              │  16 bytes
├──────────────────────────────────────────────────────────────┤
│ Name String Buffer:                                          │
│   "AliceBobDr. Christopher Williams"                         │  32 bytes
└──────────────────────────────────────────────────────────────┘
```

Total: header + 39 (records) + 16 (offset table) + 32 (strings) = header + 87 bytes

---

### <a name="schema_marker_table"/>Permitted Type Markers in SoA Schema

| Marker | In Schema Means | Payload Size | Notes |
|--------|-----------------|--------------|-------|
| `U` | uint8 | 1 byte | |
| `i` | int8 | 1 byte | |
| `u` | uint16 | 2 bytes | |
| `I` | int16 | 2 bytes | |
| `l` | int32 | 4 bytes | |
| `m` | uint32 | 4 bytes | |
| `L` | int64 | 8 bytes | |
| `M` | uint64 | 8 bytes | |
| `h` | float16 | 2 bytes | |
| `d` | float32 | 4 bytes | |
| `D` | float64 | 8 bytes | |
| `C` | char | 1 byte | |
| `B` | byte | 1 byte | |
| `T` | boolean | 1 byte | Payload: `T` or `F` marker |
| `Z` | null/placeholder | 0 bytes | No payload |
| `S <int> <len>` | fixed string | `len` bytes | No length prefix in payload |
| `H <int> <len>` | fixed high-precision | `len` bytes | No length prefix in payload |
| `[$S#<n>...` | dictionary string | 1-8 bytes | Index into embedded dictionary |
| `[$H#<n>...` | dictionary high-prec | 1-8 bytes | Index into embedded dictionary |
| `[$<type>]` | offset-based string/H | sizeof(type) | Offset table + buffer appended |
| `{...}` | nested object | sum of fields | All fields must be supported types |
| `[...]` | fixed array | sum of elements | Explicit element types listed |


Recommended File Specifiers
------------------------------

For Binary JData files, the recommended file suffix is **`".bjd"`**.
The MIME type for a Binary JData document is **`"application/jdata-binary"`**

Acknowledgement
------------------------------

The BJData spec is derived from the Universal Binary JSON (UBJSON, https://ubjson.org) 
specification (Draft 12) developed by Riyad Kalla and other UBJSON contributors.

The initial version of this MarkDown-formatted specification was derived from the 
documentation included in the [Py-UBJSON](https://github.com/Iotic-Labs/py-ubjson/blob/dev-contrib/UBJSON-Specification.md) 
repository (Commit 5ce1fe7).

This specification was developed as part of the NeuroJSON project (https://neurojson.org) 
with funding support from the US National Institute of Health (NIH) under
grant [U24-NS124027](https://reporter.nih.gov/project-details/10308329).
