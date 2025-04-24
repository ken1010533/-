import requests
import json
import re
from urllib.parse import quote
import sys


def 獲取武器詳細參數():
        # 清除 HTML 標籤的函數
    def clean_html_tags(text):
        return re.sub(r"<.*?>", "", text) if text else text

    # 讀取多筆 ID
    entry_ids = all_ids

    for entry_id in entry_ids:
        entry_id = entry_id.strip()
        if not entry_id.isdigit():
            寫入(f"輸入無效，略過 ID: {entry_id}")
            continue

        url = "https://sg-wiki-api-static.hoyolab.com/hoyowiki/genshin/wapi/entry_page?entry_page_id=" + entry_id
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://wiki.hoyolab.com",
            "Referer": "https://wiki.hoyolab.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "x-rpc-language": "zh-tw",
            "x-rpc-wiki_app": "genshin",
        }

        response = requests.get(url, headers=headers)
        寫入("-----------------------------------------------------------------------------\n\n")
        寫入(f"\n===== ID: {entry_id} 的資料 =====")
        寫入("狀態碼:", response.status_code)

        try:
            data = response.json()
            page_data = data.get("data", {}).get("page", {})

            寫入("\n【基本資訊】")
            寫入(f'名稱: {clean_html_tags(page_data.get("name", ""))}')
            寫入(f"ID: {clean_html_tags(page_data.get('id', ''))}")
            寫入(f"類型: {clean_html_tags(page_data.get('filter_values', {}).get('weapon_type', {}).get('values', [''])[0])}")
            寫入(f"稀有度: {clean_html_tags(page_data.get('filter_values', {}).get('weapon_rarity', {}).get('values', [''])[0])}")
            weapon_property = page_data.get('filter_values', {}).get('weapon_property', {}).get('values', [])
            副屬性 = clean_html_tags(weapon_property[0]) if weapon_property else "無"
            寫入(f"副屬性: {副屬性}")
            寫入(f"描述: {clean_html_tags(page_data.get('desc', ''))}")

            modules = page_data.get('modules', [])
            for module in modules:
                if module.get('name') == '屬性':
                    components = module.get('components', [])
                    for comp in components:
                        if comp.get('component_id') == 'baseInfo':
                            base_info = json.loads(comp.get('data', '{}'))
                            寫入("\n【武器效果】")
                            for item in base_info.get('list', []):
                                key = item.get("key", "")
                                value = item.get("value", [])
                                if key in ["來源", "鍛造素材", "精煉素材", "兌換所需", "故事","七聖召喚", "精煉材料","鍛造材料",""]:
                                    continue
                                寫入(f"{key}:")
                                for v in value:
                                    clean_v = clean_html_tags(v)
                                    寫入(f"  {clean_v}")
            
            for module in modules:
                if module.get('name') == '突破':
                    components = module.get('components', [])
                    for comp in components:
                        if comp.get('component_id') == 'ascension':
                            level_data = json.loads(comp.get('data', '{}'))
                            寫入("\n【突破】")
                            for item in level_data.get('list', []):
                                level_name = item.get('key', '')
                                突破屬性 = item.get('combatList', [''])
                                寫入(f"  {level_name}:")
                                if len(突破屬性) >= 2:
                                    keys = 突破屬性[0].get("values", [])
                                    values = 突破屬性[1].get("values", [])
                                    combat_dict = dict(zip(keys, values))
                                    寫入("  突破屬性:")
                                    for key, value in combat_dict.items():
                                        寫入(f"    {key}: {value}")

                                else:
                                    寫入("    無法解析突破屬性")

        except Exception as e:
            寫入("解析 JSON 失敗:", e)
            寫入("原始內容:", response.text)


def 獲取武器ID():

    global all_ids
    url= "https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list"

    # 設定 Headers，包含多個 cookie，使用分號隔開
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://wiki.hoyolab.com/",
        "Origin": "https://wiki.hoyolab.com",
        "Cookie":quote("ltoken_v2=v2_CAISDGN3a2o5dno3cGNzZxokYjQ1MGNhYTctMjRhZC00ODBhLTg2NmMtYTQwYTlmMzViNzc1IKbr4r8GKK7Mks0EMN7u-mFCC2Jic19vdmVyc2Vh.prX4ZwAAAAAB.MEYCIQDhOXj68xZdoNjXOuQnBQhqDHvcJrwF-g9bDh9LiftYXwIhAKyqlWSL46aDNwG_nwrceIAClD8-GFW5UuejN-73bKJa; mi18nLang=zh-tw")
    }

    # 設定 POST 傳送的資料（這邊 menu_id: 5 是聖遺物，可依需求調整）
    data = {
        "filters": [],
        "menu_id": "4",
        "page_num": 1,
        "page_size": 30,
        "use_es": True,
        "lang": "zh-tw"
    }

    # 發送請求
    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    total_pages = result.get("data", {}).get("page_total", 8)

    # 初始化 all_ids 為空列表
    all_ids = []

    # 依據總頁數分頁抓取
    for page in range(1, total_pages + 1):
        data["page_num"] = page
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        entries = result.get("data", {}).get("list", [])
        for entry in entries:
            entry_id = entry.get("entry_page_id", "")
            if entry_id:
                all_ids.append(str(entry_id))

    # 用逗號分隔所有 ID 輸出
    id_string = ",".join(all_ids)
    寫入("全部 ID（共 {} 筆）:".format(len(all_ids)))
    寫入(id_string)



# 設定一個全域變數來追蹤是否為第一次寫入
first_write = True

def 寫入(*args, **kwargs):
    global first_write
    # 檢查是否是第一次寫入
    if first_write:
        # 第一次寫入時清空檔案
        with open('output.txt', 'w', encoding='utf-8') as f:
            print(*args, **kwargs, file=f)
        first_write = False  # 設置為 False，表示後續寫入不再清空檔案
    else:
        # 之後的寫入不清空檔案，直接附加
        with open('output.txt', 'a', encoding='utf-8') as f:
            print(*args, **kwargs, file=f)



# 重設所有 寫入 以使用 寫入
sys.stdout = sys.__stdout__  # 恢復 寫入 預設輸出

獲取武器ID()
獲取武器詳細參數()