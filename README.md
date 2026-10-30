
# ずんだスクリプト

指定したテキストをずんだもんの声で読み上げてくれたり、読み上げ音声ファイルを作ってくれるツールです。  
**bashのスクリプト**です。

---

## セットアップ方法

### 1. VOICEVOXエンジンを用意する

VOICEVOXエンジンを起動します。zundaを動かすPCと別のPCで動かす場合は、
そのエンジンへ接続できるようにしておきます。
詳しくは [VOICEVOXエンジン](https://github.com/VOICEVOX/voicevox_engine) を参照してください。

Ubuntu / WSL では、必要なコマンドを次のようにインストールできます。

```bash
sudo apt update
sudo apt install curl jq ffmpeg
```

### 2. zundaをインストールする

プロジェクトを取得し、そのディレクトリへ移動したうえで、次を実行します。

```bash
mkdir -p "$HOME/bin"
chmod +x src/zunda
ln -s "$(pwd)/src/zunda" "$HOME/bin/zunda"
```

すでに ~/bin/zunda がある場合、まず中身や設定を確認し、必要に応じて
バックアップしてください。上記の ln は既存ファイルを上書きしません。
~/bin がPATHに含まれない場合は、シェルの設定に追加してください。
このリンクを使うと、プロジェクトの src/zunda が実行されます。

### 3. 個人設定を作る

同じPCでエンジンを使う場合は設定なしでも動きます。変更したいときは
~/.config/zunda/config を作って編集してください。

```bash
mkdir -p "$HOME/.config/zunda"
nano "$HOME/.config/zunda/config"
chmod 600 "$HOME/.config/zunda/config"
```

設定ファイルの例です。接続先が別のPCなら、ホスト名をそのPCに合わせます。

```bash
VOICEVOX_ENGINE_HOST="localhost"
VOICEVOX_ENGINE_PORT="50021"
SPEAKER_ID=3
SAMPLING_RATE=24000
```

設定できる項目は次のとおりです。必要な行だけ書けば、残りは既定値が使われます。

- VOICEVOX_ENGINE_HOST、VOICEVOX_ENGINE_PORT: エンジンの接続先
- SPEAKER_ID: 話者ID。zunda --list-speakers で一覧を確認できます。
- SAMPLING_RATE: 出力のサンプリング周波数
- SPEED、PITCH、INTONATION、VOLUME: 話し方の調整
- PRE_PHONEME_LENGTH、POST_PHONEME_LENGTH、PAUSE_LENGTH_SCALE: 無音や間の調整
- SENTENCE_INTERVAL: ファイル出力時の文の間隔
- MAX_JOBS: 同時に合成する数
- INPUT_ENCODING: ファイルと標準入力の文字コード
- LOG_FILE、LOG_OUTPUT: ログの保存先とログ出力の有無

優先順位は **プログラムの既定値 → 個人設定 → 実行時のフラグ** です。
たとえば zunda --speaker 3 は、その実行だけ個人設定の話者IDを上書きします。
XDG_CONFIG_HOME を設定している場合は、そのディレクトリの
zunda/config を読み込みます。

設定ファイルはシェルの書式で読み込まれるため、信頼できる内容だけを書いてください。
個人設定はGit管理外に置かれるので、プロジェクトをGitで更新しても残ります。

**以前の版から移行する場合:** 古い zunda の先頭に直接書いた接続先や
変更した既定値を確認し、対応する項目を個人設定に写してください。
元のファイルやバックアップは、移行後の動作を確かめるまで保管してください。
すでに個人設定ファイルがある場合は、上書きせず内容を確認してください。

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

入力テキストは既定で UTF-8 として読み込みます。Shift-JIS や EUC-JP の
ファイル・標準入力を使う場合は文字コードを明示してください。

    zunda --input-encoding SHIFT-JIS -i text.txt -o voice.wav
    cat text.txt | zunda --input-encoding EUC-JP -o voice.wav

複数の入力を指定した場合は、標準入力、コマンド引数、ファイルの順に
連結します。コマンド引数は UTF-8 として扱います。UTF-8 でない入力を
指定なしで渡した場合は、誤変換を避けるためエラーで停止します。

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
      zunda "こんにちは" --stdout | ffplay -nodisp -autoexit -
      zunda "こんにちは" --stdout | aplay
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
