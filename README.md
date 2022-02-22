![](https://neurojson.org/wiki/upload/neurojson_banner_long.png)

# Binary JData Format Specification Development Guide

We use this repository to gather feedback from the community regarding the 
["Binary JData Format Specification"](Binary_JData_Specification.md), or 
Binary JData (**BJData**) format. Such feedback is crucial to finalize this file 
specification and help improve it in the future once disseminated.

The latest version of the BJData specification can be found in the file named 
[Binary_JData_Specification.md](Binary_JData_Specification.md). The specification is written
in the [Markdown format](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet) 
for convenient editing and version control.

This specification was derived from the Universal Binary JSON (UBJSON) Specification
[Draft 12](https://github.com/ubjson/universal-binary-json/tree/master/spec12)
developed by Riyad Kalla and other UBJSON contributors. The MarkDown version 
of this specification was derived from the documentation included in the 
[Py-ubjson](https://github.com/Iotic-Labs/py-ubjson/blob/dev-contrib/UBJSON-Specification.md)
repository (Commit 5ce1fe7). **The BJData format is no longer backward compatible with UBJSON.**

Libraries that support this specification include
- Python: **pybj** (PIP:  https://pypi.org/project/bjdata/, Github: https://github.com/NeuroJSON/pybj)
- MATLAB/Octave: **JSONLab** (Debian/Ubuntu/Fedora: `sudo apt-get install octave-jsonlab`, Github: https://github.com/fangq/jsonlab)
- C: **ubj** (Github: https://github.com/fangq/ubj)
- C++: **JSON for Modern C++** (with this patch https://github.com/nlohmann/json/pull/3336)

**Acknowledgement**: This specification was developed as part of the NeuroJSON project
(http://neurojson.org), with funding support from the US National Institute of Health (NIH) under
grant [U24-NS124027](https://reporter.nih.gov/project-details/10308329) (PI: [Qianqian Fang](http://fanglab.org)).

## How to participate

You can use a number of methods to provide your feedback to the working 
draft of this file specification, including

- [Create an "Issue"](https://github.com/NeuroJSON/bjdata/issues)
  - This is the most recommended method to provide detailed feedback or 
    discussion. An "Issue" in github is highly versatile. One can ask a 
    question, report a bug, provide a feature request, or simply propose
    general discussions. Please use URLs or keywords to link your discussion 
    to a specific line/section/topic in the document.
- [Write short comments on Request for Comments (RFC) commits](https://github.com/NeuroJSON/bjdata/commit/2f352210f928af9efd89f47c845d8e68c5b9bbc2)
  - A milestone version of the specification will be associated with an
    RFC (Request for comments) commit (where the entire file is removed
    and re-added so that every line appears in such commit). One can
    write short comments as well as post replies on this RFC page. 
  - The latest RFC commit is based on **Version 1 Draft-2**. Please use
    [this link](https://github.com/NeuroJSON/bjdata/commit/2f352210f928af9efd89f47c845d8e68c5b9bbc2) to comment.
  - To add a comment, you need to first register a github account, and then 
    browse the above RFC page. When hovering your cursor over each line, a 
    "plus" icon is displayed, clicking it will allow one to comment on a 
    specific line (or reply to other's comments).
  - The RFC page can get busy if too many comments appear. Please consider 
    using the [Issues section](https://github.com/NeuroJSON/bjdata/issues) if this happens.
  - One can browse the commit history of the specification document. If
    anyone is interested in commenting on a particular updated, you can also
    comment on any of the commit page using the same method.
- [Use the JData mailing list](https://groups.google.com/forum/#!forum/openjdata)
  - You may send your comments to the jdata mailing list (openjdata at googlegroups.com). 
    Subscribers will discuss by emails, and if a motion is reached, proposals
    will be resubmitted as an Issue, and changes to the specification will be
    associated with this issue page.

For anyone who wants to contribute to the writing or revision of this document,
please follow the below steps

- Fork this repository and make updates, then create a pull-request
  - Please first register an account on github, then, browse the 
    [JData repository](https://github.com/NeuroJSON/bjdata);
    on the top-right of this page, find and click the "Fork" button.
  - once you fork the JData project to your own repository, you may edit the
    files in your browser directly, or download to your local folder, and 
    edit the files using a text editor;
  - once your revision is complete, please "commit" and "push" it to your forked
    git repository. Then you should create a pull-request (PR) against the upstream
    repository (i.e., `NeuroJSON/bjdata`). Please select "Compare cross forks" and 
    select `"NeuroJSON/bjdata"` as "base fork". Please write a descriptive title for
    your pull-request. The project maintainer will review your updates
    and choose to merge to the upstream files or request revision from you.
    
