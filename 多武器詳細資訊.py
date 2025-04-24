import requests
import re
import json

# 清除 HTML 標籤的函數
def clean_html_tags(text):
    return re.sub(r"<.*?>", "", text) if text else text

# 讀取多筆 ID
entry_ids = input("請輸入數字 ID（可用逗號分隔）: ").split(",")

for entry_id in entry_ids:
    entry_id = entry_id.strip()
    if not entry_id.isdigit():
        print(f"輸入無效，略過 ID: {entry_id}")
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
    print(f"\n===== ID: {entry_id} 的資料 =====")
    print("狀態碼:", response.status_code)

    try:
        data = response.json()
        page_data = data.get("data", {}).get("page", {})

        print("\n【基本資訊】")
        print(f'名稱: {clean_html_tags(page_data.get("name", ""))}')
        print(f"ID: {clean_html_tags(page_data.get('id', ''))}")
        print(f"類型: {clean_html_tags(page_data.get('filter_values', {}).get('weapon_type', {}).get('values', [''])[0])}")
        print(f"稀有度: {clean_html_tags(page_data.get('filter_values', {}).get('weapon_rarity', {}).get('values', [''])[0])}")
        weapon_property = page_data.get('filter_values', {}).get('weapon_property', {}).get('values', [])
        副屬性 = clean_html_tags(weapon_property[0]) if weapon_property else "無"
        print(f"副屬性: {副屬性}")
        print(f"描述: {clean_html_tags(page_data.get('desc', ''))}")

        modules = page_data.get('modules', [])
        for module in modules:
            if module.get('name') == '屬性':
                components = module.get('components', [])
                for comp in components:
                    if comp.get('component_id') == 'baseInfo':
                        base_info = json.loads(comp.get('data', '{}'))
                        print("\n【武器效果】")
                        for item in base_info.get('list', []):
                            key = item.get("key", "")
                            value = item.get("value", [])
                            if key in ["來源", "鍛造素材", "精煉素材", "兌換所需", "故事", ""]:
                                continue
                            print(f"{key}:")
                            for v in value:
                                clean_v = clean_html_tags(v)
                                print(f"  {clean_v}")
        
        for module in modules:
            if module.get('name') == '突破':
                components = module.get('components', [])
                for comp in components:
                    if comp.get('component_id') == 'ascension':
                        level_data = json.loads(comp.get('data', '{}'))
                        print("\n【突破】")
                        for item in level_data.get('list', []):
                            level_name = item.get('key', '')
                            突破屬性 = item.get('combatList', [''])
                            print(f"  {level_name}:")
                            if len(突破屬性) >= 2:
                                keys = 突破屬性[0].get("values", [])
                                values = 突破屬性[1].get("values", [])
                                combat_dict = dict(zip(keys, values))
                                print("  突破屬性:")
                                for key, value in combat_dict.items():
                                    print(f"    {key}: {value}")
                            else:
                                print("    無法解析突破屬性")

    except Exception as e:
        print("解析 JSON 失敗:", e)
        print("原始內容:", response.text)
