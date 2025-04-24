import requests
import json

# === 設定區 ===
USE_MOCK_DATA = False  # True: 使用假資料，False: 呼叫 API
OUTPUT_FILE = "artifacts.json"  # 輸出檔案名稱
PAGES_TO_FETCH = [1, 2]  # 要抓的頁數

url = "https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://wiki.hoyolab.com/",
    "Origin": "https://wiki.hoyolab.com",
    "Cookie": "ltoken_v2=...; mi18nLang=zh-tw"  # ← 放有效 cookie
}


def get_mock_data(page_num):
    return {
        "retcode": 0,
        "message": "OK",
        "data": {
            "list": [
                {
                    "entry_page_id": f"mock_{page_num}_1",
                    "name": f"模擬聖遺物 {page_num}-1",
                    "icon_url": f"https://example.com/icon_{page_num}_1.png",
                    "display_field": {
                        "four_set_effect": "模擬4件套效果...",
                        "two_set_effect": "模擬2件套效果。"
                    }
                },
                {
                    "entry_page_id": f"mock_{page_num}_2",
                    "name": f"模擬聖遺物 {page_num}-2",
                    "icon_url": f"https://example.com/icon_{page_num}_2.png",
                    "display_field": {
                        "four_set_effect": "模擬4件套效果...",
                        "two_set_effect": "模擬2件套效果。"
                    }
                }
            ],
            "total": "55"
        }
    }


def parse_artifact_info(artifact_data):
    return {
        "name": artifact_data["name"],
        "icon": artifact_data["icon_url"],
        "2-piece": artifact_data["display_field"]["two_set_effect"],
        "4-piece": artifact_data["display_field"]["four_set_effect"]
    }


def get_artifact_data(page_num):
    data = {
        "filters": [],
        "menu_id": "5",
        "page_num": page_num,
        "page_size": 50,
        "use_es": True,
        "lang": "zh-tw"
    }

    if USE_MOCK_DATA:
        print(f"[使用模擬資料，第 {page_num} 頁]")
        return get_mock_data(page_num)
    else:
        print(f"[正在取得第 {page_num} 頁資料...]")
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200 and response.json().get("retcode") == 0:
                return response.json()
            else:
                print(f"⚠️ 第 {page_num} 頁 API 錯誤，狀態碼 {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ 請求第 {page_num} 頁失敗:", str(e))
            return None


def main():
    all_artifacts = []

    for page in PAGES_TO_FETCH:
        response_data = get_artifact_data(page)
        if response_data:
            artifacts = response_data["data"]["list"]
            parsed = [parse_artifact_info(art) for art in artifacts]
            all_artifacts.extend(parsed)

    print(f"\n✅ 共收集 {len(all_artifacts)} 套聖遺物，準備寫入 JSON...\n")

    # 寫入 JSON 檔案（含中文格式）
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_artifacts, f, ensure_ascii=False, indent=2)
        print(f"📁 成功輸出到 {OUTPUT_FILE}")
    except Exception as e:
        print("❌ 寫入 JSON 檔失敗:", str(e))

    # 顯示部分結果
    for artifact in all_artifacts[:5]:  # 顯示前 5 筆
        print(f"=== {artifact['name']} ===")
        print(f"圖標: {artifact['icon']}")
        print(f"2件套效果: {artifact['2-piece']}")
        print(f"4件套效果: {artifact['4-piece']}\n")


if __name__ == "__main__":
    main()
