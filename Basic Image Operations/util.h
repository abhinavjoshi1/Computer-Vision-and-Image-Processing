#ifndef UTIL_H

#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint16_t bf_type;            // File type signature 'BM'
    uint32_t bf_size;            // File size in bytes
    uint16_t bf_reserved1;       // Reserved field
    uint16_t bf_reserved2;       // Reserved field
    uint32_t bf_offbits;         // Offset to pixel data
} BITMAPFILEHEADER;

typedef struct {
    uint32_t bi_size;            // Header size (40 bytes)
    int32_t  bi_width;           // Image width
    int32_t  bi_height;          // Image height (positive = bottom-up)
    uint16_t bi_planes;          // Number of color planes (1)
    uint16_t bi_bit_count;        // Bits per pixel (24)
    uint32_t bi_compression;     // Compression type (0 = no compression)
    uint32_t bi_size_image;       // Image size in bytes
    int32_t  bi_xpels_permeter;   // Horizontal resolution
    int32_t  bi_ypels_permeter;   // Vertical resolution
    uint32_t bi_clr_used;         // Colors in color palette
    uint32_t bi_clrimportant;    // Important colors
} BITMAPINFOHEADER;

typedef struct {
    int width;              // Image width in pixels
    int height;             // Image height in pixels
    int channels;           // Number of channels (3 for BGR)
    int stride;             // Bytes per row (width * channels)
    unsigned char *data;    // Image data array (top-down storage)
} Image;


int   readImage(const char *filename, Image *img);
int   writeImage(const char *filename, const Image *img);
int   indexx(const Image *img, int row, int col, int ch);
int   getPixelVal(const Image *img, int row, int col, unsigned char *b, unsigned char *g, unsigned char *r);
int   setPixelVal(Image *img, int row, int col, unsigned char b, unsigned char g, unsigned char r);
Image conv3x3(const Image *in, const float K[3][3], float div, float addBias);
Image sharpenImage(const Image *input);
Image blurImage(const Image *input);
void  contrastEnhance(Image *img);
void negateImage(Image *image);
Image cloneImage(const Image *src);
void  reduceGrayLevels(Image *img, int levels);
void freeImage(Image *img);
Image getSubImage(int ul_r, int ul_c, int lr_r, int lr_c, const Image *src);
Image rotate90(const Image *img);
Image rotate180(const Image *img);

#endif