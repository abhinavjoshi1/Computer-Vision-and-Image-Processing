import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def load_image(image_path):
    """Load RGB image and convert to numpy array."""
    img = Image.open(image_path)
    img_rgb = img.convert('RGB')
    return np.array(img_rgb)

def apply_padding(image, pad_size, mode='reflect'):
    """Apply padding to image for convolution operations."""
    if len(image.shape) == 3:  # RGB image
        h, w, c = image.shape
        padded = np.zeros((h + 2*pad_size, w + 2*pad_size, c), dtype=image.dtype)
        
        for channel in range(c):
            if mode == 'reflect':
                # Reflect padding
                padded[:, :, channel] = np.pad(image[:, :, channel], pad_size, mode='reflect')
            elif mode == 'zero':
                # Zero padding
                padded[pad_size:h+pad_size, pad_size:w+pad_size, channel] = image[:, :, channel]
            elif mode == 'replicate':
                # Replicate edge values
                padded[:, :, channel] = np.pad(image[:, :, channel], pad_size, mode='edge')
    else:  # Grayscale image
        if mode == 'reflect':
            padded = np.pad(image, pad_size, mode='reflect')
        elif mode == 'zero':
            h, w = image.shape
            padded = np.zeros((h + 2*pad_size, w + 2*pad_size), dtype=image.dtype)
            padded[pad_size:h+pad_size, pad_size:w+pad_size] = image
        elif mode == 'replicate':
            padded = np.pad(image, pad_size, mode='edge')
    
    return padded

def convolve2d(image, kernel):
    """Perform 2D convolution on a single channel."""
    kernel_h, kernel_w = kernel.shape
    pad_h, pad_w = kernel_h // 2, kernel_w // 2
    
    # Pad the image
    padded = apply_padding(image, max(pad_h, pad_w), mode='reflect')
    
    # Get output dimensions
    output_h = image.shape[0]
    output_w = image.shape[1]
    
    # Initialize output
    output = np.zeros((output_h, output_w), dtype=np.float64)
    
    # Perform convolution
    for i in range(output_h):
        for j in range(output_w):
            # Extract the region of interest
            roi = padded[i:i+kernel_h, j:j+kernel_w]
            # Element-wise multiplication and sum
            output[i, j] = np.sum(roi * kernel)
    
    return output

def apply_filter_rgb(image, kernel):
    """Apply filter to RGB image by processing each channel separately."""
    h, w, c = image.shape
    filtered = np.zeros((h, w, c), dtype=np.float64)
    
    for channel in range(c):
        filtered[:, :, channel] = convolve2d(image[:, :, channel].astype(np.float64), kernel)
    
    return filtered

def gaussian_kernel(size, sigma):
    """Create a Gaussian kernel for blurring."""
    kernel = np.zeros((size, size))
    center = size // 2
    
    # Calculate Gaussian values
    for i in range(size):
        for j in range(size):
            x, y = i - center, j - center
            kernel[i, j] = np.exp(-(x*x + y*y) / (2 * sigma * sigma))
    
    # Normalize
    kernel = kernel / np.sum(kernel)
    return kernel

def box_blur_kernel(size):
    """Create a simple box blur kernel."""
    kernel = np.ones((size, size)) / (size * size)
    return kernel

def unsharp_masking(image, blur_kernel_size=5, sigma=1.0, amount=1.5, threshold=0):
    """
    Apply unsharp masking sharpening.
    
    Args:
        image: Input RGB image
        blur_kernel_size: Size of the blur kernel
        sigma: Standard deviation for Gaussian blur
        amount: Sharpening strength
        threshold: Threshold for sharpening (not implemented in basic version)
    
    Returns:
        Sharpened image
    """
    print(f"Applying Unsharp Masking (kernel_size={blur_kernel_size}, sigma={sigma}, amount={amount})")
    
    # Create Gaussian blur kernel
    blur_kernel = gaussian_kernel(blur_kernel_size, sigma)
    
    # Create blurred version
    blurred = apply_filter_rgb(image.astype(np.float64), blur_kernel)
    
    # Create mask (difference between original and blurred)
    mask = image.astype(np.float64) - blurred
    
    # Apply sharpening: original + amount * mask
    sharpened = image.astype(np.float64) + amount * mask
    
    # Clip values to valid range
    sharpened = np.clip(sharpened, 0, 255)
    
    return sharpened.astype(np.uint8)

