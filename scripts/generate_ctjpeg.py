from wraptor import CTypesCodeGenerator, ModuleBuilder


def main():
    header_file = "C:/Users/cmbruns/Documents/git/libjpeg-turbo/jpeglib.h"
    mb = ModuleBuilder(file_paths=[header_file,])
    mb.typedef("JBLOCK").include()
    mb.typedefs(lambda c: c.location.file.name == header_file).include()
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
    ]:
        mb.typedef(typedef).include()
    mb.structs(lambda c: c.location.file.name == header_file).include()
    # mb.struct("JQUANT_TBL").include()
    # mb.struct("jpeg_decompress_struct").include()
    ct = CTypesCodeGenerator(mb)
    with open("../ctj/jpeglib.py", "w") as output:
        ct.write_module(output)


if __name__ == "__main__":
    main()
