#include <stdio.h>

#include "util.h"

// readImage(fileName, image) - Read an image
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