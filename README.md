![](https://neurojson.org/wiki/upload/neurojson_banner_long.png)

# Binary JData Format Specification Development Guide

We use this repository to gather feedback from the community regarding the 
["Binary JData Format Specification"](Binary_JData_Specification.md), or 
Binary JData (**BJData**) format. Such feedback is crucial to finalize this file 
specification and help improve it in future releases.

The latest version of the BJData specification can be found in the file
[Binary_JData_Specification.md](Binary_JData_Specification.md). The specification is written
in [Markdown format](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
for convenient editing and version control.

This specification was derived from the Universal Binary JSON (UBJSON) Specification
[Draft 12](https://github.com/ubjson/universal-binary-json/tree/master/spec12)
developed by Riyad Kalla and other UBJSON contributors. The Markdown version
of this specification was derived from the documentation included in the
[Py-ubjson](https://github.com/Iotic-Labs/py-ubjson/blob/dev-contrib/UBJSON-Specification.md)
repository (Commit 5ce1fe7). **The BJData format is no longer backward compatible with UBJSON.**

Libraries that support this specification include
- Python: **pybj** (PIP:  https://pypi.org/project/bjdata/, GitHub: https://github.com/NeuroJSON/pybj)
- MATLAB/Octave: **JSONLab** (Debian/Ubuntu/Fedora: `sudo apt-get install octave-jsonlab`, GitHub: https://github.com/NeuroJSON/jsonlab)
- C: **ubj** (GitHub: https://github.com/NeuroJSON/ubj)
- C++: **JSON for Modern C++** (v3.11.0 or later) (https://github.com/nlohmann/json/)
- JavaScript: **bjd** (npm: https://www.npmjs.com/package/bjd, GitHub: https://github.com/NeuroJSON/js-bjdata)
- Dart: **bjdata** (pub.dev: https://pub.dev/packages/bjdata, GitHub: https://github.com/nebkat/dart-bjdata)

**Acknowledgement**: This specification was developed as part of the NeuroJSON project
(http://neurojson.org), with funding support from the US National Institute of Health (NIH) under
grant [U24-NS124027](https://reporter.nih.gov/project-details/10308329) (PI: [Qianqian Fang](http://fanglab.org)).


## What is BJData

BJData is a binary JSON format. It is similar to JSON but can store strongly-typed binary data.
The BJData format improves upon the widely supported UBJSON (https://ubjson.org) format by adding
the following key features:

- added 4 new data types previously missing from UBJSON, including `[u] - uint16`, `[m] - uint32`, 
  `[M] - uint64` and `[h] - half/float16`,
- first among all binary JSON formats to support **packed N-dimensional arrays (ndarray)** — a data
  type that is of great importance to the scientific community,
- adopted **Little-Endian** as the default byte-order, as opposed to Big-Endian for UBJSON/MessagePack/CBOR,
- only fixed-length data types are allowed in optimized container types (`$`), which means
  `[{SHTFTZN` cannot follow `$`, but `UiuIlmLMhdDCB` are allowed

![](./images/BJData_Diagram.png)


## How to participate

You can use a number of methods to provide your feedback on the working 
draft of this specification, including

- [Create an "Issue"](https://github.com/NeuroJSON/bjdata/issues)
  - This is the most recommended method to provide detailed feedback or 
    discussion. An "Issue" in GitHub is highly versatile: one can ask a 
    question, report a bug, submit a feature request, or start a general
    discussion. Please use URLs or keywords to link your discussion 
    to a specific line, section, or topic in the document.
- [Comment on a release](https://github.com/NeuroJSON/bjdata/releases)
  - Stable releases are tagged and listed on the
    [releases page](https://github.com/NeuroJSON/bjdata/releases).
    To add a comment, please use the
    [Issues section](https://github.com/NeuroJSON/bjdata/issues).
  - You can also browse the commit history of the specification. To comment
    on a specific change, use the Issues section and reference the commit.
- [Use NeuroJSON Forum](https://github.com/orgs/NeuroJSON/discussions)
  - You may send your comments to the NeuroJSON GitHub forum. You may report
    bugs, request new features, or submit new datasets.

For anyone who wants to contribute to the writing or revision of this document,
please follow the steps below:

- Fork this repository and make updates, then create a pull request
  - Please first register an account on GitHub, then browse the 
    [BJData Spec repository](https://github.com/NeuroJSON/bjdata);
    on the top-right of the page, find and click the "Fork" button.
  - Once you fork the project to your own repository, you may edit the
    files in your browser directly, or download to your local folder and 
    edit them using a text editor.
  - Once your revision is complete, please "commit" and "push" it to your forked
    git repository. Then create a pull request (PR) against the upstream
    repository (i.e., `NeuroJSON/bjdata`). Please select "Compare cross forks" and 
    select `"NeuroJSON/bjdata"` as "base fork". Please write a descriptive title for
    your pull request. The project maintainer will review your updates
    and either merge them or request revisions.
