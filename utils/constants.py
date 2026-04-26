"""
Application constants and configuration
"""

# Application Info
APP_NAME = "Text Image Comparison Tool"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Abhishek Kumar Rawat"

# Window Configuration
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 700

# Colors for Highlighting
COLOR_MISSING = "#FF4444"      # Red - Missing text (in image but not in provided)
COLOR_EXTRA = "#44AA44"        # Green - Extra text (in provided but not in image)
COLOR_CHANGED = "#FFAA00"      # Yellow - Changed/Mismatched text
COLOR_MATCHED = "#4444FF"      # Blue - Correct matches
COLOR_BACKGROUND = "#FFFFFF"   # White background
COLOR_TEXT = "#000000"         # Black text

# Highlighting Configuration
HIGHLIGHT_STYLE = {
    "missing": {"background": COLOR_MISSING, "color": "white"},
    "extra": {"background": COLOR_EXTRA, "color": "white"},
    "changed": {"background": COLOR_CHANGED, "color": "white"},
    "matched": {"background": COLOR_MATCHED, "color": "white"},
}

# OCR Configuration
OCR_LANGUAGE = ["en", "ch"]    # English and Chinese
OCR_USE_GPU = False             # Set to True if NVIDIA GPU available
OCR_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for text recognition

# Comparison Configuration
SIMILARITY_THRESHOLD = 0.85     # Threshold for word matching
WORD_SIMILARITY_THRESHOLD = 0.8 # For fuzzy word matching
CASE_SENSITIVE = True           # Case-sensitive comparison
IGNORE_WHITESPACE = False       # Ignore whitespace differences

# File Extensions
SUPPORTED_IMAGE_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif")
SUPPORTED_IMAGE_FILTER = "Image Files (*.jpg *.jpeg *.png *.bmp *.gif *.tiff);;All Files (*)"

# Export Configuration
EXPORT_PDF_MARGIN = 50
EXPORT_PDF_FONTSIZE = 10
EXPORT_PDF_TITLE_FONTSIZE = 14

# Performance Configuration
MAX_IMAGE_SIZE = (4000, 4000)   # Maximum image dimensions for processing
MAX_TEXT_LENGTH = 100000        # Maximum text length for comparison
PROCESSING_TIMEOUT = 300        # Timeout for OCR processing (seconds)

# UI Configuration
FONT_FAMILY = "Consolas"        # Monospace font for code-like display
FONT_SIZE = 10
FONT_SIZE_TITLE = 14
FONT_SIZE_LABEL = 11

# Comparison Display
CONTEXT_LINES = 2               # Lines to show around differences
MAX_DIFF_DISPLAY_CHARS = 500    # Maximum characters to show in diff

# Threading
MAX_WORKERS = 2                 # Max concurrent OCR operations
OCR_THREAD_PRIORITY = "high"    # Thread priority for OCR

# Similarity Calculation
SIMILARITY_METHOD = "levenshtein"  # Options: "levenshtein", "jaro", "difflib"

# Report Generation
INCLUDE_STATISTICS = True
INCLUDE_DETAILED_DIFF = True
INCLUDE_CHARACTER_MAP = True
INCLUDE_WORD_COMPARISON = True

# Cache Configuration
ENABLE_CACHE = True
CACHE_DIRECTORY = "./cache"
CACHE_SIZE_MB = 500

# Logging
LOG_LEVEL = "INFO"              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "text_comparison.log"
ENABLE_CONSOLE_LOGGING = True

# Batch Processing
BATCH_MODE_ENABLED = True
MAX_BATCH_SIZE = 10

# Keyboard Shortcuts
SHORTCUT_OPEN_IMAGE = "Ctrl+O"
SHORTCUT_COMPARE = "Ctrl+Enter"
SHORTCUT_EXPORT = "Ctrl+S"
SHORTCUT_CLEAR = "Ctrl+L"
SHORTCUT_EXIT = "Ctrl+Q"
