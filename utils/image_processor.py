"""
Image processing utilities
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handle image loading and preprocessing"""
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        Load image from file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            OpenCV image array or None if failed
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            logger.info(f"Successfully loaded image: {image_path}")
            return image
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None
    
    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: OpenCV image array
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
            
            # Dilate and erode to remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            logger.info("Image preprocessing completed successfully")
            return processed
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 2000, max_height: int = 2000) -> np.ndarray:
        """
        Resize image if it exceeds maximum dimensions
        
        Args:
            image: OpenCV image array
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Resized image
        """
        try:
            height, width = image.shape[:2]
            
            if width <= max_width and height <= max_height:
                return image
            
            # Calculate aspect ratio
            aspect_ratio = width / height
            
            if width > max_width:
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
            
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"Image resized from {width}x{height} to {new_width}x{new_height}")
            return resized
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return image
    
    @staticmethod
    def adjust_contrast(image: np.ndarray, alpha: float = 1.2, beta: int = 30) -> np.ndarray:
        """
        Adjust image contrast and brightness
        
        Args:
            image: OpenCV image array
            alpha: Contrast factor (1.0-3.0)
            beta: Brightness offset
            
        Returns:
            Adjusted image
        """
        try:
            adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
            return adjusted
        except Exception as e:
            logger.error(f"Error adjusting contrast: {str(e)}")
            return image
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by specified angle
        
        Args:
            image: OpenCV image array
            angle: Rotation angle in degrees
            
        Returns:
            Rotated image
        """
        try:
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, matrix, (width, height))
            return rotated
        except Exception as e:
            logger.error(f"Error rotating image: {str(e)}")
            return image
    
    @staticmethod
    def convert_to_pil(cv_image: np.ndarray) -> Image.Image:
        """
        Convert OpenCV image to PIL Image
        
        Args:
            cv_image: OpenCV image array
            
        Returns:
            PIL Image
        """
        try:
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            return pil_image
        except Exception as e:
            logger.error(f"Error converting image: {str(e)}")
            return None
    
    @staticmethod
    def convert_to_cv2(pil_image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to OpenCV image
        
        Args:
            pil_image: PIL Image
            
        Returns:
            OpenCV image array
        """
        try:
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return cv_image
        except Exception as e:
            logger.error(f"Error converting image: {str(e)}")
            return None
    
    @staticmethod
    def get_image_info(image: np.ndarray) -> dict:
        """
        Get image information
        
        Args:
            image: OpenCV image array
            
        Returns:
            Dictionary with image info
        """
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        return {
            "width": width,
            "height": height,
            "channels": channels,
            "size_pixels": width * height,
        }
    
    @staticmethod
    def crop_image(image: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """
        Crop image to specified region
        
        Args:
            image: OpenCV image array
            x1, y1: Top-left coordinates
            x2, y2: Bottom-right coordinates
            
        Returns:
            Cropped image
        """
        try:
            cropped = image[y1:y2, x1:x2]
            return cropped
        except Exception as e:
            logger.error(f"Error cropping image: {str(e)}")
            return image
    
    @staticmethod
    def auto_rotate_document(image: np.ndarray) -> np.ndarray:
        """
        Automatically rotate document image to correct orientation
        
        Args:
            image: OpenCV image array
            
        Returns:
            Rotated image
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            # Detect lines
            lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
            
            if lines is not None:
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angle = np.degrees(theta) - 90
                    angles.append(angle)
                
                # Get median angle
                median_angle = np.median(angles)
                
                if abs(median_angle) > 0.5:
                    image = ImageProcessor.rotate_image(image, median_angle)
            
            return image
        except Exception as e:
            logger.error(f"Error auto-rotating image: {str(e)}")
            return image
