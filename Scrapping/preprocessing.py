import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from tqdm import tqdm
import os
import emoji

# --- CONFIGURATION ---
LIMIT_DATA = None  # Ubah ke angka (misal: 1000) jika ingin memproses sebagian saja

# Initialize Sastrawi
print("Initializing Sastrawi tools...")
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
stopword = stopword_factory.create_stop_word_remover()

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # 1. Menghapus Emoji secara eksplisit
    text = emoji.replace_emoji(text, replace='')
    
    # 2. Case Folding (Lowercase)
    text = text.lower()
    
    # 3. Menghapus URL
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # 4. Menghapus mentions (@user) dan hashtags (#tag)
    text = re.sub(r'@\w+|#\w+', '', text)
    
    # 5. Menghapus Simbol, Angka, dan tanda baca (Hanya menyisakan huruf)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # 6. Menghapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} tidak ditemukan!")
        return

    print(f"Membaca data dari {input_file}...")
    # Read CSV (YouTube data usually uses UTF-8)
    df = pd.read_csv(input_file)
    
    # Check if 'comment' column exists (based on youtube_scraper.py)
    column_to_process = 'comment'
    if column_to_process not in df.columns:
        # Try finding any column that looks like a comment if 'comment' is missing
        possible_cols = [col for col in df.columns if 'text' in col.lower() or 'comment' in col.lower()]
        if possible_cols:
            column_to_process = possible_cols[0]
            print(f"Kolom 'comment' tidak ada, menggunakan kolom '{column_to_process}' sebagai gantinya.")
        else:
            print(f"Error: Tidak ada kolom teks/komentar di {input_file}")
            return

    # Hapus baris yang kosong pada kolom target
    df = df.dropna(subset=[column_to_process])
    
    # Batasi data jika LIMIT_DATA diatur
    if LIMIT_DATA:
        print(f"Membatasi data hanya {LIMIT_DATA} baris untuk percepatan...")
        df = df.head(LIMIT_DATA)
    
    # Gunakan tqdm untuk progress bar di pandas
    tqdm.pandas()
    
    print("\n[1/3] Melakukan Cleaning & Case Folding...")
    df['cleaned_text'] = df[column_to_process].progress_apply(clean_text)
    
    print("\n[2/3] Menghapus Stopwords (Bahasa Indonesia)...")
    df['no_stopwords'] = df['cleaned_text'].progress_apply(lambda x: stopword.remove(x))
    
    print("\n[3/3] Melakukan Stemming (Sastrawi)...")
    
    print("Mengumpulkan kata unik...")
    all_words = [word for sentence in df['no_stopwords'] for word in str(sentence).split()]
    unique_words = list(set(all_words))
    print(f"Total kata unik: {len(unique_words)}")
    
    stem_cache = {}
    print("Memproses stemming pada kata unik (ini jauh lebih cepat)...")
    for word in tqdm(unique_words, desc="Stemming"):
        stem_cache[word] = stemmer.stem(word)
        
    print("Memetakan kembali kata yang telah di-stem ke dataset...")
    def apply_stem(text):
        words = str(text).split()
        return ' '.join([stem_cache.get(w, w) for w in words])

    df['preprocessed_text'] = df['no_stopwords'].progress_apply(apply_stem)
    
    print(f"\nMenyimpan hasil ke {output_file}...")
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print("\nPreprocessing Selesai!")
    print(f"Total data diproses: {len(df)} baris.")

if __name__ == "__main__":
    # Path file
    INPUT_CSV = "data/processed_comments.csv"
    OUTPUT_CSV = "data/preprocessed_data.csv"
    
    preprocess_data(INPUT_CSV, OUTPUT_CSV)
