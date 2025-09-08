import cv2
import numpy as np
import matplotlib.pyplot as plt

# Objectives 
# 1. Histogram Equalisation
# 2. Histogram Specialisation
# 


def histogram_equalization(image):
    
    result = np.zeros_like(image)
    
    for ch in range(image.shape[2]):
        channel = image[:, :, ch]
        
        # Compute histogram
        histogram, _ = np.histogram(channel.flatten(), 256, [0, 256])
        
        # PDF
        pdf = histogram / histogram.sum()
        
        # CDF
        cdf = pdf.cumsum()
        cdf_normalized = np.round(255 * cdf).astype(np.uint8)
        
        # Map original pixel values using CDF
        result[:, :, ch] = cdf_normalized[channel]
    
    return result


def histogram_specification(source, reference):
   
    result = np.zeros_like(source)
    for ch in range(source.shape[2]):
        src = source[:, :, ch]
        ref = reference[:, :, ch]
        
        # Histograms
        src_hist, _ = np.histogram(src.flatten(), 256, [0, 256])
        ref_hist, _ = np.histogram(ref.flatten(), 256, [0, 256])
        
        # PDFs
        src_pdf = src_hist / src_hist.sum()
        ref_pdf = ref_hist / ref_hist.sum()
        
        # CDFs
        src_cdf = src_pdf.cumsum()
        ref_cdf = ref_pdf.cumsum()
        
        # Build mapping: for each src level, find closest ref level
        mapping = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            j = np.argmin(np.abs(src_cdf[i] - ref_cdf))
            mapping[i] = j
        
        # Apply mapping
        result[:, :, ch] = mapping[src]
    
    return result


if __name__ == "__main__":
    

    image = cv2.imread(r"E:\CodeSpace\GitHub\Computer-Vision-and-Image-Processing\Histogram Equalisation & Specification\lena_color.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Histogram Equalization
    he_img = histogram_equalization(image)

    # Reference image
    ref_img = cv2.imread(r"E:\CodeSpace\GitHub\Computer-Vision-and-Image-Processing\Histogram Equalisation & Specification\lena_color.png")
    ref_img = cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)
    hs_img = histogram_specification(image, ref_img)

    # Display
    titles = ["Original", "Histogram Equalized", "Histogram Specified (to reference)"]
    images = [image, he_img, hs_img]

    plt.figure(figsize=(15, 8))
    
    for i in range(3):
        plt.subplot(1, 3, i + 1)
        plt.imshow(images[i])
        plt.title(titles[i])
        plt.axis("off")
    plt.tight_layout()
    
    plt.show()
