import asyncio
import sys
sys.path.append('.')

# Import the resume function from server.py
from pathlib import Path
import fitz  # PyMuPDF for PDFs

async def test_resume():
    """Test the resume function directly"""
    try:
        # Path to your local resume file (PDF, DOCX, or HTML)
        resume_path = Path("resume.pdf")
        
        if not resume_path.exists():
            return "<error>Resume file not found. Please place your resume.pdf in the same directory as this script.</error>"
        
        doc = fitz.open(resume_path)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        
        # Convert to markdown format
        if text.strip():
            # Simple text to markdown conversion
            lines = text.split('\n')
            markdown_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    # Simple heuristic: if line is all caps or ends with colon, make it a header
                    if line.isupper() or line.endswith(':'):
                        markdown_lines.append(f"## {line}")
                    else:
                        markdown_lines.append(line)
                else:
                    markdown_lines.append("")
            return '\n'.join(markdown_lines)
        else:
            return "<error>No text content found in resume PDF</error>"

    except ImportError:
        return "<error>PyMuPDF (fitz) not installed. Please install it with: pip install PyMuPDF</error>"
    except Exception as e:
        return f"<error>Could not read or convert resume: {str(e)}</error>"

if __name__ == "__main__":
    result = asyncio.run(test_resume())
    print("=" * 50)
    print("RESUME OUTPUT:")
    print("=" * 50)
    print(result)
    print("=" * 50) 