"""
OCR Engine using PaddleOCR for text extraction from images
"""

import logging
from typing import Optional, Dict, List, Tuple
from paddleocr import PaddleOCR
import numpy as np
import cv2
from utils import ImageProcessor, constants

logger = logging.getLogger(__name__)


class OCREngine:
    """Handle OCR operations using PaddleOCR"""
    
    def __init__(self):
        """Initialize OCR engine with PaddleOCR"""
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                use_gpu=constants.OCR_USE_GPU,
                show_log=False
            )
            logger.info("OCR Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OCR Engine: {str(e)}")
            raise
    
    def extract_text(self, image_path: str) -> Optional[str]:
        """
        Extract text from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text or None if failed
        """
        try:
            # Load and preprocess image
            image = ImageProcessor.load_image(image_path)
            if image is None:
                return None
            
            # Resize if needed
            image = ImageProcessor.resize_image(image)
            
            # Preprocess for better OCR
            processed = ImageProcessor.preprocess_image(image)
            
            # Run OCR
            logger.info(f"Running OCR on image: {image_path}")
            results = self.ocr.ocr(processed, cls=True)
            
            # Extract text from results
            extracted_text = self._parse_ocr_results(results)
            logger.info(f"Successfully extracted {len(extracted_text)} characters")
            
            return extracted_text
        
        except Exception as e:
            logger.error(f"Error during OCR: {str(e)}")
            return None
    
    def extract_text_with_details(self, image_path: str) -> Optional[Dict]:
        """
        Extract text with detailed information (coordinates, confidence)
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with text details or None if failed
        """
        try:
            # Load and preprocess image
            image = ImageProcessor.load_image(image_path)
            if image is None:
                return None
            
            # Resize if needed
            image = ImageProcessor.resize_image(image)
            
            # Preprocess for better OCR
            processed = ImageProcessor.preprocess_image(image)
            
            # Run OCR
            logger.info(f"Running detailed OCR on image: {image_path}")
            results = self.ocr.ocr(processed, cls=True)
            
            # Parse results with details
            details = self._parse_ocr_results_detailed(results)
            logger.info(f"Successfully extracted {len(details['text'])} characters with details")
            
            return details
        
        except Exception as e:
            logger.error(f"Error during detailed OCR: {str(e)}")
            return None
    
    def _parse_ocr_results(self, results: List) -> str:
        """
        Parse OCR results to extract text
        
        Args:
            results: PaddleOCR results
            
        Returns:
            Extracted text
        """
        text_lines = []
        
        if results is None or len(results) == 0:
            return ""
        
        for page in results:
            if page is None:
                continue
            
            for line in page:
                if line and len(line) >= 2:
                    text = line[1][0]  # Extract text
                    confidence = line[1][1]  # Extract confidence
                    
                    # Only include text with sufficient confidence
                    if confidence >= constants.OCR_CONFIDENCE_THRESHOLD:
                        text_lines.append(text)
        
        return "\n".join(text_lines)
    
    def _parse_ocr_results_detailed(self, results: List) -> Dict:
        """
        Parse OCR results with detailed information
        
        Args:
            results: PaddleOCR results
            
        Returns:
            Dictionary with detailed text information
        """
        text_lines = []
        confidences = []
        coordinates = []
        
        if results is None or len(results) == 0:
            return {
                "text": "",
                "lines": [],
                "confidences": [],
                "coordinates": []
            }
        
        for page in results:
            if page is None:
                continue
            
            for line in page:
                if line and len(line) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    coords = line[0]  # Bounding box coordinates
                    
                    if confidence >= constants.OCR_CONFIDENCE_THRESHOLD:
                        text_lines.append(text)
                        confidences.append(confidence)
                        coordinates.append(coords)
        
        return {
            "text": "\n".join(text_lines),
            "lines": text_lines,
            "confidences": confidences,
            "coordinates": coordinates
        }
    
    def extract_text_regions(self, image_path: str) -> Optional[List[Dict]]:
        """
        Extract text by regions with bounding boxes
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of text regions with coordinates
        """
        try:
            image = ImageProcessor.load_image(image_path)
            if image is None:
                return None
            
            image = ImageProcessor.resize_image(image)
            processed = ImageProcessor.preprocess_image(image)
            
            results = self.ocr.ocr(processed, cls=True)
            
            regions = []
            if results is not None:
                for page in results:
                    if page is None:
                        continue
                    
                    for line in page:
                        if line and len(line) >= 2:
                            region = {
                                "text": line[1][0],
                                "confidence": line[1][1],
                                "coordinates": line[0]
                            }
                            if region["confidence"] >= constants.OCR_CONFIDENCE_THRESHOLD:
                                regions.append(region)
            
            return regions
        
        except Exception as e:
            logger.error(f"Error extracting text regions: {str(e)}")
            return None
    
    def get_statistics(self, extracted_text: str) -> Dict:
        """
        Get statistics about extracted text
        
        Args:
            extracted_text: Extracted text from OCR
            
        Returns:
            Dictionary with text statistics
        """
        return {
            "total_characters": len(extracted_text),
            "total_words": len(extracted_text.split()),
            "total_lines": len(extracted_text.split('\n')),
            "non_whitespace_characters": len(extracted_text.replace(" ", "").replace("\n", "")),
            "unique_characters": len(set(extracted_text)),
        }
