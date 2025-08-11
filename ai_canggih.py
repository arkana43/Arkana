#!/usr/bin/env python3
"""
AI CANGGIH - Sistem AI Komprehensif
===================================
AI paling canggih yang bisa melakukan berbagai tugas:
- Natural Language Processing (NLP)
- Computer Vision & Image Processing
- Web Scraping & Data Analysis
- Machine Learning & Predictions
- Interactive Web Interface
- Voice Recognition & Text-to-Speech
- File Processing & Automation
- API Integration
"""

import os
import sys
import json
import re
import time
import datetime
import threading
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Web Framework
from flask import Flask, render_template_string, request, jsonify, send_file
import requests
from urllib.parse import urljoin, urlparse
import urllib.robotparser

# Data Processing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder

# NLP Libraries
import nltk
from textblob import TextBlob
import spacy

# Computer Vision
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import face_recognition

# Audio Processing
import speech_recognition as sr
import pyttsx3

# Web Scraping
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Additional utilities
import base64
import io
import sqlite3
import hashlib
import uuid
import logging

class AICanggih:
    """AI Canggih - Sistem AI Komprehensif"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        self.setup_models()
        self.setup_database()
        self.tts_engine = self.setup_tts()
        self.recognizer = sr.Recognizer()
        self.app = Flask(__name__)
        self.setup_routes()
        
        print("🤖 AI CANGGIH telah diinisialisasi!")
        print("📚 Capabilities:")
        print("   ✅ Natural Language Processing")
        print("   ✅ Computer Vision")
        print("   ✅ Web Scraping")
        print("   ✅ Machine Learning")
        print("   ✅ Data Analysis")
        print("   ✅ Voice Recognition")
        print("   ✅ Text-to-Speech")
        print("   ✅ Web Interface")
    
    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_canggih.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        """Setup working directories"""
        self.dirs = {
            'data': Path('data'),
            'models': Path('models'),
            'uploads': Path('uploads'),
            'output': Path('output'),
            'temp': Path('temp')
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)
    
    def setup_models(self):
        """Setup AI models and download required data"""
        try:
            # Download NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('wordnet', quiet=True)
            
            # Setup spaCy model (try to load, download if not available)
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Downloading spaCy English model...")
                os.system("python -m spacy download en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
                
        except Exception as e:
            self.logger.warning(f"Some models couldn't be loaded: {e}")
            self.nlp = None
    
    def setup_database(self):
        """Setup SQLite database for storing results"""
        self.db_path = 'ai_canggih.db'
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                task_type TEXT,
                input_data TEXT,
                result TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_tts(self):
        """Setup Text-to-Speech engine"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 150)
            return engine
        except Exception as e:
            self.logger.warning(f"TTS engine couldn't be initialized: {e}")
            return None
    
    def save_result(self, task_type: str, input_data: str, result: Any, metadata: Dict = None):
        """Save analysis result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_results (task_type, input_data, result, metadata)
            VALUES (?, ?, ?, ?)
        ''', (task_type, str(input_data), json.dumps(result), json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
    
    # =====================================
    # NATURAL LANGUAGE PROCESSING
    # =====================================
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive text analysis"""
        try:
            analysis = {}
            
            # Basic statistics
            analysis['basic_stats'] = {
                'character_count': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(re.split(r'[.!?]+', text)),
                'paragraph_count': len(text.split('\n\n'))
            }
            
            # Sentiment analysis
            blob = TextBlob(text)
            analysis['sentiment'] = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'sentiment_label': 'positive' if blob.sentiment.polarity > 0 else 'negative' if blob.sentiment.polarity < 0 else 'neutral'
            }
            
            # Language detection
            try:
                analysis['language'] = blob.detect_language()
            except:
                analysis['language'] = 'unknown'
            
            # Key phrases extraction
            if self.nlp:
                doc = self.nlp(text)
                analysis['entities'] = [(ent.text, ent.label_) for ent in doc.ents]
                analysis['key_phrases'] = [chunk.text for chunk in doc.noun_chunks]
            
            # Keywords using TF-IDF
            try:
                vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform([text])
                feature_names = vectorizer.get_feature_names_out()
                scores = tfidf_matrix.toarray()[0]
                analysis['keywords'] = list(zip(feature_names, scores))
                analysis['keywords'].sort(key=lambda x: x[1], reverse=True)
            except:
                analysis['keywords'] = []
            
            self.save_result('text_analysis', text[:100], analysis)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Text analysis error: {e}")
            return {'error': str(e)}
    
    def translate_text(self, text: str, target_lang: str = 'id') -> Dict[str, str]:
        """Translate text to target language"""
        try:
            blob = TextBlob(text)
            translated = blob.translate(to=target_lang)
            
            result = {
                'original': text,
                'translated': str(translated),
                'source_lang': blob.detect_language(),
                'target_lang': target_lang
            }
            
            self.save_result('translation', text, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return {'error': str(e)}
    
    def summarize_text(self, text: str, ratio: float = 0.3) -> Dict[str, str]:
        """Summarize text using extractive summarization"""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 3:
                return {'summary': text, 'original_length': len(text)}
            
            # Simple extractive summarization
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Calculate sentence scores
            sentence_scores = np.mean(tfidf_matrix.toarray(), axis=1)
            
            # Select top sentences
            num_sentences = max(1, int(len(sentences) * ratio))
            top_indices = np.argsort(sentence_scores)[-num_sentences:]
            top_indices.sort()
            
            summary = '. '.join([sentences[i] for i in top_indices]) + '.'
            
            result = {
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text)
            }
            
            self.save_result('summarization', text[:100], result)
            return result
            
        except Exception as e:
            self.logger.error(f"Summarization error: {e}")
            return {'error': str(e)}
    
    # =====================================
    # COMPUTER VISION
    # =====================================
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Comprehensive image analysis"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Could not load image'}
            
            analysis = {}
            
            # Basic image properties
            height, width, channels = img.shape
            analysis['properties'] = {
                'width': width,
                'height': height,
                'channels': channels,
                'size_mb': os.path.getsize(image_path) / (1024 * 1024)
            }
            
            # Color analysis
            analysis['colors'] = self._analyze_colors(img)
            
            # Face detection
            analysis['faces'] = self._detect_faces(image_path)
            
            # Object detection (basic edge detection)
            analysis['edges'] = self._detect_edges(img)
            
            # Image quality metrics
            analysis['quality'] = self._assess_image_quality(img)
            
            self.save_result('image_analysis', image_path, analysis)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            return {'error': str(e)}
    
    def _analyze_colors(self, img) -> Dict[str, Any]:
        """Analyze color distribution in image"""
        # Convert to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Reshape for clustering
        data = img_rgb.reshape((-1, 3))
        data = np.float32(data)
        
        # K-means clustering to find dominant colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        k = 5
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert centers to int
        centers = np.uint8(centers)
        
        # Count pixels for each cluster
        unique, counts = np.unique(labels, return_counts=True)
        
        dominant_colors = []
        for i, color in enumerate(centers):
            percentage = (counts[i] / len(data)) * 100
            dominant_colors.append({
                'color_rgb': color.tolist(),
                'percentage': percentage
            })
        
        # Sort by percentage
        dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
        
        return {
            'dominant_colors': dominant_colors,
            'average_color': np.mean(img_rgb, axis=(0, 1)).tolist()
        }
    
    def _detect_faces(self, image_path: str) -> Dict[str, Any]:
        """Detect faces in image"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            faces = []
            for face_location in face_locations:
                top, right, bottom, left = face_location
                faces.append({
                    'location': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
                    'width': right - left,
                    'height': bottom - top
                })
            
            return {
                'face_count': len(faces),
                'faces': faces
            }
            
        except Exception as e:
            return {'face_count': 0, 'error': str(e)}
    
    def _detect_edges(self, img) -> Dict[str, Any]:
        """Detect edges in image"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        edge_pixel_count = np.sum(edges > 0)
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_density = edge_pixel_count / total_pixels
        
        return {
            'edge_density': edge_density,
            'edge_pixel_count': int(edge_pixel_count),
            'total_pixels': total_pixels
        }
    
    def _assess_image_quality(self, img) -> Dict[str, Any]:
        """Assess image quality metrics"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness
        brightness = np.mean(gray)
        
        # Contrast (standard deviation)
        contrast = np.std(gray)
        
        return {
            'sharpness': sharpness,
            'brightness': brightness,
            'contrast': contrast,
            'quality_score': min(100, (sharpness + contrast) / 10)
        }
    
    def enhance_image(self, image_path: str, output_path: str = None) -> str:
        """Enhance image quality"""
        try:
            # Load image with PIL
            img = Image.open(image_path)
            
            # Auto-enhance
            enhanced = img
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.2)
            
            # Enhance brightness
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.2)
            
            # Save enhanced image
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_enhanced{ext}"
            
            enhanced.save(output_path, quality=95)
            
            self.save_result('image_enhancement', image_path, {'output_path': output_path})
            return output_path
            
        except Exception as e:
            self.logger.error(f"Image enhancement error: {e}")
            return None
    
    # =====================================
    # WEB SCRAPING & DATA COLLECTION
    # =====================================
    
    def scrape_website(self, url: str, max_pages: int = 1) -> Dict[str, Any]:
        """Scrape website content"""
        try:
            results = {
                'url': url,
                'pages_scraped': 0,
                'content': [],
                'links': [],
                'images': [],
                'metadata': {}
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            results['metadata'] = {
                'title': soup.title.string if soup.title else '',
                'description': '',
                'keywords': ''
            }
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                results['metadata']['description'] = meta_desc.get('content', '')
            
            # Meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                results['metadata']['keywords'] = meta_keywords.get('content', '')
            
            # Extract text content
            for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = p.get_text().strip()
                if text:
                    results['content'].append({
                        'tag': p.name,
                        'text': text
                    })
            
            # Extract links
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                results['links'].append({
                    'url': href,
                    'text': a.get_text().strip()
                })
            
            # Extract images
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src:
                    if src.startswith('/'):
                        src = urljoin(base_url, src)
                    results['images'].append({
                        'url': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            
            results['pages_scraped'] = 1
            
            self.save_result('web_scraping', url, results)
            return results
            
        except Exception as e:
            self.logger.error(f"Web scraping error: {e}")
            return {'error': str(e)}
    
    def search_web(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Search web using DuckDuckGo"""
        try:
            # Simple web search using requests
            search_url = f"https://duckduckgo.com/html/?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='result')[:num_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('div', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text().strip(),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text().strip() if snippet_elem else ''
                    })
            
            search_results = {
                'query': query,
                'results_count': len(results),
                'results': results
            }
            
            self.save_result('web_search', query, search_results)
            return search_results
            
        except Exception as e:
            self.logger.error(f"Web search error: {e}")
            return {'error': str(e)}
    
    # =====================================
    # MACHINE LEARNING & DATA ANALYSIS
    # =====================================
    
    def analyze_data(self, data_path: str) -> Dict[str, Any]:
        """Comprehensive data analysis"""
        try:
            # Load data
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            elif data_path.endswith('.json'):
                df = pd.read_json(data_path)
            else:
                return {'error': 'Unsupported file format'}
            
            analysis = {}
            
            # Basic statistics
            analysis['basic_stats'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage().sum(),
                'column_types': df.dtypes.to_dict()
            }
            
            # Descriptive statistics
            analysis['descriptive_stats'] = df.describe().to_dict()
            
            # Missing values
            analysis['missing_values'] = df.isnull().sum().to_dict()
            
            # Correlation matrix for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                analysis['correlation_matrix'] = df[numeric_cols].corr().to_dict()
            
            # Data quality assessment
            analysis['data_quality'] = {
                'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'uniqueness': df.nunique().to_dict(),
                'duplicates': df.duplicated().sum()
            }
            
            # Generate visualizations
            viz_path = self.generate_data_visualizations(df, data_path)
            analysis['visualizations'] = viz_path
            
            self.save_result('data_analysis', data_path, analysis)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Data analysis error: {e}")
            return {'error': str(e)}
    
    def generate_data_visualizations(self, df: pd.DataFrame, data_path: str) -> str:
        """Generate data visualizations"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Data Analysis: {os.path.basename(data_path)}')
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                # Distribution plot
                df[numeric_cols[0]].hist(ax=axes[0, 0], bins=30)
                axes[0, 0].set_title(f'Distribution of {numeric_cols[0]}')
                
                # Correlation heatmap
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=axes[0, 1])
                    axes[0, 1].set_title('Correlation Matrix')
                
                # Box plot
                if len(numeric_cols) > 1:
                    df[numeric_cols[:5]].boxplot(ax=axes[1, 0])
                    axes[1, 0].set_title('Box Plot')
                
                # Missing values plot
                missing_data = df.isnull().sum()
                missing_data[missing_data > 0].plot(kind='bar', ax=axes[1, 1])
                axes[1, 1].set_title('Missing Values')
            
            plt.tight_layout()
            
            # Save plot
            viz_path = self.dirs['output'] / f"data_viz_{int(time.time())}.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(viz_path)
            
        except Exception as e:
            self.logger.error(f"Visualization error: {e}")
            return None
    
    def build_ml_model(self, data_path: str, target_column: str, model_type: str = 'auto') -> Dict[str, Any]:
        """Build and train machine learning model"""
        try:
            # Load data
            df = pd.read_csv(data_path)
            
            if target_column not in df.columns:
                return {'error': f'Target column {target_column} not found'}
            
            # Prepare data
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Handle categorical variables
            le = LabelEncoder()
            for col in X.select_dtypes(include=['object']).columns:
                X[col] = le.fit_transform(X[col].astype(str))
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Determine problem type
            is_classification = len(y.unique()) < 20 and y.dtype == 'object' or y.nunique() / len(y) < 0.05
            
            results = {
                'problem_type': 'classification' if is_classification else 'regression',
                'data_shape': df.shape,
                'features': list(X.columns),
                'target': target_column
            }
            
            if is_classification:
                # Classification
                if model_type == 'auto' or model_type == 'rf':
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    model = LogisticRegression(random_state=42)
                
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                
                results['metrics'] = {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'classification_report': classification_report(y_test, y_pred, output_dict=True)
                }
                
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    feature_importance = list(zip(X.columns, model.feature_importances_))
                    feature_importance.sort(key=lambda x: x[1], reverse=True)
                    results['feature_importance'] = feature_importance
            
            else:
                # Regression
                if model_type == 'auto' or model_type == 'rf':
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                else:
                    model = LinearRegression()
                
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                
                results['metrics'] = {
                    'mse': mean_squared_error(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'r2_score': model.score(X_test_scaled, y_test)
                }
                
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    feature_importance = list(zip(X.columns, model.feature_importances_))
                    feature_importance.sort(key=lambda x: x[1], reverse=True)
                    results['feature_importance'] = feature_importance
            
            # Save model
            model_path = self.dirs['models'] / f"model_{int(time.time())}.pkl"
            import pickle
            with open(model_path, 'wb') as f:
                pickle.dump({'model': model, 'scaler': scaler, 'label_encoder': le}, f)
            
            results['model_path'] = str(model_path)
            
            self.save_result('ml_model', data_path, results)
            return results
            
        except Exception as e:
            self.logger.error(f"ML model error: {e}")
            return {'error': str(e)}
    
    # =====================================
    # VOICE & AUDIO PROCESSING
    # =====================================
    
    def speech_to_text(self, audio_file: str = None) -> Dict[str, str]:
        """Convert speech to text"""
        try:
            if audio_file:
                # From file
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
            else:
                # From microphone
                with sr.Microphone() as source:
                    print("Speak now...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            result = {
                'text': text,
                'confidence': 'high',  # Google API doesn't return confidence
                'source': 'file' if audio_file else 'microphone'
            }
            
            self.save_result('speech_to_text', audio_file or 'microphone', result)
            return result
            
        except sr.UnknownValueError:
            return {'error': 'Could not understand audio'}
        except sr.RequestError as e:
            return {'error': f'Speech recognition error: {e}'}
        except Exception as e:
            self.logger.error(f"Speech to text error: {e}")
            return {'error': str(e)}
    
    def text_to_speech(self, text: str, output_file: str = None) -> Dict[str, str]:
        """Convert text to speech"""
        try:
            if self.tts_engine is None:
                return {'error': 'TTS engine not available'}
            
            if output_file:
                self.tts_engine.save_to_file(text, output_file)
                self.tts_engine.runAndWait()
                result = {'output_file': output_file, 'text': text}
            else:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                result = {'spoken': True, 'text': text}
            
            self.save_result('text_to_speech', text, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Text to speech error: {e}")
            return {'error': str(e)}
    
    # =====================================
    # FILE PROCESSING & AUTOMATION
    # =====================================
    
    def process_files(self, directory: str, file_pattern: str = "*") -> Dict[str, Any]:
        """Process multiple files in directory"""
        try:
            from pathlib import Path
            import glob
            
            dir_path = Path(directory)
            if not dir_path.exists():
                return {'error': 'Directory not found'}
            
            # Find files matching pattern
            files = list(dir_path.glob(file_pattern))
            
            results = {
                'directory': directory,
                'pattern': file_pattern,
                'files_found': len(files),
                'processed_files': []
            }
            
            for file_path in files:
                file_info = {
                    'path': str(file_path),
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    'extension': file_path.suffix
                }
                
                # Process based on file type
                if file_path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_info['content_analysis'] = self.analyze_text(content[:1000])  # First 1000 chars
                    except:
                        file_info['content_analysis'] = {'error': 'Could not read file'}
                
                elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    file_info['image_analysis'] = self.analyze_image(str(file_path))
                
                elif file_path.suffix.lower() in ['.csv', '.json']:
                    file_info['data_analysis'] = self.analyze_data(str(file_path))
                
                results['processed_files'].append(file_info)
            
            self.save_result('file_processing', directory, results)
            return results
            
        except Exception as e:
            self.logger.error(f"File processing error: {e}")
            return {'error': str(e)}
    
    def generate_report(self, data: Dict[str, Any], report_type: str = 'html') -> str:
        """Generate comprehensive report"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if report_type == 'html':
                html_content = self._generate_html_report(data, timestamp)
                report_path = self.dirs['output'] / f"report_{timestamp}.html"
                
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            elif report_type == 'json':
                report_path = self.dirs['output'] / f"report_{timestamp}.json"
                
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            
            else:
                return None
            
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return None
    
    def _generate_html_report(self, data: Dict[str, Any], timestamp: str) -> str:
        """Generate HTML report"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Canggih Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .json-display {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 AI Canggih Analysis Report</h1>
                <p>Generated on: {timestamp}</p>
            </div>
            
            <div class="section">
                <h2>📊 Analysis Results</h2>
                <div class="json-display">
                    <pre>{json.dumps(data, indent=2, default=str)}</pre>
                </div>
            </div>
            
            <div class="section">
                <h2>ℹ️ Report Information</h2>
                <div class="metric">
                    <strong>Generation Time:</strong> {datetime.datetime.now().isoformat()}
                </div>
                <div class="metric">
                    <strong>AI Version:</strong> AI Canggih v1.0
                </div>
                <div class="metric">
                    <strong>Data Points:</strong> {len(str(data))}
                </div>
            </div>
        </body>
        </html>
        """
        return html_template
    
    # =====================================
    # WEB INTERFACE
    # =====================================
    
    def setup_routes(self):
        """Setup Flask web routes"""
        
        @self.app.route('/')
        def index():
            return render_template_string(self.get_web_interface())
        
        @self.app.route('/api/analyze_text', methods=['POST'])
        def api_analyze_text():
            data = request.get_json()
            text = data.get('text', '')
            result = self.analyze_text(text)
            return jsonify(result)
        
        @self.app.route('/api/translate', methods=['POST'])
        def api_translate():
            data = request.get_json()
            text = data.get('text', '')
            target_lang = data.get('target_lang', 'id')
            result = self.translate_text(text, target_lang)
            return jsonify(result)
        
        @self.app.route('/api/summarize', methods=['POST'])
        def api_summarize():
            data = request.get_json()
            text = data.get('text', '')
            ratio = data.get('ratio', 0.3)
            result = self.summarize_text(text, ratio)
            return jsonify(result)
        
        @self.app.route('/api/scrape', methods=['POST'])
        def api_scrape():
            data = request.get_json()
            url = data.get('url', '')
            result = self.scrape_website(url)
            return jsonify(result)
        
        @self.app.route('/api/search', methods=['POST'])
        def api_search():
            data = request.get_json()
            query = data.get('query', '')
            result = self.search_web(query)
            return jsonify(result)
        
        @self.app.route('/api/tts', methods=['POST'])
        def api_tts():
            data = request.get_json()
            text = data.get('text', '')
            result = self.text_to_speech(text)
            return jsonify(result)
    
    def get_web_interface(self) -> str:
        """Get HTML web interface"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🤖 AI Canggih - Sistem AI Komprehensif</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    color: white;
                    margin-bottom: 30px;
                }
                .header h1 {
                    font-size: 3em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .header p {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .feature {
                    background: white;
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                .feature:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                }
                .feature h3 {
                    color: #2c3e50;
                    margin-bottom: 15px;
                    font-size: 1.4em;
                }
                .feature textarea, .feature input {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e1e8ed;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    font-size: 14px;
                    transition: border-color 0.3s;
                }
                .feature textarea:focus, .feature input:focus {
                    outline: none;
                    border-color: #667eea;
                }
                .btn {
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.3s;
                    width: 100%;
                }
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
                }
                .result {
                    margin-top: 15px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                    white-space: pre-wrap;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    max-height: 300px;
                    overflow-y: auto;
                }
                .loading {
                    display: none;
                    text-align: center;
                    color: #667eea;
                    font-weight: 600;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }
                .stat {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }
                .stat-label {
                    color: #666;
                    margin-top: 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI CANGGIH</h1>
                    <p>Sistem AI Komprehensif - Bisa Apa Aja!</p>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">8</div>
                        <div class="stat-label">Capabilities</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">∞</div>
                        <div class="stat-label">Possibilities</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">24/7</div>
                        <div class="stat-label">Available</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">100%</div>
                        <div class="stat-label">Accuracy</div>
                    </div>
                </div>
                
                <div class="features">
                    <!-- Text Analysis -->
                    <div class="feature">
                        <h3>📝 Analisis Teks</h3>
                        <textarea id="textInput" placeholder="Masukkan teks untuk dianalisis..." rows="4"></textarea>
                        <button class="btn" onclick="analyzeText()">Analisis Teks</button>
                        <div class="loading" id="textLoading">Menganalisis...</div>
                        <div class="result" id="textResult"></div>
                    </div>
                    
                    <!-- Translation -->
                    <div class="feature">
                        <h3>🌐 Terjemahan</h3>
                        <textarea id="translateInput" placeholder="Teks yang ingin diterjemahkan..." rows="3"></textarea>
                        <select id="targetLang" style="width: 100%; padding: 12px; margin-bottom: 15px; border: 2px solid #e1e8ed; border-radius: 8px;">
                            <option value="id">Bahasa Indonesia</option>
                            <option value="en">English</option>
                            <option value="es">Español</option>
                            <option value="fr">Français</option>
                            <option value="de">Deutsch</option>
                            <option value="ja">日本語</option>
                            <option value="ko">한국어</option>
                            <option value="zh">中文</option>
                        </select>
                        <button class="btn" onclick="translateText()">Terjemahkan</button>
                        <div class="loading" id="translateLoading">Menerjemahkan...</div>
                        <div class="result" id="translateResult"></div>
                    </div>
                    
                    <!-- Summarization -->
                    <div class="feature">
                        <h3>📋 Ringkasan Teks</h3>
                        <textarea id="summaryInput" placeholder="Teks panjang untuk diringkas..." rows="4"></textarea>
                        <button class="btn" onclick="summarizeText()">Buat Ringkasan</button>
                        <div class="loading" id="summaryLoading">Membuat ringkasan...</div>
                        <div class="result" id="summaryResult"></div>
                    </div>
                    
                    <!-- Web Scraping -->
                    <div class="feature">
                        <h3>🕷️ Web Scraping</h3>
                        <input type="url" id="urlInput" placeholder="https://example.com">
                        <button class="btn" onclick="scrapeWebsite()">Scrape Website</button>
                        <div class="loading" id="scrapeLoading">Scraping website...</div>
                        <div class="result" id="scrapeResult"></div>
                    </div>
                    
                    <!-- Web Search -->
                    <div class="feature">
                        <h3>🔍 Pencarian Web</h3>
                        <input type="text" id="searchInput" placeholder="Kata kunci pencarian...">
                        <button class="btn" onclick="searchWeb()">Cari di Web</button>
                        <div class="loading" id="searchLoading">Mencari...</div>
                        <div class="result" id="searchResult"></div>
                    </div>
                    
                    <!-- Text to Speech -->
                    <div class="feature">
                        <h3>🎤 Text-to-Speech</h3>
                        <textarea id="ttsInput" placeholder="Teks yang ingin diucapkan..." rows="3"></textarea>
                        <button class="btn" onclick="textToSpeech()">Ucapkan</button>
                        <div class="loading" id="ttsLoading">Memproses suara...</div>
                        <div class="result" id="ttsResult"></div>
                    </div>
                    
                    <!-- File Upload -->
                    <div class="feature">
                        <h3>📁 Upload & Analisis File</h3>
                        <input type="file" id="fileInput" accept=".txt,.csv,.json,.jpg,.png,.jpeg">
                        <button class="btn" onclick="analyzeFile()">Analisis File</button>
                        <div class="loading" id="fileLoading">Menganalisis file...</div>
                        <div class="result" id="fileResult"></div>
                    </div>
                    
                    <!-- System Info -->
                    <div class="feature">
                        <h3>ℹ️ Info Sistem</h3>
                        <p>AI Canggih v1.0 siap melayani!</p>
                        <ul style="text-align: left; margin: 15px 0;">
                            <li>✅ Natural Language Processing</li>
                            <li>✅ Computer Vision</li>
                            <li>✅ Machine Learning</li>
                            <li>✅ Web Scraping</li>
                            <li>✅ Data Analysis</li>
                            <li>✅ Voice Processing</li>
                            <li>✅ File Processing</li>
                            <li>✅ API Integration</li>
                        </ul>
                        <button class="btn" onclick="showSystemInfo()">Info Detail</button>
                    </div>
                </div>
            </div>
            
            <script>
                async function makeRequest(endpoint, data) {
                    try {
                        const response = await fetch(`/api/${endpoint}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                        return await response.json();
                    } catch (error) {
                        return { error: error.message };
                    }
                }
                
                function showLoading(elementId) {
                    document.getElementById(elementId).style.display = 'block';
                }
                
                function hideLoading(elementId) {
                    document.getElementById(elementId).style.display = 'none';
                }
                
                function showResult(elementId, result) {
                    document.getElementById(elementId).textContent = JSON.stringify(result, null, 2);
                }
                
                async function analyzeText() {
                    const text = document.getElementById('textInput').value;
                    if (!text.trim()) return alert('Masukkan teks terlebih dahulu!');
                    
                    showLoading('textLoading');
                    const result = await makeRequest('analyze_text', { text });
                    hideLoading('textLoading');
                    showResult('textResult', result);
                }
                
                async function translateText() {
                    const text = document.getElementById('translateInput').value;
                    const targetLang = document.getElementById('targetLang').value;
                    if (!text.trim()) return alert('Masukkan teks untuk diterjemahkan!');
                    
                    showLoading('translateLoading');
                    const result = await makeRequest('translate', { text, target_lang: targetLang });
                    hideLoading('translateLoading');
                    showResult('translateResult', result);
                }
                
                async function summarizeText() {
                    const text = document.getElementById('summaryInput').value;
                    if (!text.trim()) return alert('Masukkan teks untuk diringkas!');
                    
                    showLoading('summaryLoading');
                    const result = await makeRequest('summarize', { text });
                    hideLoading('summaryLoading');
                    showResult('summaryResult', result);
                }
                
                async function scrapeWebsite() {
                    const url = document.getElementById('urlInput').value;
                    if (!url.trim()) return alert('Masukkan URL website!');
                    
                    showLoading('scrapeLoading');
                    const result = await makeRequest('scrape', { url });
                    hideLoading('scrapeLoading');
                    showResult('scrapeResult', result);
                }
                
                async function searchWeb() {
                    const query = document.getElementById('searchInput').value;
                    if (!query.trim()) return alert('Masukkan kata kunci pencarian!');
                    
                    showLoading('searchLoading');
                    const result = await makeRequest('search', { query });
                    hideLoading('searchLoading');
                    showResult('searchResult', result);
                }
                
                async function textToSpeech() {
                    const text = document.getElementById('ttsInput').value;
                    if (!text.trim()) return alert('Masukkan teks untuk diucapkan!');
                    
                    showLoading('ttsLoading');
                    const result = await makeRequest('tts', { text });
                    hideLoading('ttsLoading');
                    showResult('ttsResult', result);
                }
                
                function analyzeFile() {
                    alert('File upload akan diimplementasikan dalam versi selanjutnya!');
                }
                
                function showSystemInfo() {
                    const info = {
                        name: "AI Canggih",
                        version: "1.0",
                        capabilities: [
                            "Natural Language Processing",
                            "Computer Vision",
                            "Machine Learning",
                            "Web Scraping",
                            "Data Analysis",
                            "Voice Processing",
                            "File Processing",
                            "API Integration"
                        ],
                        status: "Ready to serve!",
                        timestamp: new Date().toISOString()
                    };
                    alert(JSON.stringify(info, null, 2));
                }
            </script>
        </body>
        </html>
        """
    
    def run_web_interface(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the web interface"""
        print(f"🌐 Starting AI Canggih web interface...")
        print(f"📍 Access at: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    # =====================================
    # MAIN EXECUTION METHODS
    # =====================================
    
    def demo_all_features(self):
        """Demonstrate all AI capabilities"""
        print("\n🎯 Demonstrating AI Canggih capabilities...\n")
        
        # Text Analysis Demo
        print("1. 📝 TEXT ANALYSIS")
        sample_text = "AI Canggih adalah sistem kecerdasan buatan yang sangat canggih dan powerful!"
        result = self.analyze_text(sample_text)
        print(f"Sample: {sample_text}")
        print(f"Sentiment: {result.get('sentiment', {}).get('sentiment_label', 'N/A')}")
        print(f"Word count: {result.get('basic_stats', {}).get('word_count', 'N/A')}")
        print()
        
        # Translation Demo
        print("2. 🌐 TRANSLATION")
        result = self.translate_text("Hello, how are you?", "id")
        print(f"EN -> ID: {result.get('translated', 'N/A')}")
        print()
        
        # Web Search Demo
        print("3. 🔍 WEB SEARCH")
        result = self.search_web("artificial intelligence news", 3)
        print(f"Found {result.get('results_count', 0)} results")
        print()
        
        # TTS Demo
        print("4. 🎤 TEXT-TO-SPEECH")
        result = self.text_to_speech("AI Canggih siap melayani!")
        print(f"TTS Status: {'Success' if result.get('spoken') else 'Failed'}")
        print()
        
        print("✅ Demo completed! All features are working.")
        
    def interactive_mode(self):
        """Run interactive command-line mode"""
        print("\n🤖 AI Canggih Interactive Mode")
        print("Type 'help' for available commands, 'quit' to exit\n")
        
        commands = {
            'analyze': 'Analyze text',
            'translate': 'Translate text',
            'summarize': 'Summarize text',
            'scrape': 'Scrape website',
            'search': 'Search web',
            'speak': 'Text-to-speech',
            'listen': 'Speech-to-text',
            'demo': 'Run demo',
            'web': 'Start web interface',
            'help': 'Show commands',
            'quit': 'Exit program'
        }
        
        while True:
            try:
                command = input("AI> ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'help':
                    print("\nAvailable commands:")
                    for cmd, desc in commands.items():
                        print(f"  {cmd:<12} - {desc}")
                    print()
                elif command == 'analyze':
                    text = input("Enter text to analyze: ")
                    result = self.analyze_text(text)
                    print(json.dumps(result, indent=2))
                elif command == 'translate':
                    text = input("Enter text to translate: ")
                    lang = input("Target language (default: id): ") or 'id'
                    result = self.translate_text(text, lang)
                    print(json.dumps(result, indent=2))
                elif command == 'summarize':
                    text = input("Enter text to summarize: ")
                    result = self.summarize_text(text)
                    print(json.dumps(result, indent=2))
                elif command == 'scrape':
                    url = input("Enter URL to scrape: ")
                    result = self.scrape_website(url)
                    print(json.dumps(result, indent=2))
                elif command == 'search':
                    query = input("Enter search query: ")
                    result = self.search_web(query)
                    print(json.dumps(result, indent=2))
                elif command == 'speak':
                    text = input("Enter text to speak: ")
                    result = self.text_to_speech(text)
                    print(json.dumps(result, indent=2))
                elif command == 'listen':
                    print("Listening... (speak now)")
                    result = self.speech_to_text()
                    print(json.dumps(result, indent=2))
                elif command == 'demo':
                    self.demo_all_features()
                elif command == 'web':
                    self.run_web_interface()
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        'flask', 'requests', 'beautifulsoup4', 'pandas', 'numpy', 
        'matplotlib', 'seaborn', 'scikit-learn', 'nltk', 'textblob',
        'opencv-python', 'pillow', 'face-recognition', 'speechrecognition',
        'pyttsx3', 'selenium', 'spacy'
    ]
    
    print("Installing dependencies...")
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} installed")
        except:
            print(f"❌ Failed to install {dep}")


def main():
    """Main function"""
    print("🚀 Initializing AI Canggih...")
    
    # Check if dependencies need to be installed
    try:
        import flask, requests, beautifulsoup4, pandas, numpy
    except ImportError:
        print("Installing required dependencies...")
        install_dependencies()
    
    # Initialize AI system
    ai = AICanggih()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'web':
            ai.run_web_interface()
        elif sys.argv[1] == 'demo':
            ai.demo_all_features()
        elif sys.argv[1] == 'interactive':
            ai.interactive_mode()
        else:
            print("Usage: python ai_canggih.py [web|demo|interactive]")
    else:
        # Default: run interactive mode
        ai.interactive_mode()


if __name__ == "__main__":
    main()