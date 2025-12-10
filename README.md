# SummAI - Intelligent Text Summarization

A powerful web application for intelligent text summarization using advanced Natural
Language Processing (NLP) techniques. SummAI provides multiple summarization methods,
real-time analytics, and a modern, user-friendly interface.

## Features

- **Multiple Summarization Methods**
  - **Normal Mode**: Standard frequency-based summarization
  - **Business Insights Mode**: Enhanced summarization optimized for business content,
  prioritizing financial metrics, strategic insights, and key business terms

- **Customizable Summary Length**: Adjustable compression ratio from 10% to 90%

- **Text Analysis**
  - Keyword extraction using TF-IDF
  - Readability metrics (Flesch-Kincaid grade level, reading time)
  - Real-time word, character, and sentence counting

- **Analytics Dashboard**
  - Track total summaries generated
  - Monitor words processed and generated
  - View compression ratios
  - Method usage statistics
  - Daily statistics tracking

- **User Experience**
  - Modern, responsive design
  - Dark mode support
  - Copy to clipboard functionality
  - Download summaries as text files
  - Real-time text statistics

## Technology Stack

- **Backend**: Flask (Python)
- **NLP Library**: NLTK (Natural Language Toolkit)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **CORS**: Flask-CORS for cross-origin requests

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GENAI
   ```

2. **Navigate to the application directory**
   ```bash
   cd GENAI
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to http://localhost:5000

## Project Structure

```
GENAI/
├── GENAI/
│   ├── app.py
│   ├── requirements.txt
│   ├── static/
│   │   ├── script.js
│   │   └── style.css
│   └── templates/
│       └── index.html
├── analytics_data.json
└── README.md
```

## API Endpoints

### POST /api/summarize
Generate a summary of the provided text.

**Request Body:**
```json
{
  "text": "Your text to summarize...",
  "ratio": 40,
  "method": "normal"
}
```

**Response:**
```json
{
  "success": true,
  "summary": "Generated summary text...",
  "original_length": 500,
  "summary_length": 200,
  "compression_ratio": 40.0,
  "keywords": ["keyword1", "keyword2", ...],
  "readability": {
    "avg_words_per_sentence": 15.5,
    "avg_chars_per_word": 4.2,
    "flesch_kincaid_grade": 8.5,
    "reading_time_minutes": 2.5
  }
}
```

### POST /api/analyze
Analyze text for keywords and readability metrics.

**Request Body:**
```json
{
  "text": "Text to analyze..."
}
```

### GET /api/analytics
Get current analytics statistics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_summaries": 100,
    "total_texts_processed": 100,
    "total_words_processed": 50000,
    "total_words_generated": 20000,
    "average_compression_ratio": 40.0,
    "methods_used": {
      "normal": 60,
      "business_insights": 40
    },
    "sessions": 25
  }
}
```

### POST /api/batch-summarize
Process multiple texts in batch (up to 50 texts).

**Request Body:**
```json
{
  "texts": ["Text 1...", "Text 2...", ...],
  "ratio": 40,
  "method": "normal"
}
```

### GET /api/health
Health check endpoint.

## Usage

1. **Enter Text**: Paste or type your text into the input area
2. **Choose Method**: Select between "Normal" or "Business Insights" summarization
3. **Adjust Length**: Use the slider to set your desired summary length (10-90%)
4. **Generate**: Click "Generate Summary" to process your text
5. **Review Results**: View the summary, keywords, and readability metrics
6. **Export**: Copy or download your summary

## Summarization Methods

### Normal Mode
Uses word frequency analysis to identify the most important sentences. Best for
general-purpose text summarization.

### Business Insights Mode
Enhanced algorithm that:
- Prioritizes business-related keywords (revenue, profit, growth, etc.)
- Detects financial metrics and percentages
- Identifies action words and strategic decisions
- Considers sentence position and length
- Optimized for business reports, financial documents, and strategic content

## Analytics

The application tracks usage statistics including:
- Total summaries generated
- Words processed and generated
- Average compression ratios
- Method usage breakdown
- Daily statistics
- Session tracking

Access analytics by clicking the analytics button in the header.

## Configuration

### Port Configuration
To change the default port (5000), modify the last line in app.py:

```python
app.run(debug=True, port=YOUR_PORT)
```

### Analytics Data
Analytics data is stored in analytics_data.json in the root directory. This file is
automatically created and updated.

## Dependencies

- **Flask** (3.1.2): Web framework
- **Flask-CORS** (4.0.0): Cross-origin resource sharing
- **NLTK** (3.9.2): Natural language processing toolkit

## Development

### Running in Debug Mode
The application runs in debug mode by default. For production, set debug=False in app.py.

### NLTK Data
The application automatically downloads required NLTK data (punkt tokenizer and stopwords)
on first run.