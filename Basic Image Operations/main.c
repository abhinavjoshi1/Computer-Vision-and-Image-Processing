
#include <stdio.h>
#include "util.h"


int main(int argc, char **argv)
{

    const char* input_file = (argc > 1) ? argv[1] : "input.bmp";

    Image image;
    if (!readImage(input_file, &image))
    {
        fprintf(stderr, "Failed to read %s\n", input_file);
        return 1;
    }

    printf("Processing the input image ...\n");

    printf("1. Pixel value access.");
    unsigned char b, g, r;
    int centerR = image.height / 2, centerC = image.width / 2;
    getPixelVal(&image, centerR, centerC, &b, &g, &r);
    printf("Center pixel (%d,%d): R=%u G=%u B=%u\n", centerR, centerC, r, g, b);

    writeImage("original.bmp", &image);

    printf("2. Gray level reduction.");
    Image reduced_image = cloneImage(&image);
    reduceGrayLevels(&reduced_image, 4);
    writeImage("reduced_gray_level.bmp", &reduced_image);


    printf("3. Image crop.");
    int ul_r = image.height / 4, ul_c = image.width / 4;
    int lr_r = 3 * image.height / 4, lr_c = 3 * image.width / 4;
    Image crop = getSubImage(ul_r, ul_c, lr_r, lr_c, &image);
    printf("Cropped region: (%d,%d) to (%d,%d)\n", ul_r, ul_c, lr_r, lr_c);
    writeImage("cropped_image.bmp", &crop);

    printf("4. Image Filtering.");
    Image blurred = blurImage(&image);
    writeImage("blur_image.bmp", &blurred);

    Image sharpened = sharpenImage(&image);
    writeImage("sharp_image.bmp", &sharpened);

    printf("5. Negative Image.");
    Image negative = cloneImage(&image);
    negateImage(&negative);
    writeImage("negative_image.bmp", &negative);
    
    printf("6. Contrast Enhancement.");
    Image contrast = cloneImage(&image);
    contrastEnhance(&contrast);
    writeImage("contrast_enhance.bmp", &contrast);


    printf("7. Image Rotation:\n");
    Image rotate_90 = rotate90(&image);
    writeImage("rotated_image_90.bmp", &rotate_90);

    Image rotate_180 = rotate180(&image);
    writeImage("rotated_image_180.bmp", &rotate_180);

    // cleaning.
    freeImage(&reduced_image);
    freeImage(&negative); 
    freeImage(&contrast);
    freeImage(&rotate_90);
    freeImage(&rotate_180);
    freeImage(&blurred);
    freeImage(&sharpened);
    freeImage(&crop);
    freeImage(&image);

    return 0;
}
