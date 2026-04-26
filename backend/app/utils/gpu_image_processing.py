"""
GPU-Accelerated Image Processing for Face Recognition
Uses CUDA and OpenCL for faster image operations
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from .gpu_utils import gpu_manager

class GPUImageProcessor:
    def __init__(self):
        self.gpu_manager = gpu_manager
        self.gpu_manager.optimize_opencv_for_gpu()
        
        # Initialize GPU-based processors
        self._init_gpu_processors()
    
    def _init_gpu_processors(self):
        """Initialize GPU-based processors"""
        try:
            # Check if CUDA is actually available in OpenCV build
            if self.gpu_manager.cuda_available and hasattr(cv2, 'cuda'):
                # CUDA-based processors
                self.clahe_gpu = cv2.cuda.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                self.bilateral_filter_gpu = cv2.cuda.bilateralFilter
                self.gaussian_blur_gpu = cv2.cuda.GaussianBlur
            else:
                # No CUDA support in this OpenCV build
                self.clahe_gpu = None
                self.bilateral_filter_gpu = None
                self.gaussian_blur_gpu = None
            
            # OpenCL optimizations are handled automatically by OpenCV
                
        except Exception as e:
            # Silently fallback to CPU
            self.clahe_gpu = None
            self.bilateral_filter_gpu = None
            self.gaussian_blur_gpu = None
    
    def enhance_image_gpu(self, image: np.ndarray) -> np.ndarray:
        """Smart GPU-accelerated image enhancement - only use GPU when beneficial"""
        height, width = image.shape[:2]
        image_size = height * width
        
        # Only use GPU for larger images where the benefit outweighs overhead
        # Threshold: 1MP+ images benefit from GPU acceleration
        gpu_threshold = 1000000  # 1 megapixel
        
        try:
            # Check if CUDA is actually available
            if image_size > gpu_threshold and self.gpu_manager.cuda_available and hasattr(cv2, 'cuda') and self.clahe_gpu is not None:
                return self._enhance_image_cuda(image)
            elif image_size > gpu_threshold and self.gpu_manager.opencl_available:
                # For OpenCL, use even higher threshold due to overhead
                if image_size > 2000000:  # 2MP+
                    return self._enhance_image_opencl(image)
                else:
                    return self._enhance_image_cpu_optimized(image)
            else:
                # Use CPU for smaller images or when GPU not available
                return self._enhance_image_cpu_optimized(image)
        except Exception as e:
            return self._enhance_image_cpu_optimized(image)
    
    def _enhance_image_cuda(self, image: np.ndarray) -> np.ndarray:
        """CUDA-accelerated image enhancement"""
        # Upload image to GPU
        gpu_img = cv2.cuda_GpuMat()  # type: ignore
        gpu_img.upload(image)  # type: ignore
        
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            gpu_img_rgb = cv2.cuda.cvtColor(gpu_img, cv2.COLOR_BGR2RGB)  # type: ignore
        else:
            gpu_img_rgb = gpu_img
        
        # Convert to LAB color space for better processing
        if len(image.shape) == 3:
            gpu_lab = cv2.cuda.cvtColor(gpu_img_rgb, cv2.COLOR_RGB2LAB)  # type: ignore
            
            # Split channels
            gpu_l = cv2.cuda_GpuMat()  # type: ignore
            gpu_a = cv2.cuda_GpuMat()  # type: ignore
            gpu_b = cv2.cuda_GpuMat()  # type: ignore
            cv2.cuda.split(gpu_lab, [gpu_l, gpu_a, gpu_b])  # type: ignore
            
            # Apply CLAHE to L channel
            gpu_l_clahe = cv2.cuda_GpuMat()  # type: ignore
            self.clahe_gpu.apply(gpu_l, gpu_l_clahe)  # type: ignore
            
            # Merge channels back
            gpu_lab_enhanced = cv2.cuda_GpuMat()  # type: ignore
            cv2.cuda.merge([gpu_l_clahe, gpu_a, gpu_b], gpu_lab_enhanced)  # type: ignore
            
            # Convert back to RGB
            gpu_img_enhanced = cv2.cuda.cvtColor(gpu_lab_enhanced, cv2.COLOR_LAB2RGB)  # type: ignore
        else:
            # Grayscale image
            gpu_img_enhanced = cv2.cuda_GpuMat()  # type: ignore
            self.clahe_gpu.apply(gpu_img_rgb, gpu_img_enhanced)  # type: ignore
        
        # Apply bilateral filter for noise reduction
        gpu_filtered = cv2.cuda_GpuMat()  # type: ignore
        cv2.cuda.bilateralFilter(gpu_img_enhanced, gpu_filtered, -1, 75, 75)  # type: ignore
        
        # Apply Gaussian blur for smoothing
        gpu_blurred = cv2.cuda_GpuMat()  # type: ignore
        cv2.cuda.GaussianBlur(gpu_filtered, gpu_blurred, (3, 3), 0)  # type: ignore
        
        # Sharpen the image
        gpu_sharpened = self._sharpen_gpu_cuda(gpu_blurred)
        
        # Download result from GPU
        result = gpu_sharpened.download()  # type: ignore
        return result
    
    def _enhance_image_opencl(self, image: np.ndarray) -> np.ndarray:
        """OpenCL-accelerated image enhancement"""
        # OpenCL operations are handled automatically by OpenCV when enabled
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Apply CLAHE (OpenCL accelerated automatically)
        if len(image_rgb.shape) == 3:
            lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            lab = cv2.merge([l, a, b])
            image_rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            image_rgb = clahe.apply(image_rgb)
        
        # Apply bilateral filter (OpenCL accelerated)
        image_rgb = cv2.bilateralFilter(image_rgb, 9, 75, 75)
        
        # Sharpen the image
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(image_rgb, -1, kernel)
        image_rgb = cv2.addWeighted(image_rgb, 0.7, sharpened, 0.3, 0)
        
        # Gamma correction
        gamma = 1.2
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        image_rgb = cv2.LUT(image_rgb, table)
        
        return image_rgb
    
    def _enhance_image_cpu_optimized(self, image: np.ndarray) -> np.ndarray:
        """Highly optimized CPU image enhancement - faster than GPU for small images"""
        # Enable all CPU optimizations
        cv2.setNumThreads(0)  # Use all available cores
        cv2.setUseOptimized(True)  # Enable optimized code paths
        
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Simplified but effective enhancement - much faster
        if len(image_rgb.shape) == 3:
            # Convert to YUV for faster processing
            yuv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2YUV)
            
            # Apply CLAHE only to Y channel (luminance)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            yuv[:,:,0] = clahe.apply(yuv[:,:,0])
            
            # Convert back
            image_rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
        else:
            # Grayscale
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            image_rgb = clahe.apply(image_rgb)
        
        # Skip bilateral filter for speed - use faster Gaussian blur instead
        image_rgb = cv2.GaussianBlur(image_rgb, (3, 3), 0)
        
        # Simple sharpening with smaller kernel
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        image_rgb = cv2.filter2D(image_rgb, -1, kernel)
        
        return image_rgb
    
    def _sharpen_gpu_cuda(self, gpu_img):
        """CUDA-based image sharpening"""
        try:
            # Create sharpening kernel
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
            
            # Apply convolution filter
            gpu_sharpened = cv2.cuda_GpuMat()  # type: ignore
            cv2.cuda.filter2D(gpu_img, -1, kernel, gpu_sharpened)  # type: ignore
            
            # Blend with original
            gpu_result = cv2.cuda_GpuMat()  # type: ignore
            cv2.cuda.addWeighted(gpu_img, 0.7, gpu_sharpened, 0.3, 0, gpu_result)  # type: ignore
            
            return gpu_result
        except Exception as e:
            return gpu_img
    
    def resize_gpu(self, image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """GPU-accelerated image resizing"""
        try:
            if self.gpu_manager.cuda_available and hasattr(cv2, 'cuda'):
                gpu_img = cv2.cuda_GpuMat()  # type: ignore
                gpu_img.upload(image)  # type: ignore
                
                gpu_resized = cv2.cuda_GpuMat()  # type: ignore
                cv2.cuda.resize(gpu_img, gpu_resized, size, interpolation=cv2.INTER_CUBIC)  # type: ignore
                
                return gpu_resized.download()  # type: ignore
            else:
                # OpenCL or CPU fallback
                return cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)
        except Exception as e:
            return cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)
    
    def detect_faces_gpu_optimized(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Fast CPU-optimized face detection - GPU overhead not worth it for face detection"""
        # For face detection, CPU is actually faster due to GPU overhead
        # Use optimized CPU detection instead
        
        try:
            import face_recognition
            FACE_RECOGNITION_AVAILABLE = True
        except ImportError:
            FACE_RECOGNITION_AVAILABLE = False
            # Fallback to empty list if face_recognition not available
            print("⚠️ face_recognition not available, returning empty face list")
            return []
        
        # Enable CPU optimizations
        cv2.setNumThreads(0)
        cv2.setUseOptimized(True)
        
        # Use HOG model for speed (much faster than CNN)
        # Only use CNN for very high-resolution images
        height, width = image.shape[:2]
        image_size = height * width
        
        if image_size > 2000000:  # 2MP+ use CNN for accuracy
            model = 'cnn'
            upsamples = 1
        else:  # Smaller images use HOG for speed
            model = 'hog'
            upsamples = 1
        
        try:
            # Single-scale detection for speed
            face_locations = face_recognition.face_locations(
                image, 
                number_of_times_to_upsample=upsamples,
                model=model
            )
            
            return face_locations
            
        except Exception as e:
            pass
            # Fallback to HOG if CNN fails
            try:
                face_locations = face_recognition.face_locations(
                    image, 
                    number_of_times_to_upsample=0,
                    model='hog'
                )
                return face_locations
            except:
                return []
    
    def _is_same_face(self, loc1: Tuple[int, int, int, int], loc2: Tuple[int, int, int, int], threshold: int = 50) -> bool:
        """Check if two face locations represent the same face"""
        top1, right1, bottom1, left1 = loc1
        top2, right2, bottom2, left2 = loc2
        
        center1 = ((left1 + right1) // 2, (top1 + bottom1) // 2)
        center2 = ((left2 + right2) // 2, (top2 + bottom2) // 2)
        
        distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
        return distance < threshold
    
    def get_gpu_status(self) -> dict:
        """Get GPU processing status"""
        return self.gpu_manager.get_status()

# Global GPU image processor instance
gpu_processor = GPUImageProcessor()
