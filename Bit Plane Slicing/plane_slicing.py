
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Qbjective

# 1. Extract each bit plane from image
# 2. Creating binary image for each bit plane
# 3. Compare content of each plane


def read_image(image_path):
    
    input_image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    
    return gray_image

def extract_bit_plane(image, bit_position):
    
    bit_plane = (image >> bit_position) & 1
    bit_plane = bit_plane * 255
    
    return bit_plane


# Significance of each plane can be understood as number of clear bit in each plane.
def analyze_bit_plane_significance(bit_planes):

    significance = []
    for i, plane in enumerate(bit_planes):
        non_zero_ratio = np.count_nonzero(plane) / plane.size
        significance.append(non_zero_ratio)
        print(f"Bit Plane {i} (2^{i}): {non_zero_ratio:.3f} non-zero ratio")
    
    return significance


def display_bit_planes(image, bit_planes):

    figure, axes = plt.subplots(3, 3, figsize=(15, 12))
    
    # Display original image in top-left
    axes[0, 0].imshow(image, cmap='gray')
    axes[0, 0].set_title('Original Image\n(8-bit Grayscale)', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Display each bit plane
    positions = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    
    for i, (bit_plane, (row, col)) in enumerate(zip(bit_planes, positions)):
        axes[row, col].imshow(bit_plane, cmap='gray')
        axes[row, col].set_title(f'Bit Plane {i} : (2^{i} = {2**i})', 
                                fontsize=11, fontweight='bold')
        axes[row, col].axis('off')
        
        # Add text showing bit significance
        non_zero_ratio = np.count_nonzero(bit_plane) / bit_plane.size
        axes[row, col].text(0.02, 0.98, f'{non_zero_ratio:.1%}', transform=axes[row, col].transAxes, verticalalignment='top',bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    
if __name__ == "__main__":
    
    IMG_PATH = r"E:\CodeSpace\GitHub\Computer-Vision-and-Image-Processing\Bit Plane Slicing\lena_color.png"
    
    gray_image = read_image(IMG_PATH)
    
    print(f"Image shape: {gray_image.shape}")
    print(f"Image data type: {gray_image.dtype}")
    print(f"Pixel value range: {gray_image.min()} to {gray_image.max()}")
    
    
    bit_planes = []
    
    for i in range(8):
        bit_plane = extract_bit_plane(gray_image, i)
        # print(bit_plane)
        bit_planes.append(bit_plane)
        # print(type(bit_planes))
    
    display_bit_planes(gray_image, bit_planes)

    