def high_pass_filter(image, cutoff_size=3):
    """
    Apply high-pass filtering for sharpening.
    
    Args:
        image: Input RGB image
        cutoff_size: Size of the low-pass filter to subtract
    
    Returns:
        High-pass filtered image
    """
    print(f"Applying High-Pass Filter (cutoff_size={cutoff_size})")
    
    # Create low-pass filter (simple averaging)
    low_pass_kernel = box_blur_kernel(cutoff_size)
    
    # Apply low-pass filter
    low_pass = apply_filter_rgb(image.astype(np.float64), low_pass_kernel)
    
    # High-pass = Original - Low-pass
    high_pass = image.astype(np.float64) - low_pass
    
    # Add back to original for sharpening effect
    sharpened = image.astype(np.float64) + high_pass
    
    # Clip values
    sharpened = np.clip(sharpened, 0, 255)
    
    return sharpened.astype(np.uint8)

def laplacian_sharpening(image, kernel_type='4-connected', amount=1.0):
    """
    Apply Laplacian sharpening.
    
    Args:
        image: Input RGB image
        kernel_type: '4-connected' or '8-connected'
        amount: Sharpening strength
    
    Returns:
        Laplacian sharpened image
    """
    print(f"Applying Laplacian Sharpening (kernel_type={kernel_type}, amount={amount})")
    
    # Define Laplacian kernels
    if kernel_type == '4-connected':
        laplacian_kernel = np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ])
    else:  # 8-connected
        laplacian_kernel = np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ])
    
    # Apply Laplacian filter
    laplacian = apply_filter_rgb(image.astype(np.float64), laplacian_kernel)
    
    # Sharpen: Original + amount * Laplacian
    sharpened = image.astype(np.float64) + amount * laplacian
    
    # Clip values
    sharpened = np.clip(sharpened, 0, 255)
    
    return sharpened.astype(np.uint8)

def gradient_sharpening(image, operator='sobel', amount=0.5):
    """
    Apply gradient-based sharpening using Sobel or Prewitt operators.
    
    Args:
        image: Input RGB image
        operator: 'sobel' or 'prewitt'
        amount: Sharpening strength
    
    Returns:
        Gradient sharpened image
    """
    print(f"Applying Gradient Sharpening (operator={operator}, amount={amount})")
    
    # Define gradient kernels
    if operator == 'sobel':
        gx = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ])
        gy = np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ])
    else:  # prewitt
        gx = np.array([
            [-1, 0, 1],
            [-1, 0, 1],
            [-1, 0, 1]
        ])
        gy = np.array([
            [-1, -1, -1],
            [0, 0, 0],
            [1, 1, 1]
        ])
    
    # Calculate gradients for each channel
    gradient_magnitude = np.zeros_like(image, dtype=np.float64)
    
    for channel in range(image.shape[2]):
        # Apply gradient filters
        grad_x = convolve2d(image[:, :, channel].astype(np.float64), gx)
        grad_y = convolve2d(image[:, :, channel].astype(np.float64), gy)
        
        # Calculate gradient magnitude
        gradient_magnitude[:, :, channel] = np.sqrt(grad_x**2 + grad_y**2)
    
    # Sharpen: Original + amount * Gradient
    sharpened = image.astype(np.float64) + amount * gradient_magnitude
    
    # Clip values
    sharpened = np.clip(sharpened, 0, 255)
    
    return sharpened.astype(np.uint8)

