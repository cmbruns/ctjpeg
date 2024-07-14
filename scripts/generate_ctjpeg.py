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
            """) + jpeglib_contents),
        ),
    )
    # mb.typedef("JBLOCK").include()
    mb.typedefs(lambda c: c.location.file.name == jpeglib_path).include()
    # Supply missing dependencies outside the header
    for typedef in [
        "JDIMENSION",
        "JOCTET",
        "JSAMPLE",
        "J12SAMPLE",
        "J16SAMPLE",
        "JCOEF",
        "UINT8",
        "UINT16",
        "boolean",
        "size_t",
    ]:
        mb.typedef(typedef).include()
    mb.structs(lambda c: c.location.file.name == jpeglib_path).include()
    # mb.struct("JQUANT_TBL").include()
    # mb.struct("jpeg_decompress_struct").include()
    ct = CTypesCodeGenerator(mb)
    with open("../ctj/jpeglib.py", "w") as output:
        ct.write_module(output)


if __name__ == "__main__":
    main()
