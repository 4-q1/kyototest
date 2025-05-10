# kyototest
特別協力 by koko1928


Q-1用のコードの旧バージョンの実装。


Renderを使用したバックエンドで動作するためのコードとなっている。


---

### ✅ 1. Ubuntuのインストールと初期設定

1. **Ubuntu ServerのISOをダウンロード**

   * [https://ubuntu.com/download/server](https://ubuntu.com/download/server)

2. **USBに書き込んでインストール**

   * [Rufus](https://rufus.ie/) などで書き込み → サーバーに挿して起動

3. **初期設定（ログイン後）**

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install git python3-pip python3-venv -y
   ```

---

### ✅ 2. GitHubからプロジェクトをClone

```bash
cd ~
git clone https://github.com/4-q1/kyototest.git
cd kyototest
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### ✅ 3. Flaskアプリの起動（テスト）

```bash
python app.py
```

* `http://localhost:5000/` が立ち上がる（この時点ではローカルでのみアクセス可能）

---

### ✅ 4. Cloudflare Tunnelの準備

#### 4-1. cloudflared のインストール

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

#### 4-2. Cloudflare にログイン & トンネル作成

```bash
cloudflared login
```

* ブラウザは開けない場合：

  * 他PCのブラウザで提示されたURLを開き、Cloudflareアカウントでログインして認証完了
  * 認証ファイルが `.cloudflared/` に保存される

#### 4-3. トンネル作成と設定

```bash
cloudflared tunnel create kyoto-app
```

* トンネルIDが発行される → メモしておく

#### 4-4. `config.yml` の設置

```bash
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```

テンプレート内容：

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /home/youruser/.cloudflared/<YOUR_TUNNEL_ID>.json

ingress:
  - service: http://localhost:5000
  - service: http_status:404
```

※ `youruser` → あなたのUbuntuユーザー名に変更

---

### ✅ 5. トンネル起動 & サーバー公開

```bash
cloudflared tunnel run kyoto-app
```

→ 表示されるURL（例: `https://random-string.trycloudflare.com`）にアクセスすれば外部からアプリが見える！

---

### ✅ 6. 自動起動設定（任意）

```bash
sudo cloudflared service install
```

これでOS再起動後も自動でトンネルが起動します。

---




