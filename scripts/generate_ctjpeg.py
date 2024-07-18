import inspect

from wraptor import CTypesCodeGenerator, ModuleBuilder

from ctj.resources import resource_filename, resource_string


def main():
    jpeglib_path = resource_filename("ctj", "jpeglib.h")
    jpeglib_contents = resource_string("ctj", "jpeglib.h")
    mb = ModuleBuilder(
        path=jpeglib_path,
        # jpeglib.h needs to include stdio.h to get definition for size_t
        unsaved_files=(
            (jpeglib_path, inspect.cleandoc(f"""
                #include "stdio.h"
            """) + "\n" + jpeglib_contents),
        ),
    )
    jpeg_header = mb.in_header(jpeglib_path)
    jpeg_header.typedefs().include()
    jpeg_header.macros().include()
    jpeg_header.enums().include()
    # Supply missing dependencies outside the header
    for typedef in [
        "boolean",
        "J12SAMPLE",
        "J16SAMPLE",
        "JCOEF",
        "JDIMENSION",
        "JOCTET",
        "JSAMPLE",
        "size_t",
        "UINT8",
        "UINT16",
    ]:
        mb.typedef(typedef).include()
    jpeg_header.structs().include()
    # Create a declaration for the union type of one field
    # mb.struct("jpeg_error_mgr").field("msg_parm").type.insert_declaration("msg_parm_union_t")
    foo = mb.struct("jpeg_error_mgr").field("msg_parm").type.get_declaration()
    ct = CTypesCodeGenerator(mb)
    with open("../ctj/jpeglib.py", "w") as output:
        ct.write_module(output)


if __name__ == "__main__":
    main()
