#ifndef UTIL.H

#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint16_t bfType;            // File type signature 'BM'
    uint32_t bfSize;            // File size in bytes
    uint16_t bfReserved1;       // Reserved field
    uint16_t bfReserved2;       // Reserved field
    uint32_t bfOffBits;         // Offset to pixel data
} File_Header;

typedef struct {
    uint32_t biSize;            // Header size (40 bytes)
    int32_t  biWidth;           // Image width
    int32_t  biHeight;          // Image height (positive = bottom-up)
    uint16_t biPlanes;          // Number of color planes (1)
    uint16_t biBitCount;        // Bits per pixel (24)
    uint32_t biCompression;     // Compression type (0 = no compression)
    uint32_t biSizeImage;       // Image size in bytes
    int32_t  biXPelsPerMeter;   // Horizontal resolution
    int32_t  biYPelsPerMeter;   // Vertical resolution
    uint32_t biClrUsed;         // Colors in color palette
    uint32_t biClrImportant;    // Important colors
} Info_Header;

typedef struct {
    int width;              // Image width in pixels
    int height;             // Image height in pixels
    int channels;           // Number of channels (3 for BGR)
    int stride;             // Bytes per row (width * channels)
    unsigned char *pixels;    // Image data array (top-down storage)
} Image;

 /**
 * @brief Utility to read an image as file.
 *
 * @pre Image must be of type BMP.
 * @param filename The Filename.
 * @param image The image.
 * @return '0' for success, '1' for failure.
 */
int readImage(const char *filename, Image *image);


#endif