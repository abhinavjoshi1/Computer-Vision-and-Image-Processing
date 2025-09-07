
#include "util.h"
#include <string.h> 
#include <math.h> 
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

Image createImage(int h, int w, int ch)
{
    Image image;
    image.width = w;
    image.height = h;
    image.channels = ch;
    image.stride = w * ch;
    image.data = (unsigned char*)calloc((size_t)h * image.stride, 1);
    return image;
}

Image cloneImage(const Image *src)
{
    Image output = createImage(src->height, src->width, src->channels);
    memcpy(output.data, src->data, (size_t)src->height * src->stride);
    return output;
}

int inBounds(const Image *img, int row, int col)
{
    return (row >= 0 && row < img->height && col >= 0 && col < img->width);
}

int readImage(const char *filename, Image *image) {
    FILE *file_ptr = fopen(filename, "rb");
    if (!file_ptr) {
        perror("Error opening file");
        return 0;
    }

    BITMAPFILEHEADER File_Header;
    fread(&File_Header, sizeof(BITMAPFILEHEADER), 1, file_ptr);

    if (File_Header.bf_type != 0x4D42)
    {
        printf("Not a BMP file\n");
        fclose(file_ptr);
        return 0;
    }

    BITMAPINFOHEADER Info_Header;
    fread(&Info_Header, sizeof(BITMAPINFOHEADER), 1, file_ptr);

    if (Info_Header.bi_bit_count != 24 || Info_Header.bi_compression != 0)
    {
        printf("Only uncompressed 24-bit BMP supported.\n");
        fclose(file_ptr);
        return 0;
    }

    image->width = Info_Header.bi_width;
    image->height = abs(Info_Header.bi_height);  // height can be negative
    image->channels = 3;
    image->stride = image->width * image->channels;
    int rowSize = (image->stride + 3) & ~3; // padded row size

    // allocate memory (top-down order, no padding in storage)
    image->data = (unsigned char *)malloc(image->stride * image->height);
    if (!image->data)
    {
        printf("Memory allocation failed\n");
        fclose(file_ptr);
        return 0;
    }

    fseek(file_ptr, File_Header.bf_offbits, SEEK_SET);

    unsigned char *rowBuffer = (unsigned char *)malloc(rowSize);
    if (!rowBuffer) {
        free(image->data);
        fclose(file_ptr);
        return 0;
    }

    int is_bottom_up = (Info_Header.bi_height > 0);

    for (int row = 0; row < image->height; row++) {
        fread(rowBuffer, 1, rowSize, file_ptr);

        unsigned char *dst;
        if (is_bottom_up)
            dst = image->data + (image->height - 1 - row) * image->stride;
        else
            dst = image->data + row * image->stride;

        for (int col = 0; col < image->stride; col++) {
            dst[col] = rowBuffer[col]; // copy only valid pixels (no padding)
        }
    }

    free(rowBuffer);
    fclose(file_ptr);
    return 1;
}


int writeImage(const char *filename, const Image *image)
{
    FILE *file_ptr = fopen(filename, "wb");
    if (!file_ptr) return 0;

    int rowSize = (image->width * image->channels + 3) & ~3;  
    int dataSize = rowSize * image->height;

    // File Header
    BITMAPFILEHEADER FH;
    FH.bf_type = 0x4D42; // "BM"
    FH.bf_size = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + dataSize;
    FH.bf_reserved1 = 0;
    FH.bf_reserved2 = 0;
    FH.bf_offbits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // Info Header
    BITMAPINFOHEADER IH;
    IH.bi_size = sizeof(BITMAPINFOHEADER);
    IH.bi_width = image->width;
    IH.bi_height = image->height; 
    IH.bi_planes = 1;
    IH.bi_bit_count = image->channels * 8; 
    IH.bi_compression = 0;
    IH.bi_size_image = dataSize;
    IH.bi_xpels_permeter = 2835; 
    IH.bi_ypels_permeter = 2835;
    IH.bi_clr_used = 0;
    IH.bi_clrimportant = 0;

    // Write headers
    fwrite(&FH, sizeof(FH), 1, file_ptr);
    fwrite(&IH, sizeof(IH), 1, file_ptr);

    // Write pixel data in bottom-up order
    unsigned char *padding = calloc(1, rowSize - image->stride);
    for (int y = image->height - 1; y >= 0; y--) {  // bottom-up
        unsigned char *row = image->data + y * image->stride;
        fwrite(row, 1, image->stride, file_ptr);
        if (rowSize > image->stride)
            fwrite(padding, 1, rowSize - image->stride, file_ptr);
    }
    free(padding);

    fclose(file_ptr);
    return 1;
}


