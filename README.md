
# 🤖 AI CANGGIH - Sistem AI Komprehensif

**AI paling canggih yang bisa melakukan berbagai tugas dalam satu file lengkap!**

## 🚀 Fitur Utama

✅ **Natural Language Processing (NLP)**
- Analisis sentimen teks
- Deteksi bahasa otomatis  
- Ekstraksi entitas dan frasa kunci
- Keyword extraction dengan TF-IDF

✅ **Machine Translation**
- Terjemahan multi-bahasa
- Deteksi bahasa sumber otomatis
- Support 15+ bahasa populer

✅ **Text Summarization**
- Ringkasan teks otomatis
- Extractive summarization
- Kontrol rasio kompresi

✅ **Computer Vision**
- Analisis gambar komprehensif
- Deteksi wajah otomatis
- Analisis warna dominan
- Penilaian kualitas gambar
- Enhancement gambar otomatis

✅ **Web Scraping & Search**
- Scraping website otomatis
- Pencarian web real-time
- Ekstraksi metadata lengkap
- Pengumpulan link dan gambar

✅ **Machine Learning**
- Model klasifikasi dan regresi
- Auto feature engineering
- Data visualization
- Model evaluation metrics

✅ **Voice Processing**
- Speech-to-Text
- Text-to-Speech
- Audio file processing
- Real-time voice recognition

✅ **Data Analysis**
- Analisis dataset CSV/JSON
- Statistik deskriptif
- Correlation analysis
- Data quality assessment
- Visualisasi otomatis

✅ **Web Interface**
- Interface web modern
- Real-time processing
- Interactive dashboard
- Mobile-responsive design

## 📦 Instalasi

### 1. Clone/Download File
```bash
# Download file ai_canggih.py
wget https://your-repo/ai_canggih.py
```

### 2. Install Dependencies
```bash
# Install semua dependencies
pip install -r requirements.txt

# Atau install manual
pip install flask requests beautifulsoup4 pandas numpy matplotlib seaborn scikit-learn nltk textblob opencv-python pillow face-recognition speechrecognition pyttsx3 selenium spacy
```

### 3. Download Model NLP
```bash
# Download spaCy English model
python -m spacy download en_core_web_sm
```

## 🔧 Cara Penggunaan

### Mode Interactive (Command Line)
```bash
python ai_canggih.py interactive
```

### Mode Web Interface
```bash
python ai_canggih.py web
```
Kemudian buka browser ke `http://localhost:5000`

### Mode Demo
```bash
python ai_canggih.py demo
```

### Default Mode
```bash
python ai_canggih.py
```
Akan menjalankan mode interactive

## 💻 Contoh Penggunaan

### 1. Analisis Teks
```python
from ai_canggih import AICanggih

ai = AICanggih()
result = ai.analyze_text("AI Canggih adalah sistem yang sangat powerful!")
print(result)
```

### 2. Terjemahan
```python
result = ai.translate_text("Hello world", "id")
print(result['translated'])  # "Halo dunia"
```

### 3. Analisis Gambar
```python
result = ai.analyze_image("photo.jpg")
print(f"Faces detected: {result['faces']['face_count']}")
```

### 4. Web Scraping
```python
result = ai.scrape_website("https://example.com")
print(f"Found {len(result['content'])} content blocks")
```

### 5. Machine Learning
```python
result = ai.build_ml_model("data.csv", "target_column")
print(f"Model accuracy: {result['metrics']['accuracy']}")
```

## 🌐 Web Interface Features

Akses web interface di `http://localhost:5000` untuk:

- **📝 Analisis Teks**: Input teks dan dapatkan analisis lengkap
- **🌐 Terjemahan**: Terjemahan real-time ke berbagai bahasa  
- **📋 Ringkasan**: Buat ringkasan teks otomatis
- **🕷️ Web Scraping**: Scrape website dengan input URL
- **🔍 Pencarian Web**: Cari informasi di internet
- **🎤 Text-to-Speech**: Konversi teks ke suara
- **📁 File Processing**: Upload dan analisis file
- **ℹ️ System Info**: Informasi sistem dan capabilities

