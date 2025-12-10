from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

import string
import os
import re
from collections import Counter
from math import log


from datetime import datetime
import json

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

app = Flask(__name__)
CORS(app)

ANALYTICS_FILE = 'analytics_data.json'

class AnalyticsTracker:
    def __init__(self, filename=ANALYTICS_FILE):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        """Load analytics data from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Migrate old method names to new ones
                    if 'methods_used' in data:
                        old_methods = data['methods_used']
                        # Convert old method names to new ones
                        if 'frequency' in old_methods or 'tfidf' in old_methods or 'hybrid' in old_methods:
                            # Migrate old data
                            new_methods = {
                                'normal': old_methods.get('frequency', 0),
                                'business_insights': old_methods.get('hybrid', 0) + old_methods.get('tfidf', 0)
                            }
                            data['methods_used'] = new_methods
                            # Save migrated data
                            with open(self.filename, 'w') as f:
                                json.dump(data, f, indent=2)
                    return data
            except:
                return self.get_default_data()
        return self.get_default_data()
    
    def get_default_data(self):
        """Get default analytics structure"""
        return {
            'total_summaries': 0,
            'total_texts_processed': 0,
            'total_words_processed': 0,
            'total_words_generated': 0,
            'average_compression_ratio': 0,
            'methods_used': {
                'normal': 0,
                'business_insights': 0
            },
            'file_types_uploaded': {},
            'daily_stats': {},
            'sessions': 0
        }
    
    def save_data(self):
        """Save analytics data to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def track_summary(self, method, original_length, summary_length, file_type=None):
        """Track a summarization event"""
        compression_ratio = (summary_length / original_length * 100) if original_length > 0 else 0
        
        self.data['total_summaries'] += 1
        self.data['total_texts_processed'] += 1
        self.data['total_words_processed'] += original_length
        self.data['total_words_generated'] += summary_length
        
        # Update average compression ratio
        total_summaries = self.data['total_summaries']
        avg = self.data['average_compression_ratio']
        self.data['average_compression_ratio'] = (avg * (total_summaries - 1) + compression_ratio) / total_summaries
        
        # Track method usage
        if method in self.data['methods_used']:
            self.data['methods_used'][method] += 1
        
        # Track file types
        if file_type:
            if file_type not in self.data['file_types_uploaded']:
                self.data['file_types_uploaded'][file_type] = 0
            self.data['file_types_uploaded'][file_type] += 1
        
        # Track daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.data['daily_stats']:
            self.data['daily_stats'][today] = {
                'summaries': 0,
                'words_processed': 0,
                'words_generated': 0
            }
        
        self.data['daily_stats'][today]['summaries'] += 1
        self.data['daily_stats'][today]['words_processed'] += original_length
        self.data['daily_stats'][today]['words_generated'] += summary_length
        
        self.save_data()
    
    def increment_sessions(self):
        """Track new session"""
        self.data['sessions'] += 1
        self.save_data()
    
    def get_stats(self):
        """Get current analytics statistics"""
        return {
            'total_summaries': self.data['total_summaries'],
            'total_texts_processed': self.data['total_texts_processed'],
            'total_words_processed': self.data['total_words_processed'],
            'total_words_generated': self.data['total_words_generated'],
            'average_compression_ratio': round(self.data['average_compression_ratio'], 1),
            'methods_used': self.data['methods_used'],
            'file_types_uploaded': self.data['file_types_uploaded'],
            'sessions': self.data['sessions']
        }

# Initialize analytics tracker
analytics = AnalyticsTracker()

