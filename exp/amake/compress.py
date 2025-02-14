import AssetForge

from pathlib import Path
from typing import List

import zlib

class CompressTool(AssetForge.AssetTool):
    """

    #include <iostream>
    #include <stdexcept>
    #include <sys/mman.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <cstring>
    #include <zlib.h>
    #include <cstdlib>

    /// Decompresses a memory‐mapped file whose first 4 bytes are an unsigned int
    /// indicating the size of the compressed data. Returns a pointer to a buffer
    /// containing the decompressed data (caller must free it with free()) and sets
    /// decompressedSize to the number of decompressed bytes.
    void* decompress_mapped_file(const char* filename, size_t &decompressedSize) {
        // Open the file.
        int fd = open(filename, O_RDONLY);
        if (fd < 0) {
            throw std::runtime_error("Could not open file");
        }

        // Get file size.
        struct stat sb;
        if (fstat(fd, &sb) < 0) {
            close(fd);
            throw std::runtime_error("fstat failed");
        }
        size_t fileSize = sb.st_size;
        if (fileSize < sizeof(unsigned int)) {
            close(fd);
            throw std::runtime_error("File too small to contain header");
        }

        // Memory-map the file.
        void* fileData = mmap(NULL, fileSize, PROT_READ, MAP_PRIVATE, fd, 0);
        close(fd);
        if (fileData == MAP_FAILED) {
            throw std::runtime_error("mmap failed");
        }
        const unsigned char* mappedBytes = static_cast<const unsigned char*>(fileData);
        const unsigned char* compData = mappedBytes

        // Set up zlib stream for decompression.
        z_stream strm;
        std::memset(&strm, 0, sizeof(strm));
        strm.next_in = const_cast<Bytef*>(compData);
        strm.avail_in = fileSize;

        if (inflateInit(&strm) != Z_OK) {
            munmap(fileData, fileSize);
            throw std::runtime_error("inflateInit failed");
        }

        // Allocate an output buffer.
        // In practice, you might store the uncompressed size in the header.
        size_t outputBufferSize = fileSize * 10; // Arbitrary guess; adjust as needed.
        unsigned char* outBuffer = static_cast<unsigned char*>(std::malloc(outputBufferSize));
        if (!outBuffer) {
            inflateEnd(&strm);
            munmap(fileData, fileSize);
            throw std::bad_alloc();
        }
        strm.next_out = outBuffer;
        strm.avail_out = outputBufferSize;

        // Decompress.
        int ret = inflate(&strm, Z_FINISH);
        if (ret != Z_STREAM_END) {
            std::free(outBuffer);
            inflateEnd(&strm);
            munmap(fileData, fileSize);
            throw std::runtime_error("inflate failed or output buffer too small");
        }
        decompressedSize = outputBufferSize - strm.avail_out;
        inflateEnd(&strm);

        // Unmap the file.
        munmap(fileData, fileSize);

        return outBuffer;
    }
    
    """
    
    def check_match(self, file_path: Path) -> bool:
        return file_path.suffixes.count(".bin") == 1 and file_path.suffixes[-1] == ".bin"

    def define_dependencies(self, file_path: Path) -> List[Path]:
        return []

    def define_outputs(self, file_path: Path) -> List[Path]:
        # Return the same relative path so that the output file in the output folder will have the same structure.
        return [self.output_folder / self.relative_path(file_path.with_name(file_path.name + ".z"))]
    
    def build(self, file_path: Path) -> None:
        input_path = file_path
        output_path = self.output_folder / self.relative_path(file_path.with_name(file_path.name + ".z"))

        with open(input_path, "rb") as fin:
            data = fin.read()

        with open(input_path, "rb") as fin:
            data = fin.read()
        
        compressed_data = zlib.compress(data)
    
        # Write the compressed data to a file
        with open(output_path, "wb") as fout:
            fout.write(compressed_data)
