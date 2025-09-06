# Imports
import cv2
import numpy as np
import matplotlib.pyplot as plot

RGB_IMG_PATH = "E:\CodeSpace\GitHub\Computer-Vision-and-Image-Processing\Gray level reduction\lena_color.png"
GRAY_IMG_PATH = "E:\CodeSpace\GitHub\Computer-Vision-and-Image-Processing\Gray level reduction\lena_gray.png"

reduction_levels = [128, 64, 32, 16, 8, 4, 2]


# Objectives

# 5. Uniform vs Non Uniform quatization.
# 6. Restore compressed image ( as gray level reduction used for compression ).






# Image read and display
rgb_input_image = cv2.imread(RGB_IMG_PATH)
rgb_input_image_rgb = cv2.cvtColor(rgb_input_image, cv2.COLOR_BGR2RGB)

gray_input_image = cv2.imread(GRAY_IMG_PATH)
gray_input_image = cv2.imread(GRAY_IMG_PATH, cv2.IMREAD_GRAYSCALE)


# plot.imshow(rgb_input_image_rgb)
# plot.imshow(gray_input_image)
# plot.axis("off")
# plot.show()


# Quantization
def quantize_image(input_image, levels):
    
    bin_width = 256 // levels
    
    # midpoint
    # quantized = (input_image // bin_width) * bin_width + bin_width //2
    
    # lower bound
    quantized = (input_image // bin_width) * bin_width


    result = np.clip(quantized, 0, 255).astype(np.uint8)
    
    return result


# Operation
def perform_operations(rgb_image, grayscale_image, reduction_levels):
    
    elements = len(reduction_levels)
    
    for i, levels in enumerate(reduction_levels, 1):
        reduced_image = quantize_image(rgb_image, levels)
        plot.subplot(2, elements, i)
        plot.imshow(reduced_image)
        plot.title(f"Gray Level : {levels}")
        plot.axis("off")
        
    for i, levels in enumerate(reduction_levels, 1):
        reduced_image = quantize_image(grayscale_image, levels)
        plot.subplot(2, elements, elements + i)
        plot.imshow(reduced_image, cmap="gray")
        plot.title(f"Gray Levels: {levels}")
        plot.axis("off")
    
    plot.show()
    
    
if __name__ == "__main__":
    
    perform_operations(rgb_input_image, gray_input_image, reduction_levels)
    