int indexx(const Image *image, int row, int col, int ch)
{
    return (row * image->stride) + (col * image->channels) + ch;
}

Image conv3x3(const Image *in, const float K[3][3], float div, float addBias)
{
    Image output = createImage(in->height, in->width, 3);

    for (int row = 0; row < in->height; row++)
    {
        for (int col = 0; col < in->width; col++)
        {
            float acc[3] = {0, 0, 0};  

            // Apply 3x3 kernel
            for (int kr = -1; kr <= 1; ++kr)
            {
                for (int kc = -1; kc <= 1; ++kc) {
                    int rr = row + kr, cc = col + kc;
                    float k = K[kr+1][kc+1];

                    if (!inBounds(in, rr, cc)) continue;  

                    int sp = indexx(in, rr, cc, 0);
                    acc[0] += k * in->data[sp+0];
                    acc[1] += k * in->data[sp+1];
                    acc[2] += k * in->data[sp+2];
                }
            }

            int dp = indexx(&output, row, col, 0);

            // Apply division and bias, clamp to [0,255]
            for (int ch = 0; ch < 3; ++ch)
            {
                float v = (div != 0 ? acc[ch] / div : acc[ch]) + addBias;
                if (v < 0) v = 0;
                if (v > 255) v = 255;
                output.data[dp+ch] = (unsigned char)(v + 0.5f);
            }
        }
    }
    return output;
}


Image sharpenImage(const Image *input)
{
    // Laplacian sharpening kernel
    float K[3][3] = {{0,-1,0},{-1,5,-1},{0,-1,0}};
    return conv3x3(input, K, 1.0f, 0.0f);
}

Image blurImage(const Image *input)
{
    float K[3][3] = {{1,1,1},{1,1,1},{1,1,1}};
    return conv3x3(input, K, 9.0f, 0.0f);
}

int getPixelVal(const Image *image, int row, int col, unsigned char *b, unsigned char *g, unsigned char *rC)
{
    // Checking need not be done, as used for center pixel only in this assignment. 

    int p = indexx(image, row, col, 0);
    if (b) *b = image->data[p+0];     // Blue 
    if (g) *g = image->data[p+1];     // Green 
    if (rC) *rC = image->data[p+2];   // Red

    return 0;
}

void negateImage(Image *image)
{

    size_t totalBytes = (size_t)image->height * image->stride;
    for (size_t i = 0; i < totalBytes; i++)
    {
        image->data[i] = (unsigned char)(255 - image->data[i]);
    }
}

int setPixelVal(Image *image, int row, int col, unsigned char b, unsigned char g, unsigned char rC)
{
    if (!inBounds(image, row, col))
        return 0;

    int p = indexx(image, row, col, 0);
    image->data[p+0] = b;   // Blue
    image->data[p+1] = g;   // Green
    image->data[p+2] = rC;  // Red

    return 0;
}