def display_results(original, results, titles):
    """Display original and sharpened images in a grid."""
    n_images = len(results) + 1
    cols = 3
    rows = (n_images + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    
    # Flatten axes for easier indexing
    axes_flat = axes.flatten()
    
    # Display original image
    axes_flat[0].imshow(original)
    axes_flat[0].set_title('Original Image', fontsize=12, fontweight='bold')
    axes_flat[0].axis('off')
    
    # Display sharpened results
    for i, (result, title) in enumerate(zip(results, titles)):
        axes_flat[i+1].imshow(result)
        axes_flat[i+1].set_title(title, fontsize=12, fontweight='bold')
        axes_flat[i+1].axis('off')
    
    # Hide unused subplots
    for i in range(n_images, len(axes_flat)):
        axes_flat[i].axis('off')
    
    plt.tight_layout()
    plt.suptitle('Image Sharpening Techniques Comparison', fontsize=16, fontweight='bold', y=0.98)
    plt.show()

def analyze_sharpening_effects(original, sharpened_images, titles):
    """Analyze and display the sharpening effects."""
    print("\\n" + "="*60)
    print("SHARPENING ANALYSIS")
    print("="*60)
    
    for i, (sharpened, title) in enumerate(zip(sharpened_images, titles)):
        # Calculate difference from original
        diff = np.abs(sharpened.astype(np.float64) - original.astype(np.float64))
        mean_diff = np.mean(diff)
        max_diff = np.max(diff)
        
        # Calculate enhancement intensity
        enhancement = np.mean(np.abs(sharpened.astype(np.float64) - original.astype(np.float64)))
        
        print(f"{title}:")
        print(f"  Mean pixel difference: {mean_diff:.2f}")
        print(f"  Max pixel difference: {max_diff:.2f}")
        print(f"  Enhancement intensity: {enhancement:.2f}")
        print()

def main():
    # Load the RGB Lenna image
    image_path = r"Sharpening/lena_color.png"  # Update this to your image path
    
    try:
        print("Loading Lenna image...")
        original = load_image(image_path)
        print(f"✓ Image loaded: {original.shape} (H×W×C)")
        print("-" * 50)
    except Exception as e:
        print(f"Error loading image: {e}")
        print("Please ensure the Lenna image is in the correct path.")
        return
    
    # Apply different sharpening techniques
    print("Applying sharpening techniques...")
    print("-" * 50)
    
    # 1. Unsharp Masking
    unsharp_result = unsharp_masking(original, blur_kernel_size=5, sigma=1.0, amount=1.5)
    
    # 2. High-Pass Filtering
    highpass_result = high_pass_filter(original, cutoff_size=3)
    
    # 3. Laplacian Sharpening
    laplacian_result = laplacian_sharpening(original, kernel_type='4-connected', amount=0.8)
    
    # 4. Gradient-Based Sharpening (Sobel)
    gradient_sobel_result = gradient_sharpening(original, operator='sobel', amount=0.5)
    
    # 5. Gradient-Based Sharpening (Prewitt) - Bonus
    gradient_prewitt_result = gradient_sharpening(original, operator='prewitt', amount=0.5)
    
    print("-" * 50)
    print("✓ All sharpening techniques applied successfully!")
    
    # Collect results
    results = [
        unsharp_result,
        highpass_result, 
        laplacian_result,
        gradient_sobel_result,
        gradient_prewitt_result
    ]
    
    titles = [
        'Unsharp Masking',
        'High-Pass Filter',
        'Laplacian Sharpening',
        'Gradient (Sobel)',
        'Gradient (Prewitt)'
    ]
    
    # Display results
    display_results(original, results, titles)
    
    # Analyze sharpening effects
    analyze_sharpening_effects(original, results, titles)
    
    # Show detailed comparison of a specific region (crop)
    print("Displaying detailed comparison...")
    show_detailed_comparison(original, results, titles)

def show_detailed_comparison(original, results, titles):
    """Show a detailed comparison of a cropped region."""
    # Crop a region for detailed comparison (center region)
    h, w = original.shape[:2]
    crop_size = min(h, w) // 3
    start_h = h // 2 - crop_size // 2
    start_w = w // 2 - crop_size // 2
    
    original_crop = original[start_h:start_h+crop_size, start_w:start_w+crop_size]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Show original crop
    axes[0, 0].imshow(original_crop)
    axes[0, 0].set_title('Original (Cropped)', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Show first 4 sharpened crops
    positions = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    
    for i in range(min(5, len(results))):
        result_crop = results[i][start_h:start_h+crop_size, start_w:start_w+crop_size]
        row, col = positions[i]
        axes[row, col].imshow(result_crop)
        axes[row, col].set_title(f'{titles[i]} (Cropped)', fontsize=12, fontweight='bold')
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.suptitle('Detailed Comparison - Cropped Region', fontsize=16, fontweight='bold', y=0.98)
    plt.show()

if __name__ == "__main__":
    main()