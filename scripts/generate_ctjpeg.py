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

    mb.macro("JPEG_LIB_VERSION").include()

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
        mb.typedef(typedef).include(export=False)
    jpeg_header.structs().include()

    # Create a declaration for the union type of one field
    # mb.struct("jpeg_error_mgr").field("msg_parm").type.insert_declaration("msg_parm_union_t")
    jpeg_error_mgr = mb.struct("jpeg_error_mgr")
    msg_parm_union_t = jpeg_error_mgr.field("msg_parm").field_type()
    # Nameless inline union needs a name before it can be declared
    msg_parm_union_t.rename("_MsgParmUnion")
    msg_parm_union_t.include(export=False, before=jpeg_error_mgr)

    # Manual forward declaration for jpeg_error_mgr
    jpeg_common_struct = mb.struct("jpeg_common_struct")
    jpeg_error_mgr.include_forward(export=False, before=jpeg_common_struct)
    mb.struct("jpeg_memory_mgr").include_forward(before=jpeg_common_struct)
    mb.struct("jpeg_progress_mgr").include_forward(before=jpeg_common_struct)
    jpeg_compress_struct = mb.struct("jpeg_compress_struct")
    mb.struct("jpeg_destination_mgr").include_forward(before=jpeg_compress_struct)

    # Forward declarations without definitions
    for field_name in [
        "cconvert",
        "coef",
        "downsample",
        "entropy",
        "fdct",
        "main",
        "marker",
        "master",
        "prep",
    ]:
        field_type = jpeg_compress_struct.field(field_name).field_type()
        field_type.include(export=False, before=jpeg_compress_struct)

    jpeg_decompress_struct = mb.struct("jpeg_decompress_struct")
    for field_name in [
        "cconvert",
        "coef",
        "cquantize",
        "entropy",
        "idct",
        "inputctl",
        "main",
        "marker",
        "master",
        "post",
        "upsample",
    ]:
        field_type = jpeg_decompress_struct.field(field_name).field_type()
        field_type.include(export=False, before=jpeg_decompress_struct)

    mb.struct("jpeg_source_mgr").include_forward(before=mb.struct("jpeg_decompress_struct"))
    mb.struct("jpeg_marker_struct").include_forward(before=mb.typedef("jpeg_saved_marker_ptr"))
    mb.struct("jpeg_compress_struct").include_forward(before=mb.typedef("j_compress_ptr"))
    mb.struct("jpeg_decompress_struct").include_forward(before=mb.typedef("j_decompress_ptr"))

    jvirt_sarray_ptr = mb.typedef("jvirt_sarray_ptr")
    jvirt_sarray_ptr.base_type().include_forward(before=jvirt_sarray_ptr)
    jvirt_barray_ptr = mb.typedef("jvirt_barray_ptr")
    jvirt_barray_ptr.base_type().include_forward(before=jvirt_barray_ptr)

    ct = CTypesCodeGenerator(mb)
    with open("../ctj/jpeglib.py", "w") as output:
        ct.write_module(output)


if __name__ == "__main__":
    main()
