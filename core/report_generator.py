"""
Report generation for comparison results
"""

import logging
from typing import Dict, Optional
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from utils import constants

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate comparison reports in multiple formats"""
    
    def __init__(self):
        """Initialize report generator"""
        logger.info("Report Generator initialized")
    
    def generate_text_report(self, comparison_result: Dict, output_path: str) -> bool:
        """
        Generate plain text report
        
        Args:
            comparison_result: Comparison results dictionary
            output_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write(f"{constants.APP_NAME} - Text Comparison Report\n")
                f.write("="*80 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                
                # Statistics
                stats = comparison_result.get("statistics", {})
                f.write("STATISTICS\n")
                f.write("-"*80 + "\n")
                f.write(f"Overall Similarity: {comparison_result.get('overall_similarity', 0):.2f}%\n")
                f.write(f"Image Total Characters: {stats.get('image_total_chars', 0)}\n")
                f.write(f"Provided Total Characters: {stats.get('provided_total_chars', 0)}\n")
                f.write(f"Image Total Words: {stats.get('image_total_words', 0)}\n")
                f.write(f"Provided Total Words: {stats.get('provided_total_words', 0)}\n")
                f.write(f"Image Total Lines: {stats.get('image_total_lines', 0)}\n")
                f.write(f"Provided Total Lines: {stats.get('provided_total_lines', 0)}\n")
                f.write("\n")
                
                # Character Level Comparison
                char_comp = comparison_result.get("character_level", {})
                f.write("CHARACTER LEVEL COMPARISON\n")
                f.write("-"*80 + "\n")
                f.write(f"Matched Characters: {char_comp.get('matched', 0)}\n")
                f.write(f"Missing Characters: {len(char_comp.get('missing', []))}\n")
                f.write(f"Extra Characters: {len(char_comp.get('extra', []))}\n")
                f.write(f"Changed Characters: {len(char_comp.get('changed', []))}\n")
                f.write("\n")
                
                # Word Level Comparison
                word_comp = comparison_result.get("word_level", {})
                f.write("WORD LEVEL COMPARISON\n")
                f.write("-"*80 + "\n")
                f.write(f"Matched Words: {word_comp.get('matched', 0)}\n")
                f.write(f"Missing Words: {len(word_comp.get('missing', []))}\n")
                f.write(f"Extra Words: {len(word_comp.get('extra', []))}\n")
                f.write(f"Misspelled Words: {len(word_comp.get('misspelled', []))}\n")
                f.write("\n")
                
                # Missing Characters Details
                if char_comp.get('missing'):
                    f.write("MISSING CHARACTERS (In Image but not in Provided Text)\n")
                    f.write("-"*80 + "\n")
                    for i, item in enumerate(char_comp['missing'][:20], 1):
                        f.write(f"{i}. Character: '{item['character']}' at position {item['position']}\n")
                        f.write(f"   Context: ...{item['context']}...\n")
                    if len(char_comp['missing']) > 20:
                        f.write(f"... and {len(char_comp['missing']) - 20} more\n")
                    f.write("\n")
                
                # Extra Characters Details
                if char_comp.get('extra'):
                    f.write("EXTRA CHARACTERS (In Provided Text but not in Image)\n")
                    f.write("-"*80 + "\n")
                    for i, item in enumerate(char_comp['extra'][:20], 1):
                        f.write(f"{i}. Character: '{item['character']}' at position {item['position']}\n")
                        f.write(f"   Context: ...{item['context']}...\n")
                    if len(char_comp['extra']) > 20:
                        f.write(f"... and {len(char_comp['extra']) - 20} more\n")
                    f.write("\n")
                
                # Missing Words Details
                if word_comp.get('missing'):
                    f.write("MISSING WORDS (In Image but not in Provided Text)\n")
                    f.write("-"*80 + "\n")
                    for i, item in enumerate(word_comp['missing'][:20], 1):
                        f.write(f"{i}. Word: '{item['word']}' at position {item['position']}\n")
                    if len(word_comp['missing']) > 20:
                        f.write(f"... and {len(word_comp['missing']) - 20} more\n")
                    f.write("\n")
                
                # Extra Words Details
                if word_comp.get('extra'):
                    f.write("EXTRA WORDS (In Provided Text but not in Image)\n")
                    f.write("-"*80 + "\n")
                    for i, item in enumerate(word_comp['extra'][:20], 1):
                        f.write(f"{i}. Word: '{item['word']}' at position {item['position']}\n")
                    if len(word_comp['extra']) > 20:
                        f.write(f"... and {len(word_comp['extra']) - 20} more\n")
                    f.write("\n")
                
                # Misspelled Words
                if word_comp.get('misspelled'):
                    f.write("MISSPELLED WORDS (Typos and Changes)\n")
                    f.write("-"*80 + "\n")
                    for i, item in enumerate(word_comp['misspelled'][:20], 1):
                        f.write(f"{i}. Image: '{item['image_word']}' -> Provided: '{item['provided_word']}'\n")
                        f.write(f"   Similarity: {item['similarity']*100:.2f}%\n")
                    if len(word_comp['misspelled']) > 20:
                        f.write(f"... and {len(word_comp['misspelled']) - 20} more\n")
                    f.write("\n")
                
                # Recommendations
                f.write("RECOMMENDATIONS\n")
                f.write("-"*80 + "\n")
                similarity = comparison_result.get('overall_similarity', 0)
                if similarity >= 95:
                    f.write("✓ Texts are nearly identical. Minor adjustments may be needed.\n")
                elif similarity >= 85:
                    f.write("✓ Texts are very similar. Review the differences above.\n")
                elif similarity >= 70:
                    f.write("⚠ Texts are moderately similar. Multiple corrections needed.\n")
                else:
                    f.write("✗ Texts differ significantly. Major corrections needed.\n")
                
                if char_comp.get('missing'):
                    f.write(f"  - Add {len(char_comp['missing'])} missing characters\n")
                if char_comp.get('extra'):
                    f.write(f"  - Remove {len(char_comp['extra'])} extra characters\n")
                if word_comp.get('missing'):
                    f.write(f"  - Add {len(word_comp['missing'])} missing words\n")
                if word_comp.get('extra'):
                    f.write(f"  - Remove {len(word_comp['extra'])} extra words\n")
                
                logger.info(f"Text report generated successfully: {output_path}")
                return True
        
        except Exception as e:
            logger.error(f"Error generating text report: {str(e)}")
            return False
    
    def generate_html_report(self, image_text: str, provided_text: str, 
                            comparison_result: Dict, output_path: str) -> bool:
        """
        Generate HTML report with highlights
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            comparison_result: Comparison results
            output_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            html_content = self._generate_html_content(image_text, provided_text, comparison_result)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated successfully: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return False
    
    def _generate_html_content(self, image_text: str, provided_text: str, 
                              comparison_result: Dict) -> str:
        """
        Generate HTML content for report
        
        Args:
            image_text: Text from image
            provided_text: Provided text
            comparison_result: Comparison results
            
        Returns:
            HTML content as string
        """
        char_comp = comparison_result.get("character_level", {})
        word_comp = comparison_result.get("word_level", {})
        stats = comparison_result.get("statistics", {})
        similarity = comparison_result.get('overall_similarity', 0)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{constants.APP_NAME} - Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{
            margin: 0;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            background-color: #ecf0f1;
            padding: 15px;
            border-left: 4px solid #3498db;
            border-radius: 3px;
        }}
        .stat-box strong {{
            color: #2c3e50;
        }}
        .stat-value {{
            font-size: 24px;
            color: #3498db;
            margin-top: 5px;
        }}
        .missing {{ color: #e74c3c; font-weight: bold; }}
        .extra {{ color: #27ae60; font-weight: bold; }}
        .changed {{ color: #f39c12; font-weight: bold; }}
        .matched {{ color: #3498db; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .comparison-box {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .text-box {{
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
            background-color: #f9f9f9;
            font-family: monospace;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .generated {{
            text-align: right;
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{constants.APP_NAME}</h1>
        <p>Text Comparison Report</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="container">
        <h2>Overall Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <strong>Similarity Score</strong>
                <div class="stat-value">{similarity:.2f}%</div>
            </div>
            <div class="stat-box">
                <strong>Total Characters (Image)</strong>
                <div class="stat-value">{stats.get('image_total_chars', 0)}</div>
            </div>
            <div class="stat-box">
                <strong>Total Characters (Provided)</strong>
                <div class="stat-value">{stats.get('provided_total_chars', 0)}</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <h2>Character Level Comparison</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>Matched Characters</td>
                <td class="matched">{char_comp.get('matched', 0)}</td>
            </tr>
            <tr>
                <td>Missing Characters (in image but not in provided)</td>
                <td class="missing">{len(char_comp.get('missing', []))}</td>
            </tr>
            <tr>
                <td>Extra Characters (in provided but not in image)</td>
                <td class="extra">{len(char_comp.get('extra', []))}</td>
            </tr>
            <tr>
                <td>Changed Characters</td>
                <td class="changed">{len(char_comp.get('changed', []))}</td>
            </tr>
        </table>
    </div>
    
    <div class="container">
        <h2>Word Level Comparison</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>Matched Words</td>
                <td class="matched">{word_comp.get('matched', 0)}</td>
            </tr>
            <tr>
                <td>Missing Words</td>
                <td class="missing">{len(word_comp.get('missing', []))}</td>
            </tr>
            <tr>
                <td>Extra Words</td>
                <td class="extra">{len(word_comp.get('extra', []))}</td>
            </tr>
            <tr>
                <td>Misspelled Words</td>
                <td class="changed">{len(word_comp.get('misspelled', []))}</td>
            </tr>
        </table>
    </div>
    
    <div class="comparison-box">
        <div>
            <h2>Image Text</h2>
            <div class="text-box">{image_text[:2000]}</div>
        </div>
        <div>
            <h2>Provided Text</h2>
            <div class="text-box">{provided_text[:2000]}</div>
        </div>
    </div>
    
    <div class="generated">Report generated by {constants.APP_NAME} v{constants.APP_VERSION}</div>
</body>
</html>
        """
        return html
