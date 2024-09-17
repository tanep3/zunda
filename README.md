
# ずんだスクリプト

指定したテキストをずんだもんの声で読み上げてくれたり、読み上げ音声ファイルを作ってくれるツールです。  
**bashのスクリプト**です。

---

## セットアップ方法

1. **voicevox_engine のセットアップ**

   まず、`voicevox_engine` をご自宅のサーバで稼働させます。  
   `-p` オプションを `'0.0.0.0:50021:50021'` で動かすと、LAN内の他のPCからもアクセスできるようになります。

   詳しくは[こちら](https://github.com/VOICEVOX/voicevox_engine)を参照ください。

2. **zundaスクリプトのインストール**

   `zunda` スクリプトを、ご自宅のパソコン（Mac, RaspiOS, Ubuntu, WSL, Cygwin等）にダウンロードし、`/usr/local/bin` に配置します。

   ```bash
   sudo mv zunda /usr/local/bin/zunda
   sudo chmod +x /usr/local/bin/zunda
   ```

   `zunda` スクリプトをエディタで開き、一番上の変数 `VOICEVOX_ENGINE_HOST` の値を、`voicevox_engine` が動いているサーバのIPアドレスに変更します。

3. **必要なツールのインストール**

   `zunda` スクリプトを動かす上で、以下のツール類をインストールします。

   ```bash
   sudo apt update
   sudo apt install jq ffmpeg
   ```

---

## 基本の使い方

1. **ヘルプ出力**

   ```bash
   zunda -h
   zunda --help
   ```

2. **しゃべらせる**

   1. テキスト指定

      ```bash
      zunda "こんにちは"
      zunda "こんにちは" "いい天気ですね"
      ```

   2. ファイル指定

      ```bash
      zunda -i text.txt
      ```

   3. 標準入力からのリダイレクト

      ```bash
      echo "こんにちは" | zunda
      ```

3. **ファイルに出力**

   音声ファイルフォーマットは、ファイル名に指定した拡張子で自動認識します。

   1. WAVファイルに出力

      ```bash
      zunda "こんにちは" -o voice.wav
      ```

   2. MP3ファイルに出力

      ```bash
      zunda "こんにちは" -o voice.mp3
      ```

   3. AAC (iPhoneの音楽ファイル形式) に出力

      ```bash
      zunda "こんにちは" -o voice.aac
      ```

   4. OGG (高圧縮の音楽フォーマット) に出力

      ```bash
      zunda "こんにちは" -o voice.ogg
      ```

4. **標準出力に音楽データを出力**

   ※ 出力データはWAVフォーマットです。

   1. 再生アプリに直接出力して聞く

      ```bash
      zunda "こんにちは" --stdout > play
      zunda "こんにちは" --stdout > aplay
      ```

   2. ファイルにリダイレクト出力

      ```bash
      zunda "こんにちは" --stdout > voice.wav
      ```

---

## 応用編

以下のスクリプト例は、`text.txt` の内容と "直接入力"、"たねちゃんねるです"、`book.txt` の内容を連結し、音声変換して `voice.mp3` ファイルを作成し、同時に `voice.wav` にも出力します。

```bash
cat text.txt | zunda "直接入力" -i book.txt "たねちゃんねるです" --log -o voice.mp3 --stdout > voice.wav
```
