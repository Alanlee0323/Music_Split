#!/usr/bin/env python
"""
Drum Splitter - 從 YouTube 連結自動下載並分離鼓軌道

使用方式：
    python split_drums.py <YouTube URL>
    python split_drums.py <YouTube URL> --keep-drums  # 只保留鼓
    python split_drums.py <YouTube URL> --model htdemucs  # 使用較快的模型
"""
import subprocess
import sys
from pathlib import Path
import shutil
import argparse
from typing import Tuple, Union, Optional


def check_dependencies():
    """檢查必要的工具是否已安裝"""
    # 檢查 yt-dlp
    if shutil.which("yt-dlp") is None:
        print("❌ 未安裝 yt-dlp，請執行: pip install yt-dlp")
        sys.exit(1)
    
    # 檢查 ffmpeg
    if shutil.which("ffmpeg") is None:
        print("❌ 未安裝 ffmpeg，請執行: conda install -c conda-forge ffmpeg")
        sys.exit(1)
    
    # 檢查 demucs
    try:
        import demucs
    except ImportError:
        print("❌ 未安裝 demucs，請執行: pip install -e .")
        sys.exit(1)
    
    print("✅ 所有依賴項已就緒")


def download_audio(url: str, output_dir: Path) -> Path:
    """從 YouTube 下載音頻"""
    print(f"\n🎵 正在下載音頻...")
    
    output_template = str(output_dir / "%(title)s.%(ext)s")
    
    cmd = [
        "yt-dlp",
        "-x",                      # 只抽取音頻
        "--audio-format", "mp3",   # 轉換為 MP3
        "--audio-quality", "0",    # 最佳品質
        "-o", output_template,     # 輸出模板
        "--no-playlist",           # 不下載播放清單
        "--restrict-filenames",    # 限制檔名字符（避免特殊字元問題）
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 下載失敗: {result.stderr}")
        sys.exit(1)
    
    # 找到下載的檔案
    mp3_files = list(output_dir.glob("*.mp3"))
    if not mp3_files:
        print("❌ 找不到下載的音頻檔案")
        sys.exit(1)
    
    # 取得最新的檔案
    audio_file = max(mp3_files, key=lambda f: f.stat().st_mtime)
    print(f"✅ 下載完成: {audio_file.name}")
    
    return audio_file


def separate_drums(audio_file: Path, model: str = "htdemucs_ft", keep_drums: bool = False):
    """使用 Demucs 分離鼓軌道"""
    print(f"\n🥁 正在分離音軌 (使用模型: {model})...")
    print("   這可能需要幾分鐘，請耐心等待...\n")
    
    cmd = [
        sys.executable, "-m", "demucs",
        "-n", model,
        "--two-stems=drums",
        str(audio_file)
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("❌ 音軌分離失敗")
        sys.exit(1)
    
    # 輸出結果位置
    output_dir = Path("separated") / model / audio_file.stem
    
    if keep_drums:
        result_file = output_dir / "drums.wav"
        print(f"\n✅ 完成！鼓軌道已保存至:")
    else:
        result_file = output_dir / "no_drums.wav"
        print(f"\n✅ 完成！去鼓版本已保存至:")
    
    print(f"   📁 {result_file.absolute()}")
    
    # 顯示所有輸出檔案
    print(f"\n📂 所有輸出檔案:")
    for f in output_dir.glob("*.wav"):
        print(f"   - {f.name}")


# 支援的音訊格式
SUPPORTED_FORMATS = [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".aiff"]


def print_header():
    """顯示程式標題"""
    print("\n" + "=" * 60)
    print("🎸 Drum Splitter - 鼓軌分離工具")
    print("=" * 60)
    print()
    print("📌 功能說明：")
    print("   此工具可使用 AI 分離音樂中的鼓軌道。")
    print("   您可以從 YouTube 下載音樂，或使用本地音訊檔案。")
    print("   可選擇只保留鼓聲，或是移除鼓聲保留其他樂器。")
    print()


def get_audio_source() -> Tuple[str, Optional[Union[str, Path]]]:
    """
    互動式取得音訊來源
    
    Returns:
        tuple: (source_type, value)
            - ("youtube", None) + url stored separately
            - ("file", Path) for local file
    """
    print("─" * 60)
    print("📎 步驟 1/4：選擇音訊來源")
    print("─" * 60)
    print()
    print("   請選擇音訊來源：")
    print()
    print("   [1] 🌐 從 YouTube 下載")
    print("       → 輸入 YouTube 連結自動下載")
    print()
    print("   [2] 📁 使用本地檔案")
    print("       → 選擇電腦中已有的音樂檔案")
    print()
    
    while True:
        choice = input("👉 請選擇 [1/2]: ").strip()
        
        if choice == "1":
            return get_youtube_url()
        elif choice == "2":
            return get_local_file()
        else:
            print("⚠️  請輸入 1 或 2")


def get_youtube_url() -> Tuple[str, str]:
    """互動式取得 YouTube 連結"""
    print()
    print("   請貼上 YouTube 影片連結，支援以下格式：")
    print("   • https://www.youtube.com/watch?v=VIDEO_ID")
    print("   • https://youtu.be/VIDEO_ID")
    print("   • https://music.youtube.com/watch?v=VIDEO_ID")
    print()
    
    while True:
        url = input("🔗 請輸入連結: ").strip()
        if url:
            if "youtube.com" in url or "youtu.be" in url:
                print(f"   ✓ 已取得連結")
                return ("youtube", url)
            else:
                print("⚠️  這不像是有效的 YouTube 連結，請重新輸入。")
        else:
            print("⚠️  連結不可為空，請重新輸入。")


def get_local_file() -> Tuple[str, Path]:
    """互動式取得本地檔案路徑"""
    print()
    print("   支援的音訊格式：")
    print(f"   {', '.join(SUPPORTED_FORMATS)}")
    print()
    print("   💡 提示：可直接將檔案拖曳到此視窗")
    print()
    
    while True:
        file_path = input("📂 請輸入檔案路徑: ").strip()
        
        # 移除可能的引號（拖曳檔案時可能會有）
        file_path = file_path.strip('"').strip("'")
        
        if not file_path:
            print("⚠️  路徑不可為空，請重新輸入。")
            continue
        
        path = Path(file_path)
        
        if not path.exists():
            print(f"⚠️  找不到檔案：{path}")
            print("   請確認路徑是否正確。")
            continue
        
        if not path.is_file():
            print("⚠️  這不是一個檔案，請輸入檔案路徑。")
            continue
        
        if path.suffix.lower() not in SUPPORTED_FORMATS:
            print(f"⚠️  不支援的格式：{path.suffix}")
            print(f"   支援的格式：{', '.join(SUPPORTED_FORMATS)}")
            continue
        
        print(f"   ✓ 已選擇：{path.name}")
        return ("file", path)


def get_output_mode() -> bool:
    """互動式選擇輸出模式"""
    print()
    print("─" * 60)
    print("🎚️  步驟 2/4：選擇輸出模式")
    print("─" * 60)
    print()
    print("   您想要什麼樣的輸出？")
    print()
    print("   [1] 🥁 只保留鼓聲 (drums.wav)")
    print("       → 適合練習其他樂器、分析鼓的編排")
    print()
    print("   [2] 🎸 移除鼓聲 (no_drums.wav)")
    print("       → 適合練習打鼓、製作卡拉OK伴奏")
    print()
    
    while True:
        choice = input("👉 請選擇 [1/2] (預設: 2): ").strip()
        if choice == "" or choice == "2":
            print("   ✓ 已選擇：移除鼓聲")
            return False  # keep_drums = False
        elif choice == "1":
            print("   ✓ 已選擇：只保留鼓聲")
            return True   # keep_drums = True
        else:
            print("⚠️  請輸入 1 或 2")


def get_model() -> str:
    """互動式選擇模型"""
    print()
    print("─" * 60)
    print("🤖 步驟 3/4：選擇 AI 模型")
    print("─" * 60)
    print()
    print("   不同模型有不同的特性：")
    print()
    print("   [1] htdemucs_ft (精調版) ⭐ 推薦")
    print("       → 最佳音質，適合大多數音樂")
    print("       → 處理時間：較長")
    print()
    print("   [2] htdemucs (標準版)")
    print("       → 平衡的音質與速度")
    print("       → 處理時間：適中")
    print()
    print("   [3] htdemucs_6s (六聲道版)")
    print("       → 可分離更多樂器 (鋼琴、吉他)")
    print("       → 處理時間：較長")
    print()
    print("   [4] hdemucs_mmi (實驗版)")
    print("       → 實驗性模型")
    print("       → 處理時間：適中")
    print()
    
    models = {
        "1": "htdemucs_ft",
        "2": "htdemucs",
        "3": "htdemucs_6s",
        "4": "hdemucs_mmi",
    }
    
    while True:
        choice = input("👉 請選擇 [1/2/3/4] (預設: 1): ").strip()
        if choice == "" or choice == "1":
            print("   ✓ 已選擇：htdemucs_ft (精調版)")
            return "htdemucs_ft"
        elif choice in models:
            model = models[choice]
            print(f"   ✓ 已選擇：{model}")
            return model
        else:
            print("⚠️  請輸入 1、2、3 或 4")


def get_output_dir() -> Path:
    """互動式選擇輸出目錄"""
    print()
    print("─" * 60)
    print("📁 步驟 4/4：設定下載目錄")
    print("─" * 60)
    print()
    print("   下載的音頻檔案將暫存於此目錄。")
    print("   分離後的結果會存放在 separated/ 目錄下。")
    print()
    
    default_dir = Path("downloads")
    user_input = input(f"👉 請輸入目錄路徑 (預設: {default_dir}): ").strip()
    
    if user_input:
        output_dir = Path(user_input)
    else:
        output_dir = default_dir
    
    print(f"   ✓ 下載目錄：{output_dir.absolute()}")
    return output_dir


def confirm_settings(source_type: str, source_value: Union[str, Path], keep_drums: bool, model: str, output_dir: Path) -> bool:
    """確認所有設定"""
    print()
    print("=" * 60)
    print("📋 設定確認")
    print("=" * 60)
    print()
    
    if source_type == "youtube":
        print(f"   🌐 音訊來源：YouTube")
        print(f"   🔗 連結：{source_value}")
    else:
        print(f"   📁 音訊來源：本地檔案")
        print(f"   🎵 檔案：{source_value}")
    
    print(f"   🎚️  輸出模式：{'只保留鼓聲' if keep_drums else '移除鼓聲'}")
    print(f"   🤖 AI 模型：{model}")
    
    if source_type == "youtube":
        print(f"   📁 下載目錄：{output_dir.absolute()}")
    
    print()
    
    while True:
        confirm = input("👉 確認開始處理？[Y/n]: ").strip().lower()
        if confirm in ["", "y", "yes"]:
            return True
        elif confirm in ["n", "no"]:
            print("❌ 已取消操作")
            return False
        else:
            print("⚠️  請輸入 Y 或 N")


def main():
    parser = argparse.ArgumentParser(description="Drum Splitter")
    parser.add_argument("input", nargs="?", help="Input file path or YouTube URL")
    parser.add_argument("--model", default="htdemucs_ft", help="Model to use (default: htdemucs_ft)")
    parser.add_argument("--keep-drums", action="store_true", help="Keep drums only (default: remove drums)")
    args = parser.parse_args()

    # 顯示標題
    print_header()
    
    # 檢查依賴
    check_dependencies()
    
    if args.input:
        # 非互動模式 (CLI)
        source_value = args.input
        if "youtube.com" in source_value or "youtu.be" in source_value:
            source_type = "youtube"
            # 對於 CLI YouTube 下載，預設下載到 downloads
            output_dir = Path("downloads") 
        else:
            source_type = "file"
            source_value = Path(source_value)
            if not source_value.exists():
                print(f"❌ 找不到檔案: {source_value}")
                sys.exit(1)
            output_dir = Path("downloads") # 本地檔案不需要，但保持變數一致
            
        keep_drums = args.keep_drums
        model = args.model
        print(f"🤖 使用模型: {model}")
        print(f"🎚️  模式: {'只保留鼓聲' if keep_drums else '移除鼓聲'}")
        
    else:
        # 互動式取得參數
        source_type, source_value = get_audio_source()
        keep_drums = get_output_mode()
        model = get_model()
        
        # 只有 YouTube 來源需要選擇下載目錄
        if source_type == "youtube":
            output_dir = get_output_dir()
        else:
            output_dir = Path("downloads")
        
        # 確認設定
        if not confirm_settings(source_type, source_value, keep_drums, model, output_dir):
            sys.exit(0)
    
    print()
    print("=" * 60)
    print("🚀 開始處理")
    print("=" * 60)
    
    # 根據來源類型取得音訊檔案
    if source_type == "youtube":
        # 建立下載目錄
        output_dir.mkdir(exist_ok=True)
        # 下載音頻
        audio_file = download_audio(source_value, output_dir)
    else:
        # 使用本地檔案
        audio_file = source_value
        print(f"\n🎵 使用本地檔案：{audio_file.name}")
    
    # 分離鼓軌道
    separate_drums(audio_file, model, keep_drums)
    
    print("\n" + "=" * 60)
    print("🎉 全部完成！")
    print("=" * 60)
    print()
    print("💡 小提示：")
    print("   • 輸出檔案位於 separated/ 目錄下")
    print("   • drums.wav = 鼓軌道")
    print("   • no_drums.wav = 無鼓伴奏")
    print()


if __name__ == "__main__":
    main()
