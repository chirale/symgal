symgal
======

Symlink gallery: recurse subdirectories and link sane images.

This tool checks a source directory with all its subdirectories searching 
for valid image files. If a valid image is found, a symbolic link is created 
into the destination directory.

* Windows only
* Run as administrator.

Symbolic links requires SeCreateSymbolicLinkPrivilege. You have to give this 
permission to a broader range of users or to run SymGal as Administrator.
Learn more: http://superuser.com/a/125981

Warning: Alpha stage, loading directory with many files could take very long.