## 📊 Database & Logging

AI Canggih secara otomatis:
- Menyimpan semua hasil analisis ke database SQLite (`ai_canggih.db`)
- Membuat log aktivitas (`ai_canggih.log`)
- Menyimpan output visualisasi di folder `output/`
- Menyimpan model ML di folder `models/`

## 🔧 Konfigurasi

### Custom Port Web Interface
```python
ai = AICanggih()
ai.run_web_interface(host='0.0.0.0', port=8080)
```

### Custom Database Path
```python
ai = AICanggih()
ai.db_path = 'custom_database.db'
```

## 📚 API Reference

### Core Methods

#### Text Processing
- `analyze_text(text)` - Analisis teks komprehensif
- `translate_text(text, target_lang)` - Terjemahan teks
- `summarize_text(text, ratio)` - Ringkasan teks

#### Computer Vision  
- `analyze_image(image_path)` - Analisis gambar
- `enhance_image(image_path)` - Enhancement gambar

#### Web & Data
- `scrape_website(url)` - Scraping website
- `search_web(query)` - Pencarian web
- `analyze_data(data_path)` - Analisis dataset

#### Machine Learning
- `build_ml_model(data_path, target)` - Build ML model

#### Voice Processing
- `speech_to_text(audio_file)` - Speech recognition
- `text_to_speech(text)` - Text-to-speech

#### File Processing
- `process_files(directory)` - Batch file processing
- `generate_report(data)` - Generate reports

## 🎯 Use Cases

### 1. Content Analysis
- Analisis sentimen review produk
- Ekstraksi keyword dari artikel
- Deteksi bahasa dokumen

### 2. Data Science
- Exploratory Data Analysis (EDA)
- Quick ML prototyping
- Data visualization

### 3. Web Intelligence
- Monitor website content
- Competitive analysis
- Content aggregation

### 4. Media Processing
- Batch image analysis
- Face detection dalam foto
- Image quality assessment

### 5. Voice Applications
- Transcription services
- Voice-controlled apps
- Audio content analysis

## 🔧 Troubleshooting

### Error "Module not found"
```bash
pip install -r requirements.txt
```

### TTS tidak bekerja
```bash
# Install TTS engine untuk sistem Anda
# Windows: sudah built-in
# Linux: 
sudo apt-get install espeak espeak-data libespeak1 libespeak-dev
# macOS:
brew install espeak
```

### Face recognition error
```bash
# Install cmake dan dlib
pip install cmake dlib
pip install face-recognition
```

### SpaCy model error
```bash
python -m spacy download en_core_web_sm
```

## 🚀 Performance Tips

1. **Memory Usage**: Untuk file besar, gunakan batch processing
2. **Speed**: Aktifkan caching untuk operasi berulang  
3. **Storage**: Bersihkan folder `temp/` secara berkala
4. **Database**: Vacuum database SQLite secara rutin

## 🔐 Security Notes

- Web interface tidak memiliki autentikasi built-in
- Hati-hati dengan input URL untuk web scraping
- Validasi input file sebelum processing
- Jangan expose web interface ke internet publik tanpa security

## 📈 Roadmap

### v1.1 (Coming Soon)
- [ ] File upload via web interface
- [ ] Real-time chat interface  
- [ ] Advanced ML models
- [ ] API authentication

### v1.2 (Future)
- [ ] GPU acceleration
- [ ] Deep learning models
- [ ] Advanced NLP models
- [ ] Multi-language interface

## 🤝 Contributing

Sistem AI Canggih ini dibuat untuk edukasi dan prototyping. 
Silakan extend dan customize sesuai kebutuhan Anda!

## 📄 License

Open source - Gunakan dan modifikasi sesuka hati!

## 🆘 Support

Jika ada pertanyaan atau issue, buat GitHub issue atau contact developer.

---

**🎉 Selamat menggunakan AI CANGGIH! Sistem AI yang bisa apa aja dalam satu file! 🤖**