def generate_summary(text, summary_ratio=0.4, method='normal'):
    """
    Generate summary using multiple methods
    
    Methods:
    - normal: Standard word frequency-based summarization
    - business_insights: Enhanced summarization with business-focused insights
    """
    
    if not text or len(text.strip()) == 0:
        return {
            'success': False,
            'message': 'Please enter some text to summarize',
            'summary': '',
            'original_length': 0,
            'summary_length': 0
        }
    
    # Clean text
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text.split()) < 3:
        return {
            'success': False,
            'message': 'Text must contain at least 3 words',
            'summary': '',
            'original_length': len(text.split()),
            'summary_length': 0
        }
    
    try:
        sentences = sent_tokenize(text)
        
        if len(sentences) == 0:
            return {
                'success': False,
                'message': 'No sentences found in text',
                'summary': '',
                'original_length': 0,
                'summary_length': 0
            }
        
        stop_words = set(stopwords.words('english'))
        
        if method == 'business_insights':
            sentence_scores = calculate_business_insights_scores(sentences, stop_words)
        else:  # normal
            sentence_scores = calculate_frequency_scores(sentences, stop_words)
        
        # Select sentences based on ratio
        summary_count = max(1, int(len(sentences) * (summary_ratio / 100)))
        
        if sentence_scores:
            sorted_indices = sorted(sentence_scores.keys(), 
                                   key=lambda x: sentence_scores[x], 
                                   reverse=True)[:summary_count]
            sorted_indices.sort()  # Maintain original order
            summary_sentences = [sentences[i] for i in sorted_indices]
        else:
            summary_sentences = sentences[:summary_count]
        
        summary = ' '.join(summary_sentences)
        
        return {
            'success': True,
            'summary': summary,
            'original_length': len(text.split()),
            'summary_length': len(summary.split()),
            'sentence_count_original': len(sentences),
            'sentence_count_summary': len(summary_sentences),
            'compression_ratio': round((len(summary.split()) / len(text.split())) * 100, 1) if text.split() else 0,
            'method': method
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing text: {str(e)}',
            'summary': '',
            'original_length': 0,
            'summary_length': 0
        }

def calculate_frequency_scores(sentences, stop_words):
    """Original frequency-based scoring"""
    words = word_tokenize(' '.join(sentences).lower())
    
    word_freq = {}
    for word in words:
        if word not in stop_words and word not in string.punctuation and len(word) > 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    if not word_freq:
        return {}
    
    max_freq = max(word_freq.values())
    for word in word_freq:
        word_freq[word] = word_freq[word] / max_freq
    
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_words = word_tokenize(sentence.lower())
        score = 0
        for word in sentence_words:
            if word in word_freq:
                score += word_freq[word]
        sentence_scores[i] = score
    
    return sentence_scores

def calculate_tfidf_scores(sentences, stop_words):
    """TF-IDF based scoring - better for longer documents"""
    n_sentences = len(sentences)
    words_in_sentences = [
        [w.lower() for w in word_tokenize(s) 
         if w.lower() not in stop_words and w not in string.punctuation and len(w) > 2]
        for s in sentences
    ]
    
    # Calculate IDF
    word_doc_freq = Counter()
    for words in words_in_sentences:
        word_doc_freq.update(set(words))
    
    idf = {word: log(n_sentences / (freq + 1)) for word, freq in word_doc_freq.items()}
    
    # Calculate TF-IDF scores
    sentence_scores = {}
    for i, words in enumerate(words_in_sentences):
        tf = Counter(words)
        score = sum(tf[word] * idf.get(word, 0) for word in tf)
        sentence_scores[i] = score / (len(words) + 1)  # Normalize by sentence length
    
    return sentence_scores

