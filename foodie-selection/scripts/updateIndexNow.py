import xml.etree.ElementTree as ET
import requests
import math

# —— 參數設定 —— #
SITEMAP_FILE = "../public/sitemap.xml"                     # sitemap 檔案路徑
API_KEY = "829a24b7168846118d06c01c75b76651"           # 將此處改成您的 IndexNow API Key
HOST = "foodie.selection.com.tw"                         # 您網站的 host（不含 https://）
ENDPOINT = "https://api.indexnow.org/indexnow"   # IndexNow 批量提交端點
MAX_URLS_PER_BATCH = 20                       # 每次提交的最大 URL 數量

# —— 從 sitemap.xml 解析所有 URL —— #
def parse_sitemap(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    # 處理 namespace
    ns = {"ns": root.tag.split("}")[0].strip("{")}
    urls = [elem.text for elem in root.findall(".//ns:loc", ns)]
    return urls

# —— 分批提交 —— #
def submit_batch(url_list):
    payload = {
        "host": HOST,
        "key": API_KEY,
        "urlList": url_list
    }
    headers = { "Content-Type": "application/json; charset=utf-8" }
    resp = requests.post(ENDPOINT, json=payload, headers=headers)
    return resp.status_code, resp.text

def main():
    urls = parse_sitemap(SITEMAP_FILE)
    total = len(urls)
    print(f"共解析到 {total} 個 URL，開始分批提交……")

    batches = math.ceil(total / MAX_URLS_PER_BATCH)
    for i in range(batches):
        start = i * MAX_URLS_PER_BATCH
        end = start + MAX_URLS_PER_BATCH
        batch_urls = urls[start:end]
        status, text = submit_batch(batch_urls)
        print(f"第 {i+1}/{batches} 批 ({len(batch_urls)} 條) 提交結果：HTTP {status}")
        if status != 200:
            print("回應內容：", text)

if __name__ == "__main__":
    main()
