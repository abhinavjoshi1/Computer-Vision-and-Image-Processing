import cv2
import numpy as np
import matplotlib.pyplot as plot


SOURCE = r"E:\CodeSpace\GitHub\Computer-Vision-and-Image-Processing\Interpolation\lena_color.png"
#Objective

# 1. Nearest Neighbour
# 2. Bilinear Interpolation
# 3. Bicubic Interpolation
# 4. Display zoomed image and compare

image_height  = None
image_width   = None
image_channel = None

def read_image(IMG_PATH):

    global image_height, image_width, image_channel
    input_image = cv2.imread(IMG_PATH)
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    image_height, image_width, image_channel = input_image.shape
    
    return input_image


def nearest_neighbour(input_image, factor):

    new_height = int(image_height * factor)
    new_width  = int(image_width * factor)
    
    result_image = np.zeros((new_height, new_width, image_channel), dtype=np.uint8)

    for row in range(new_height):
        for col in range(new_width):
            orignal_i = int(row/factor)
            orignal_j = int(col/factor)
            
            for channel in range(image_channel):
                result_image[row, col, channel] =  input_image[orignal_i, orignal_j, channel]

    # print(result_image)
    return result_image
    
    
    
def bilinear_interpolation(input_image, factor):
    
    new_height = int(image_height * factor)
    new_width  = int(image_width * factor)
    
    result_image = np.zeros((new_height, new_width, image_channel), dtype=np.uint8)
    
    for row in range(new_height):
        for col in range(new_width):
            orignal_x = (row/factor)
            orignal_y = (col/factor)
            
            i1 = int(orignal_x)
            j1 = int(orignal_y)
            
            i2 = min(i1 + 1, image_height - 1)
            j2 = min(j1 + 1, image_width - 1)
            
            di = orignal_x - i1
            dj = orignal_y - j1
            
            for channel in range(image_channel):
                
                Q11 = int(input_image[i1][j1][channel])
                Q12 = int(input_image[i1][j2][channel])
                Q21 = int(input_image[i2][j1][channel])
                Q22 = int(input_image[i2][j2][channel])
                
                hor_inter_1 = Q11*(1 - dj) + Q12*dj
                hor_inter_2 = Q21*(1 - dj) + Q22*dj
                
                value = hor_inter_1*(1 - di) + hor_inter_2*di
                
                result_image[row][col][channel] = int(value)
                
    return result_image
                
            
def cubic_interpolate(p0, p1, p2, p3, x):
    return (p1 + 0.5 * x * (p2 - p0 + x * (2*p0 - 5*p1 + 4*p2 - p3 +
           x * (3*(p1 - p2) + p3 - p0))))
        
def bicubic_interpolation(input_image, zoom_factor):
    h, w, c = input_image.shape
    new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)

    zoomed = [[[0]*c for _ in range(new_w)] for _ in range(new_h)]

    for i in range(new_h):
        for j in range(new_w):
            orig_i = i / zoom_factor
            orig_j = j / zoom_factor

            i_int = int(orig_i)
            j_int = int(orig_j)
            di = orig_i - i_int
            dj = orig_j - j_int

            for ch in range(c):
                pixels = []
                for di_offset in range(-1, 3):
                    row = []
                    for dj_offset in range(-1, 3):
                        ni = max(0, min(h - 1, i_int + di_offset))
                        nj = max(0, min(w - 1, j_int + dj_offset))
                        row.append(int(input_image[ni][nj][ch]))
                    pixels.append(row)

                # interpolate rows in x
                temp = [cubic_interpolate(row[0], row[1], row[2], row[3], dj) for row in pixels]
                # interpolate in y
                value = cubic_interpolate(temp[0], temp[1], temp[2], temp[3], di)
                value = max(0, min(255, int(round(value))))
                zoomed[i][j][ch] = value
    return zoomed
    

def crop_center(input_image, crop_size=100):
    
    h, w = input_image.shape[:2]
    center_x, center_y = w // 2, h // 2
    half_crop = crop_size // 2
    
    x1 = max(0, center_x - half_crop)
    x2 = min(w, center_x + half_crop)
    y1 = max(0, center_y - half_crop)
    y2 = min(h, center_y + half_crop)
    
    return input_image[y1:y2, x1:x2]

if __name__ == "__main__":
    SOURCE = r"E:\CodeSpace\GitHub\Computer-Vision-and-Image-Processing\Interpolation\lena_color.png"
    
    input_image = read_image(SOURCE)
    methods = ["Nearest", "Bilinear"]
    factors = [2, 4]
    
    figure, axes = plot.subplots(len(methods), 5, figsize=(20, 12))
    
    axes[0, 0].imshow(input_image)
    axes[0, 0].set_title(f"Original\n({input_image.shape[1]}x{input_image.shape[0]})")
    axes[0, 0].axis("off")
    
    for i in range(1, len(methods)):
        axes[i, 0].axis("off")
    
    for i, method in enumerate(methods):
        col_idx = 1 
        
        for factor in factors:

            if method == "Nearest":
                result = nearest_neighbour(input_image, factor)
            elif method == "Bilinear":
                result = bilinear_interpolation(input_image, factor)
            elif method == "Bicubic":
                result = bicubic_interpolation(input_image, factor)
            
            # Full upscaled image
            axes[i, col_idx].imshow(result)
            axes[i, col_idx].set_title(f"{method} {factor}x\n({result.shape[1]}x{result.shape[0]})")
            axes[i, col_idx].axis("off")
            col_idx += 1
            
            # Cropped version
            cropped = crop_center(result, crop_size=200)
            axes[i, col_idx].imshow(cropped)
            axes[i, col_idx].set_title(f"{method} {factor}x (crop)")
            axes[i, col_idx].axis("off")
            col_idx += 1
    
    plot.tight_layout()
    plot.show() 
    