def calculate_business_insights_scores(sentences, stop_words):
    """Business-focused scoring - prioritizes business keywords, metrics, and insights"""
    # Business keywords that indicate important business content
    business_keywords = {
        'revenue', 'profit', 'growth', 'sales', 'market', 'customer', 'client',
        'strategy', 'performance', 'financial', 'quarter', 'annual', 'year',
        'increase', 'decrease', 'improve', 'decline', 'target', 'goal', 'objective',
        'investment', 'capital', 'budget', 'cost', 'expense', 'income', 'earnings',
        'margin', 'roi', 'return', 'value', 'stakeholder', 'shareholder', 'equity',
        'revenue', 'profitability', 'efficiency', 'productivity', 'competitor',
        'competitive', 'market share', 'pricing', 'forecast', 'projection', 'trend',
        'metric', 'kpi', 'indicator', 'benchmark', 'milestone', 'achievement',
        'partnership', 'acquisition', 'merger', 'expansion', 'launch', 'initiative',
        'outcome', 'result', 'impact', 'benefit', 'advantage', 'opportunity', 'risk'
    }
    
    # Calculate base frequency scores
    freq_scores = calculate_frequency_scores(sentences, stop_words)
    
    # Business keyword bonus
    business_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        words = word_tokenize(sentence_lower)
        
        # Count business keywords
        business_count = sum(1 for word in words if word in business_keywords)
        
        # Check for numbers/percentages (financial metrics)
        has_numbers = bool(re.search(r'\d+[%$]?|\$\d+', sentence))
        number_bonus = 1.5 if has_numbers else 0
        
        # Check for action words (decisions, outcomes)
        action_words = {'decided', 'announced', 'achieved', 'reached', 'exceeded', 
                       'completed', 'launched', 'implemented', 'improved', 'increased',
                       'decreased', 'reduced', 'optimized', 'expanded', 'acquired'}
        has_action = any(word in sentence_lower for word in action_words)
        action_bonus = 1.2 if has_action else 0
        
        # Position bonus (executive summaries often at beginning)
        position_bonus = 1.0 - (i / len(sentences)) * 0.3  # 1.0 for first, 0.7 for last
        
        # Length preference (business summaries prefer medium-length sentences)
        word_count = len(words)
        if 8 <= word_count <= 25:
            length_bonus = 1.0
        elif word_count < 8:
            length_bonus = 0.6
        else:
            length_bonus = 0.8
        
        # Combine all factors
        base_score = freq_scores.get(i, 0)
        keyword_bonus = business_count * 0.3
        business_scores[i] = (base_score * 0.4) + (keyword_bonus * 0.2) + \
                            (number_bonus * 0.2) + (action_bonus * 0.1) + \
                            (position_bonus * 0.05) + (length_bonus * 0.05)
    
    return business_scores

def calculate_hybrid_scores(sentences, stop_words):
    """Hybrid scoring - combines frequency, position, and length"""
    freq_scores = calculate_frequency_scores(sentences, stop_words)
    
    # Position bonus (earlier sentences score higher)
    position_scores = {i: 1 - (i / len(sentences)) for i in range(len(sentences))}
    
    # Length penalty (avoid very short sentences)
    length_scores = {}
    for i, sent in enumerate(sentences):
        word_count = len(word_tokenize(sent))
        length_scores[i] = 1 if word_count > 5 else 0.5
    
    # Combine scores
    hybrid_scores = {}
    for i in range(len(sentences)):
        freq = freq_scores.get(i, 0)
        pos = position_scores.get(i, 0)
        length = length_scores.get(i, 0)
        hybrid_scores[i] = (freq * 0.6) + (pos * 0.2) + (length * 0.2)
    
    return hybrid_scores

def extract_keywords(text, num_keywords=10):
    """Extract top keywords from text using TF-IDF"""
    sentences = sent_tokenize(text)
    n_sentences = len(sentences)
    
    words_in_sentences = [
        [w.lower() for w in word_tokenize(s) 
         if w.lower() not in set(stopwords.words('english')) 
         and w not in string.punctuation and len(w) > 2]
        for s in sentences
    ]
    
    word_doc_freq = Counter()
    for words in words_in_sentences:
        word_doc_freq.update(set(words))
    
    idf = {word: log(n_sentences / (freq + 1)) for word, freq in word_doc_freq.items()}
    
    word_freq = Counter()
    for words in words_in_sentences:
        word_freq.update(words)
    
    tfidf_scores = {word: word_freq[word] * idf.get(word, 0) for word in word_freq}
    
    top_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:num_keywords]
    return [word for word, score in top_keywords]

