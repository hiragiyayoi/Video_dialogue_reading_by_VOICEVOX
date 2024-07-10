import requests
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import simpledialog, filedialog
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import os

API_ENDPOINT = "http://127.0.0.1:50021/audio_query"
SPEAKER_ID = 1
OUTPUT_DIR = "talk_wav"  # グローバル変数として定義

def text_to_speech_from_file(text_filename, audio_filename):
    # OUTPUT_DIR を引数で受け取るように変更
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # talk_wavフォルダが存在しない場合は作成

    with open(text_filename.replace('.txt', '.csv'), 'r') as text_file:
        for i, line in enumerate(text_file):
            text = line.strip()
            if not text:  # 空行はスキップ
                continue

            params = {"text": text, "speaker": SPEAKER_ID}
            timeout = 15
            response = requests.post(API_ENDPOINT, params=params, timeout=timeout)
            if response.status_code != 200:
                print(f"行 {i+1} の音声合成クエリの取得に失敗しました。")
                continue

            synthesis_endpoint = "http://127.0.0.1:50021/synthesis?speaker=1"
            synthesis_params = response.json()
            synthesis_response = requests.post(synthesis_endpoint, json=synthesis_params)
            if synthesis_response.status_code != 200:
                print(f"行 {i+1} の音声合成に失敗しました。")
                continue

            output_filename = os.path.join(OUTPUT_DIR, f"voicevox_{audio_filename}_{i+1}.wav")
            with open(output_filename, 'wb') as wav_file:
                wav_file.write(synthesis_response.content)

            print(f"VOICEVOX音声ファイルが {output_filename} に保存されました。")


def extract_audio_from_video(video_path, audio_filename, text_filename):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(f"extracted_{audio_filename}")
    audio_clip.close()
    video_clip.close()
    print(f"動画から抽出した音声が extracted_{audio_filename} に保存されました。")
    audio_to_text(f"extracted_{audio_filename}", text_filename)

def audio_to_text(audio_file_path, text_filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ja-JP')
            # テキストを半角スペースで分割し、CSV形式で保存
            text_lines = text.split(' ')
            csv_text = '\n'.join(text_lines)
            with open(text_filename.replace('.txt', '.csv'), 'w') as text_file:
                text_file.write(csv_text)
            print(f"抽出した音声のテキストが {text_filename.replace('.txt', '.csv')} に保存されました。")
        except sr.UnknownValueError:
            print("音声を認識できませんでした。")
        except sr.RequestError as e:
            print(f"音声認識サービスからの応答エラー: {e}")
            
def main():
    root = tk.Tk()
    root.title("動画音声抽出＆音声合成")

    # ファイル名入力用のフレーム
    file_frame = ttk.Frame(root, padding=10)
    file_frame.pack()

    ttk.Label(file_frame, text="音声ファイル名 (.wav):").grid(row=0, column=0, sticky=tk.W)
    audio_entry = ttk.Entry(file_frame, width=30)
    audio_entry.grid(row=0, column=1, padx=5)

    ttk.Label(file_frame, text="テキストファイル名 (.txt):").grid(row=1, column=0, sticky=tk.W)
    text_entry = ttk.Entry(file_frame, width=30)
    text_entry.grid(row=1, column=1, padx=5)

    # 動画ファイル選択ボタン
    def select_video():
        video_path = filedialog.askopenfilename(
            title="音声を抽出する動画ファイルを選択してください",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov"),
                ("All files", "*.*"),
            ],
        )
        if video_path:
            video_label.config(text=video_path)

    video_button = ttk.Button(root, text="動画ファイルを選択", command=select_video)
    video_button.pack(pady=10)
    video_label = ttk.Label(root, text="")
    video_label.pack()

    # 実行ボタン
    def run():
        OUTPUT_DIR = "talk_wav"  # 生成されるファイルを保存するディレクトリ
        audio_filename = os.path.join(OUTPUT_DIR, audio_entry.get())
        text_filename = os.path.join(OUTPUT_DIR, text_entry.get())
        video_path = video_label.cget("text")

        if video_path and audio_filename and text_filename:
            extract_audio_from_video(video_path, audio_filename, text_filename)
            text_to_speech_from_file(text_filename, audio_filename)  # OUTPUT_DIR を引数として渡す
        else:
            print("必要な情報が入力されていません。")
            # エラーメッセージを表示するなどの処理を追加しても良いでしょう。

    run_button = ttk.Button(root, text="実行", command=run)
    run_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
