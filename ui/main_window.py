"""
Main PyQt6 GUI application window
"""

import sys
import os
import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QTextEdit, QTabWidget, QTableWidget, 
    QTableWidgetItem, QProgressBar, QSplitter, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QTextCursor, QTextCharFormat
from core import OCREngine, TextComparator, ReportGenerator
from utils import ImageProcessor, constants

logger = logging.getLogger(__name__)


class OCRWorker(QThread):
    """Worker thread for OCR processing"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path
    
    def run(self):
        try:
            ocr_engine = OCREngine()
            extracted_text = ocr_engine.extract_text(self.image_path)
            if extracted_text:
                self.finished.emit(extracted_text)
            else:
                self.error.emit("Failed to extract text from image")
        except Exception as e:
            self.error.emit(f"OCR Error: {str(e)}")


class ComparisonWorker(QThread):
    """Worker thread for text comparison"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, image_text: str, provided_text: str):
        super().__init__()
        self.image_text = image_text
        self.provided_text = provided_text
    
    def run(self):
        try:
            comparator = TextComparator()
            result = comparator.compare(self.image_text, self.provided_text)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Comparison Error: {str(e)}")


class TextComparisonApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.image_text = ""
        self.provided_text = ""
        self.comparison_result = {}
        
        self.init_ui()
        self.setup_styles()
        logger.info("Application initialized")
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle(f"{constants.APP_NAME} v{constants.APP_VERSION}")
        self.setGeometry(100, 100, constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)
        self.setMinimumSize(constants.MIN_WINDOW_WIDTH, constants.MIN_WINDOW_HEIGHT)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Top toolbar
        toolbar_layout = QHBoxLayout()
        
        # Select Image button
        select_image_btn = QPushButton("📁 Select Image")
        select_image_btn.clicked.connect(self.select_image)
        toolbar_layout.addWidget(select_image_btn)
        
        # Compare button
        compare_btn = QPushButton("🔍 Compare")
        compare_btn.clicked.connect(self.compare_texts)
        toolbar_layout.addWidget(compare_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_all)
        toolbar_layout.addWidget(clear_btn)
        
        # Export button
        export_btn = QPushButton("💾 Export Report")
        export_btn.clicked.connect(self.export_report)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Tab widget for different views
        tabs = QTabWidget()
        
        # Tab 1: Comparison View
        comparison_widget = self.create_comparison_view()
        tabs.addTab(comparison_widget, "📊 Comparison")
        
        # Tab 2: Statistics View
        stats_widget = self.create_statistics_view()
        tabs.addTab(stats_widget, "📈 Statistics")
        
        # Tab 3: Details View
        details_widget = self.create_details_view()
        tabs.addTab(details_widget, "📋 Details")
        
        main_layout.addWidget(tabs)
        
        main_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_comparison_view(self) -> QWidget:
        """Create comparison view with side-by-side text display"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Left side - Image text
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Text from Image:"))
        self.image_text_display = QTextEdit()
        self.image_text_display.setReadOnly(True)
        self.image_text_display.setFont(QFont(constants.FONT_FAMILY, constants.FONT_SIZE))
        left_layout.addWidget(self.image_text_display)
        
        # Right side - Provided text
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Provided Text:"))
        self.provided_text_display = QTextEdit()
        self.provided_text_display.setFont(QFont(constants.FONT_FAMILY, constants.FONT_SIZE))
        right_layout.addWidget(self.provided_text_display)
        
        # Add layouts to main layout
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)
        
        widget.setLayout(layout)
        return widget
    
    def create_statistics_view(self) -> QWidget:
        """Create statistics view"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Comparison Statistics:", font=QFont("Arial", 12, QFont.Weight.Bold)))
        
        # Create table for statistics
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.stats_table)
        
        # Similarity indicator
        layout.addWidget(QLabel("Overall Similarity:", font=QFont("Arial", 11, QFont.Weight.Bold)))
        self.similarity_bar = QProgressBar()
        layout.addWidget(self.similarity_bar)
        
        self.similarity_label = QLabel()
        layout.addWidget(self.similarity_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_details_view(self) -> QWidget:
        """Create detailed differences view"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tabs for different details
        details_tabs = QTabWidget()
        
        # Missing text
        self.missing_table = QTableWidget()
        self.missing_table.setColumnCount(2)
        self.missing_table.setHorizontalHeaderLabels(["Item", "Position"])
        details_tabs.addTab(self.missing_table, "Missing (In Image)")
        
        # Extra text
        self.extra_table = QTableWidget()
        self.extra_table.setColumnCount(2)
        self.extra_table.setHorizontalHeaderLabels(["Item", "Position"])
        details_tabs.addTab(self.extra_table, "Extra (In Provided)")
        
        # Changed text
        self.changed_table = QTableWidget()
        self.changed_table.setColumnCount(3)
        self.changed_table.setHorizontalHeaderLabels(["Image", "Provided", "Position"])
        details_tabs.addTab(self.changed_table, "Changed")
        
        layout.addWidget(details_tabs)
        widget.setLayout(layout)
        return widget
    
    def select_image(self):
        """Select image file"""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "Select Image",
                "",
                constants.SUPPORTED_IMAGE_FILTER
            )
            
            if file_path:
                self.image_path = file_path
                self.extract_text_from_image()
        
        except Exception as e:
            logger.error(f"Error selecting image: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error selecting image: {str(e)}")
    
    def extract_text_from_image(self):
        """Extract text from selected image"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Extracting text from image...")
            
            self.ocr_worker = OCRWorker(self.image_path)
            self.ocr_worker.finished.connect(self.on_ocr_finished)
            self.ocr_worker.error.connect(self.on_ocr_error)
            self.ocr_worker.start()
        
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error extracting text: {str(e)}")
    
    def on_ocr_finished(self, text: str):
        """Handle OCR completion"""
        self.image_text = text
        self.image_text_display.setText(self.image_text)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"Extracted {len(text)} characters from image")
        logger.info(f"OCR completed: {len(text)} characters extracted")
    
    def on_ocr_error(self, error: str):
        """Handle OCR error"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error")
        logger.error(f"OCR error: {error}")
        QMessageBox.critical(self, "OCR Error", error)
    
    def compare_texts(self):
        """Compare image text with provided text"""
        try:
            if not self.image_text:
                QMessageBox.warning(self, "Warning", "Please select an image first")
                return
            
            self.provided_text = self.provided_text_display.toPlainText()
            
            if not self.provided_text:
                QMessageBox.warning(self, "Warning", "Please enter text to compare")
                return
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Comparing texts...")
            
            self.comparison_worker = ComparisonWorker(self.image_text, self.provided_text)
            self.comparison_worker.finished.connect(self.on_comparison_finished)
            self.comparison_worker.error.connect(self.on_comparison_error)
            self.comparison_worker.start()
        
        except Exception as e:
            logger.error(f"Error comparing texts: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error comparing texts: {str(e)}")
    
    def on_comparison_finished(self, result: dict):
        """Handle comparison completion"""
        self.comparison_result = result
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Comparison completed")
        
        # Update statistics view
        self.update_statistics_view(result)
        
        # Update details view
        self.update_details_view(result)
        
        logger.info("Comparison completed successfully")
    
    def on_comparison_error(self, error: str):
        """Handle comparison error"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error")
        logger.error(f"Comparison error: {error}")
        QMessageBox.critical(self, "Comparison Error", error)
    
    def update_statistics_view(self, result: dict):
        """Update statistics display"""
        stats = result.get('statistics', {})
        similarity = result.get('overall_similarity', 0)
        char_comp = result.get('character_level', {})
        word_comp = result.get('word_level', {})
        
        # Update stats table
        self.stats_table.setRowCount(0)
        
        stats_data = [
            ("Overall Similarity", f"{similarity:.2f}%"),
            ("Image Total Characters", stats.get('image_total_chars', 0)),
            ("Provided Total Characters", stats.get('provided_total_chars', 0)),
            ("Image Total Words", stats.get('image_total_words', 0)),
            ("Provided Total Words", stats.get('provided_total_words', 0)),
            ("Matched Characters", char_comp.get('matched', 0)),
            ("Missing Characters", len(char_comp.get('missing', []))),
            ("Extra Characters", len(char_comp.get('extra', []))),
            ("Matched Words", word_comp.get('matched', 0)),
            ("Missing Words", len(word_comp.get('missing', []))),
            ("Extra Words", len(word_comp.get('extra', []))),
        ]
        
        for row, (metric, value) in enumerate(stats_data):
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem(metric))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(value)))
        
        # Update similarity bar
        self.similarity_bar.setValue(int(similarity))
        
        if similarity >= 95:
            self.similarity_label.setText(f"✓ Texts are nearly identical ({similarity:.2f}% match)")
            self.similarity_label.setStyleSheet("color: green; font-weight: bold;")
        elif similarity >= 85:
            self.similarity_label.setText(f"✓ Texts are very similar ({similarity:.2f}% match)")
            self.similarity_label.setStyleSheet("color: green; font-weight: bold;")
        elif similarity >= 70:
            self.similarity_label.setText(f"⚠ Texts are moderately similar ({similarity:.2f}% match)")
            self.similarity_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.similarity_label.setText(f"✗ Texts differ significantly ({similarity:.2f}% match)")
            self.similarity_label.setStyleSheet("color: red; font-weight: bold;")
    
    def update_details_view(self, result: dict):
        """Update detailed differences display"""
        char_comp = result.get('character_level', {})
        word_comp = result.get('word_level', {})
        
        # Update missing table
        self.missing_table.setRowCount(0)
        missing_items = char_comp.get('missing', [])
        for row, item in enumerate(missing_items[:100]):
            self.missing_table.insertRow(row)
            self.missing_table.setItem(row, 0, QTableWidgetItem(f"'{item['character']}'"))
            self.missing_table.setItem(row, 1, QTableWidgetItem(str(item['position'])))
        
        # Update extra table
        self.extra_table.setRowCount(0)
        extra_items = char_comp.get('extra', [])
        for row, item in enumerate(extra_items[:100]):
            self.extra_table.insertRow(row)
            self.extra_table.setItem(row, 0, QTableWidgetItem(f"'{item['character']}'"))
            self.extra_table.setItem(row, 1, QTableWidgetItem(str(item['position'])))
        
        # Update changed table
        self.changed_table.setRowCount(0)
        changed_items = char_comp.get('changed', [])
        for row, item in enumerate(changed_items[:100]):
            self.changed_table.insertRow(row)
            self.changed_table.setItem(row, 0, QTableWidgetItem(f"'{item['image_char']}'"))
            self.changed_table.setItem(row, 1, QTableWidgetItem(f"'{item['provided_char']}'"))
            self.changed_table.setItem(row, 2, QTableWidgetItem(str(item['position'])))
    
    def export_report(self):
        """Export comparison report"""
        try:
            if not self.comparison_result:
                QMessageBox.warning(self, "Warning", "Please perform comparison first")
                return
            
            file_dialog = QFileDialog()
            file_path, file_type = file_dialog.getSaveFileName(
                self,
                "Save Report As",
                "",
                "Text Files (*.txt);;HTML Files (*.html)"
            )
            
            if file_path:
                report_gen = ReportGenerator()
                
                if file_path.endswith('.html'):
                    success = report_gen.generate_html_report(
                        self.image_text,
                        self.provided_text,
                        self.comparison_result,
                        file_path
                    )
                else:
                    success = report_gen.generate_text_report(
                        self.comparison_result,
                        file_path
                    )
                
                if success:
                    self.statusBar().showMessage(f"Report saved: {file_path}")
                    QMessageBox.information(self, "Success", f"Report saved successfully\n{file_path}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save report")
        
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error exporting report: {str(e)}")
    
    def clear_all(self):
        """Clear all data"""
        self.image_path = None
        self.image_text = ""
        self.provided_text = ""
        self.comparison_result = {}
        self.image_text_display.clear()
        self.provided_text_display.clear()
        self.stats_table.setRowCount(0)
        self.missing_table.setRowCount(0)
        self.extra_table.setRowCount(0)
        self.changed_table.setRowCount(0)
        self.similarity_bar.setValue(0)
        self.similarity_label.clear()
        self.statusBar().showMessage("Ready")
        logger.info("Application cleared")
    
    def setup_styles(self):
        """Setup application styles"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #1f618d;
        }
        QTextEdit {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 5px;
            font-family: 'Consolas';
            font-size: 10pt;
        }
        QLabel {
            color: #2c3e50;
        }
        """
        self.setStyleSheet(style)