Image getSubImage(int ul_r, int ul_c, int lr_r, int lr_c, const Image *old_image)
{
    if (ul_r < 0) ul_r = 0;
    if (ul_c < 0) ul_c = 0;
    if (lr_r > old_image->height-1) lr_r = old_image->height-1;
    if (lr_c > old_image->width-1)  lr_c = old_image->width-1;

    int h = lr_r - ul_r + 1;
    int w = lr_c - ul_c + 1;

    if (h <= 0 || w <= 0) {
        printf("Invalid crop dimensions!\n");
        return createImage(0,0,3);
    }

    Image output = createImage(h, w, 3);

    // Copy pixel data row by row
    for (int row = 0; row < h; ++row)
    {
        memcpy(output.data + (size_t)row * output.stride, old_image->data + (size_t)(ul_r + row) * old_image->stride + (size_t)ul_c * 3, (size_t)w * 3);
    }

    return output;
}


void contrastEnhance(Image *image)
{
    printf("Applying contrast enhancement...\n");

    int minC[3] = {255, 255, 255};  // Min values for each channel
    int maxC[3] = {0, 0, 0};        // Max values for each channel

    // Find min and max values for each color channel
    for (int row = 0; row < image->height; row++)
    {
        for (int col = 0; col < image->width; col++)
        {
            int p = indexx(image, row, col, 0);
            for (int ch = 0; ch < 3; ++ch)
            {
                int v = image->data[p+ch];
                if (v < minC[ch]) minC[ch] = v;
                if (v > maxC[ch]) maxC[ch] = v;
            }
        }
    }

    //  Linear stretch transformation
    for (int row = 0; row < image->height; row++)
    {
        for (int col = 0; col < image->width; col++)
        {
            int p = indexx(image, row, col, 0);
            for (int ch = 0; ch < 3; ++ch)
            {
                int low = minC[ch], high = maxC[ch];
                int v = image->data[p+ch];

                if (high == low)
                {
                    image->data[p+ch] = (unsigned char)v; 
                } 
                else
                {
                    int nv = (int)round((v - low) * 255.0 / (high - low));
                    if (nv < 0) nv = 0;
                    if (nv > 255) nv = 255;
                    image->data[p+ch] = (unsigned char)nv;
                }
            }
        }
    }
}

void reduceGrayLevels(Image *image, int levels)
{
    if (levels <= 1)
    {
        memset(image->data, 0, (size_t)image->height * image->stride); // All pixels to black if level less than 1
        return;
    }

    int step = 256 / levels;
    if (step <= 0) step = 1;

    size_t totalPixels = (size_t)image->height * image->stride;

    for (size_t i = 0; i < totalPixels; i++) {
        image->data[i] = (unsigned char)((image->data[i] / step) * step);
    }

    printf("Reduction of gray level to %d level with step size: %d \n", levels, step);
}


Image rotate90(const Image *image)
{
    // 90 degree rotate
    Image output = createImage(image->width, image->height, 3);

    for (int row = 0; row < image->height; row++)
    {
        for (int col = 0; col < image->width; col++)
        {
            int rr = col;
            int cc = image->height - 1 - row;

            int sp = indexx(image, row, col, 0);
            int dp = indexx(&output, rr, cc, 0);

            output.data[dp+0] = image->data[sp+0];
            output.data[dp+1] = image->data[sp+1];
            output.data[dp+2] = image->data[sp+2];
        }
    }
    return output;
}

Image rotate180(const Image *image)
{
    // 180 degree rotate
    Image output = createImage(image->height, image->width, 3);

    for (int row = 0; row < image->height; row++)
    {
        for (int col = 0; col < image->width; col++)
        {
            // 90-degree rotation mapping: (row,col) -> (col, height-1-row)
            int rr = image->height - 1 - row;
            int cc = image->width - 1 - col;

            int sp = indexx(image, row, col, 0);
            int dp = indexx(&output, rr, cc, 0);

            output.data[dp+0] = image->data[sp+0];
            output.data[dp+1] = image->data[sp+1];
            output.data[dp+2] = image->data[sp+2];
        }
    }
    return output;
}


void freeImage(Image *image)
{
    free(image->data);
    image->data = NULL;
    image->width = image->height = image->channels = image->stride = 0;
}