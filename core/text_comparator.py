"""
Text comparison engine for multi-level difference detection
"""

import logging
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher, unified_diff
from Levenshtein import ratio as levenshtein_ratio, distance as levenshtein_distance
from utils import constants

logger = logging.getLogger(__name__)


class TextComparator:
    """Compare texts at multiple levels (character, word, line)"""
    
    def __init__(self):
        """Initialize text comparator"""
        logger.info("Text Comparator initialized")
    
    def compare(self, image_text: str, provided_text: str) -> Dict:
        """
        Perform comprehensive comparison of two texts
        
        Args:
            image_text: Text extracted from image
            provided_text: Text provided by user
            
        Returns:
            Dictionary with comparison results
        """
        try:
            logger.info("Starting comprehensive text comparison")
            
            return {
                "character_level": self.compare_character_level(image_text, provided_text),
                "word_level": self.compare_word_level(image_text, provided_text),
                "line_level": self.compare_line_level(image_text, provided_text),
                "overall_similarity": self.calculate_similarity(image_text, provided_text),
                "statistics": self.get_comparison_statistics(image_text, provided_text)
            }
        
        except Exception as e:
            logger.error(f"Error during comparison: {str(e)}")
            return {}
    
    def compare_character_level(self, image_text: str, provided_text: str) -> Dict:
        """
        Compare texts character by character
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            
        Returns:
            Character-level comparison results
        """
        image_chars = list(image_text)
        provided_chars = list(provided_text)
        
        matched = 0
        missing = []  # In image but not in provided
        extra = []    # In provided but not in image
        changed = []  # Different characters
        
        # Use SequenceMatcher for alignment
        matcher = SequenceMatcher(None, image_chars, provided_chars)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                matched += (i2 - i1)
            elif tag == 'delete':
                for k in range(i1, i2):
                    missing.append({
                        "character": image_chars[k],
                        "position": k,
                        "context": ''.join(image_chars[max(0, k-5):k+5])
                    })
            elif tag == 'insert':
                for k in range(j1, j2):
                    extra.append({
                        "character": provided_chars[k],
                        "position": k,
                        "context": ''.join(provided_chars[max(0, k-5):k+5])
                    })
            elif tag == 'replace':
                for k in range(i2 - i1):
                    changed.append({
                        "image_char": image_chars[i1 + k] if i1 + k < len(image_chars) else "",
                        "provided_char": provided_chars[j1 + k] if j1 + k < len(provided_chars) else "",
                        "position": i1 + k,
                        "context": ''.join(image_chars[max(0, i1+k-5):i1+k+5])
                    })
        
        return {
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "changed": changed,
            "total_image_chars": len(image_chars),
            "total_provided_chars": len(provided_chars)
        }
    
    def compare_word_level(self, image_text: str, provided_text: str) -> Dict:
        """
        Compare texts at word level
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            
        Returns:
            Word-level comparison results
        """
        image_words = image_text.split()
        provided_words = provided_text.split()
        
        matched_words = []
        missing_words = []  # In image but not in provided
        extra_words = []    # In provided but not in image
        misspelled = []     # Words with typos
        
        # Use SequenceMatcher for word alignment
        matcher = SequenceMatcher(None, image_words, provided_words)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    matched_words.append(image_words[i1 + k])
            elif tag == 'delete':
                for k in range(i1, i2):
                    missing_words.append({
                        "word": image_words[k],
                        "position": k
                    })
            elif tag == 'insert':
                for k in range(j1, j2):
                    extra_words.append({
                        "word": provided_words[k],
                        "position": k
                    })
            elif tag == 'replace':
                for k in range(i2 - i1):
                    if i1 + k < len(image_words) and j1 + k < len(provided_words):
                        image_word = image_words[i1 + k]
                        provided_word = provided_words[j1 + k]
                        similarity = levenshtein_ratio(image_word, provided_word)
                        
                        if similarity > constants.WORD_SIMILARITY_THRESHOLD:
                            misspelled.append({
                                "image_word": image_word,
                                "provided_word": provided_word,
                                "similarity": similarity,
                                "position": i1 + k
                            })
                        else:
                            missing_words.append({"word": image_word, "position": i1 + k})
                            extra_words.append({"word": provided_word, "position": j1 + k})
        
        return {
            "matched": len(matched_words),
            "matched_words": matched_words,
            "missing": missing_words,
            "extra": extra_words,
            "misspelled": misspelled,
            "total_image_words": len(image_words),
            "total_provided_words": len(provided_words)
        }
    
    def compare_line_level(self, image_text: str, provided_text: str) -> Dict:
        """
        Compare texts line by line
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            
        Returns:
            Line-level comparison results
        """
        image_lines = image_text.split('\n')
        provided_lines = provided_text.split('\n')
        
        line_diffs = []
        matched_lines = 0
        
        # Use unified_diff for line comparison
        diff = list(unified_diff(image_lines, provided_lines, lineterm='', fromfile='Image', tofile='Provided'))
        
        matcher = SequenceMatcher(None, image_lines, provided_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                matched_lines += (i2 - i1)
            else:
                for k in range(max(i2 - i1, j2 - j1)):
                    image_line = image_lines[i1 + k] if i1 + k < len(image_lines) else ""
                    provided_line = provided_lines[j1 + k] if j1 + k < len(provided_lines) else ""
                    
                    line_diffs.append({
                        "line_number": i1 + k + 1,
                        "image_line": image_line,
                        "provided_line": provided_line,
                        "type": tag
                    })
        
        return {
            "matched_lines": matched_lines,
            "total_image_lines": len(image_lines),
            "total_provided_lines": len(provided_lines),
            "differences": line_diffs,
            "unified_diff": diff
        }
    
    def calculate_similarity(self, image_text: str, provided_text: str) -> float:
        """
        Calculate overall similarity percentage
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            
        Returns:
            Similarity percentage (0-100)
        """
        if constants.SIMILARITY_METHOD == "levenshtein":
            similarity = levenshtein_ratio(image_text, provided_text)
        else:  # default to difflib
            matcher = SequenceMatcher(None, image_text, provided_text)
            similarity = matcher.ratio()
        
        return round(similarity * 100, 2)
    
    def get_comparison_statistics(self, image_text: str, provided_text: str) -> Dict:
        """
        Get statistical summary of comparison
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            
        Returns:
            Statistics dictionary
        """
        return {
            "image_total_chars": len(image_text),
            "provided_total_chars": len(provided_text),
            "image_total_words": len(image_text.split()),
            "provided_total_words": len(provided_text.split()),
            "image_total_lines": len(image_text.split('\n')),
            "provided_total_lines": len(provided_text.split('\n')),
            "image_non_whitespace": len(image_text.replace(" ", "").replace("\n", "")),
            "provided_non_whitespace": len(provided_text.replace(" ", "").replace("\n", ""))
        }
    
    def highlight_differences(self, image_text: str, provided_text: str) -> Dict:
        """
        Generate highlighted version of texts showing differences
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            
        Returns:
            Dictionary with highlighted texts
        """
        char_comparison = self.compare_character_level(image_text, provided_text)
        
        image_highlighted = list(image_text)
        provided_highlighted = list(provided_text)
        
        # Mark missing characters (in image but not in provided)
        for item in char_comparison["missing"]:
            pos = item["position"]
            if pos < len(image_highlighted):
                image_highlighted[pos] = f"[MISSING:{image_highlighted[pos]}]"
        
        # Mark extra characters (in provided but not in image)
        offset = 0
        for item in char_comparison["extra"]:
            pos = item["position"] + offset
            if pos < len(provided_highlighted):
                provided_highlighted.insert(pos, f"[EXTRA:{provided_highlighted[pos]}]")
                offset += 1
        
        return {
            "image_highlighted": ''.join(image_highlighted),
            "provided_highlighted": ''.join(provided_highlighted),
            "comparison": char_comparison
        }