def calculate_readability_metrics(text):
    """Calculate text readability metrics"""
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    
    if not sentences or not words:
        return {
            'avg_words_per_sentence': 0,
            'avg_chars_per_word': 0,
            'flesch_kincaid_grade': 0,
            'reading_time_minutes': 0
        }
    
    # Average words per sentence
    avg_words_per_sentence = len(words) / len(sentences)
    
    # Average characters per word
    total_chars = sum(len(word) for word in words)
    avg_chars_per_word = total_chars / len(words) if words else 0
    
    # Simplified Flesch-Kincaid Grade Level
    # Grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    # Using approximation: syllables ≈ vowel count
    syllable_count = 0
    for word in words:
        syllable_count += count_syllables(word)
    
    flesch_kincaid = (
        0.39 * avg_words_per_sentence + 
        11.8 * (syllable_count / len(words)) - 
        15.59
    ) if len(words) > 0 else 0
    
    # Reading time (average reading speed: 200 words/minute)
    reading_time = len(words) / 200
    
    return {
        'avg_words_per_sentence': round(avg_words_per_sentence, 2),
        'avg_chars_per_word': round(avg_chars_per_word, 2),
        'flesch_kincaid_grade': max(0, round(flesch_kincaid, 1)),
        'reading_time_minutes': round(reading_time, 2)
    }

def count_syllables(word):
    """Approximate syllable count using vowel groups"""
    word = word.lower()
    syllable_count = 0
    vowels = "aeiouy"
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent e
    if word.endswith('e'):
        syllable_count -= 1
    
    return max(1, syllable_count)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        text = data.get('text', '')
        ratio = data.get('ratio', 40)
        method = data.get('method', 'normal')
        file_type = data.get('file_type', None)
        
        ratio = max(10, min(90, float(ratio)))
        method = method if method in ['normal', 'business_insights'] else 'normal'
        
        result = generate_summary(text, ratio, method)
        
        if result['success']:
            result['keywords'] = extract_keywords(text, num_keywords=8)
            result['readability'] = calculate_readability_metrics(text)
            
            analytics.track_summary(method, result['original_length'], result['summary_length'], file_type)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error. Please try again.',
            'summary': ''
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze text for keywords and readability metrics"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or len(text.strip()) == 0:
            return jsonify({
                'success': False,
                'message': 'Please provide text to analyze'
            }), 400
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        return jsonify({
            'success': True,
            'keywords': extract_keywords(text, num_keywords=15),
            'readability': calculate_readability_metrics(text),
            'word_count': len(text.split()),
            'sentence_count': len(sent_tokenize(text))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Analysis error: {str(e)}'
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get current analytics statistics"""
    return jsonify({
        'success': True,
        'stats': analytics.get_stats()
    })

@app.route('/api/analytics/reset', methods=['POST'])
def reset_analytics():
    """Reset analytics data"""
    analytics.data = analytics.get_default_data()
    analytics.save_data()
    return jsonify({
        'success': True,
        'message': 'Analytics data reset'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': '2.0'})



@app.route('/api/batch-summarize', methods=['POST'])
def batch_summarize():
    """Process multiple texts in batch"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        ratio = data.get('ratio', 40)
        method = data.get('method', 'normal')
        
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({
                'success': False,
                'message': 'Provide array of texts to summarize'
            }), 400
        
        if len(texts) > 50:
            return jsonify({
                'success': False,
                'message': 'Maximum 50 texts per batch'
            }), 400
        
        ratio = max(10, min(90, float(ratio)))
        method = method if method in ['normal', 'business_insights'] else 'normal'
        
        results = []
        for idx, text in enumerate(texts):
            result = generate_summary(text, ratio, method)
            if result['success']:
                result['index'] = idx
                result['keywords'] = extract_keywords(text, num_keywords=5)
                result['readability'] = calculate_readability_metrics(text)
                
                # Track each summary
                analytics.track_summary(method, result['original_length'], result['summary_length'])
            results.append(result)
        
        return jsonify({
            'success': True,
            'total': len(texts),
            'processed': sum(1 for r in results if r.get('success')),
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Batch processing error: {str(e)}'
        }), 500

@app.before_request
def before_request():
    """Track new session"""
    if not hasattr(app, '_session_tracked'):
        analytics.increment_sessions()
        app._session_tracked = True

if __name__ == '__main__':
    app.run(debug=True, port=5000)
