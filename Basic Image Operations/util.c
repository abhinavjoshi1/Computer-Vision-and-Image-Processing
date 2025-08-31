#include <stdio.h>

#include "util.h"


int readImage(const char *filename, Image *image)
{

    FILE *fileptr = fopen(filename, "rb");
    if (!fileptr)
    {
        perror("Failed to open file.");
        return 1;
    }
    
    File_Header FH;
    Info_Header IH;

    // Read file header
    if(fread(&FH, sizeof(File_Header), 1, fileptr) != 1)
    {
        perror("Error reading file header");
        fclose(fileptr);
    }
    // Read info header
    if(fread(&IH, sizeof(Info_Header), 1, fileptr) != 1)
    {
        perror("Error reading info header");
        fclose(fileptr);
    }


    // Validate BMP
    if (FH.bfType != 0x4D42)
    { 
        printf("Not a BMP file\n");
        fclose(fileptr);
        return 1;
    }

    // Go to pixel data and read.
    fseek(fileptr, FH.bfOffBits, SEEK_SET);

    int row_size = ((IH.biWidth * 3 + 3) & ~3); // to make multiple of 4
    int data_size = row_size * abs(IH.biHeight);

    unsigned char* pixels = (unsigned char* )malloc(data_size);

    if(fread(pixels, 1, data_size, fileptr) != data_size)
    {
        perror("Error reading pixel data.");
        free(pixels);
        fclose(fileptr);
        return 1;
    }

    image->width = IH.biWidth;
    image->height = abs(IH.biHeight);
    image->pixels = (unsigned char *)malloc(image->width * image->height * 3);

    for (int row = 0; row < image->height; row++) {

        unsigned char *src = pixels + ((IH.biHeight > 0) ? (image->height - 1 - row) * row_size : row * row_size);
        unsigned char *dst = image->pixels + row * image->width * 3;
        for (int x = 0; x < image->width * 3; x++) {
            dst[x] = src[x];
        }
    }

    free(pixels);
    return 0; // 0 for good.
}


// writeImage(fileName, image) - Write an image
int writeImage(const char *fileName, Image *image)
{
    FILE *file_ptr = fopen(fileName, "rb");
    if (!file_ptr) {
        perror("Failed to open file");
        return 0;
    }

    int width = image->width, height = image->height;
    int row_size = ((width * 3 + 3) & ~3);
    int padding_bytes = row_size - width * 3;

    uint32_t file_size = sizeof(File_Header) + sizeof(Info_Header) + (uint32_t)row_size * height;

    // Prepare file header
    File_Header fh = {0};
    fh.bfType = 0x4D42; // 'BM'
    fh.bfSize = file_size;
    fh.bfOffBits = sizeof(File_Header) + sizeof(Info_Header);

    // Prepare info header
    Info_Header ih = {0};
    ih.biSize = sizeof(Info_Header);
    ih.biWidth = width;
    ih.biHeight = height; // Positive = bottom-up storage
    ih.biPlanes = 1;
    ih.biBitCount = 24;
    ih.biCompression = 0;
    ih.biSizeImage = (uint32_t)row_size * height;

    // Write headers
    if (fwrite(&fh, sizeof(fh), 1, fp) != 1 || fwrite(&ih, sizeof(ih), 1, fp) != 1) {
        fclose(fp);
        return 0;
    }

    // Write pixel data (bottom-up order for BMP)
    unsigned char pad[3] = {0,0,0};
    for (int r = height - 1; r >= 0; --r) {
        fwrite(image->pixels + (size_t)r * image->stride, 1, (size_t)image->stride, file_ptr);
        if (padding_bytes) fwrite(pad, 1, (size_t)padding_bytes, file_ptr);
    }

    fclose(file_ptr);
    return 0;

}


int index(const Image *image, int r, int c, int ch)
{
    return (r * image->stride) + (c * image->channels) + ch;
}


// getImageInfo(noRows, noCols, maxVal) - Show image info

//  bool inBounds(r, c) = if pixel r,c in range
// int getPixelVal(r, c) - Get pixel value at r,c
// setPixelVal(r, c, value) - Set pixel value


//  getSubImage(Ulr, Ulc, LRr, LRc, oldImage) - get sub image based on inputs

// int meanGray() - get mean gray level value

// shrinkImage(s, oldImage) - shrik image
// enlargeImage(s, oldImage) - enlarge image

//  reflectImage(flag, oldImage) - reflect along horizontal or vertical direction

// operator+ (image addition) - Computes the sum of two given images or can implement a simple image morphing algorithm
// operator- (image subtraction) - useful for change detection, consider absolute difference

// negateImage() - negative of image

// translateImage(t, oldImage) ?

// rotateImage(theta, oldImage) - roate