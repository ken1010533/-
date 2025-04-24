import requests
import re
while True:
    entry_id = input("請輸入數字 ID: ")
    if entry_id.isdigit():
        url = "https://sg-wiki-api-static.hoyolab.com/hoyowiki/genshin/wapi/entry_page?entry_page_id=" + entry_id
        break
    else:
        print("輸入無效，請輸入數字。")

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

print("狀態碼:", response.status_code)

try:
    data = response.json()
    print("名稱:", data.get("data", {}).get("page", {}).get("name"))
    # print("回傳資料內容:")
    # print(data)
    
    # 整理資料部分
    print("\n===== 整理後的武器資料 =====")
    page_data = data.get("data", {}).get("page", {})
    # 基本資訊
    print("\n【基本資訊】")
# 用來清理 HTML 標籤的函數
    def clean_html_tags(text):
        return re.sub(r"<.*?>", "", text) if text else text
    print(f'名稱: {clean_html_tags(page_data.get("name", ""))}')
    print(f"ID: {clean_html_tags(page_data.get('id', ''))}")
    print(f"類型: {clean_html_tags(page_data.get('filter_values', {}).get('weapon_type', {}).get('values', [''])[0])}")
    print(f"稀有度: {clean_html_tags(page_data.get('filter_values', {}).get('weapon_rarity', {}).get('values', [''])[0])}")
    weapon_property = page_data.get('filter_values', {}).get('weapon_property', {}).get('values', [])
    副屬性 = clean_html_tags(weapon_property[0]) if weapon_property else "無"
    print(f"副屬性: {副屬性}")
    print(f"描述: {clean_html_tags(page_data.get('desc', ''))}")


# 武器效果1994

    modules = page_data.get('modules', [])
    for module in modules:
        if module.get('name') == '屬性':
            components = module.get('components', [])
            for comp in components:
                if comp.get('component_id') == 'baseInfo':
                    base_info = comp.get('data', '{}')
                    import json
                    try:
                        base_info = json.loads(base_info)
                        print("\n【武器效果】")
                        for item in base_info.get('list', []):
                            key = item.get("key", "")
                            value = item.get("value", [])

                            # 跳過「來源」
                            if key in ["來源", "鍛造素材", "精煉素材", "兌換所需", "故事","七聖召喚", "精煉材料",""]:
                                continue
                            print(f"{key}:")
                            for v in value:
                                import re
                                clean_v = re.sub(r"<.*?>", "", v)  # 去除 HTML 標籤
                                print(f"  {clean_v}")
                    except Exception as e:
                        print(f"Error processing baseInfo: {e}")
# 武器突破
    for module in modules:
        if module.get('name') == '突破':
            components = module.get('components', [])
            for comp in components:
                if comp.get('component_id') == 'ascension':
                    level_data = comp.get('data', '{}')
                    try:

                        level_data = json.loads(level_data)
                        print("\n【突破】")
                        for item in level_data.get('list', []):
                            level_name = item.get('key', '')
                            突破屬性= item.get('combatList', [''])
                            print("  突破屬性:")
                            if len(突破屬性) >= 2:
                                # 第一步：取出屬性名稱
                                keys = 突破屬性[0].get("values", [])
                                # 第二步：取出屬性值
                                values = 突破屬性[1].get("values", [])
                                # 第三步：將屬性名稱與對應數值合併成 dict
                                combat_dict = dict(zip(keys, values))
                                # 第四步：印出結果
                                print(f"  {level_name}:")
                                for key, value in combat_dict.items():
                                    print(f"    {key}: {value}")
                            else:
                                print(f"  {level_name}: 無法解析突破屬性")
                    except Exception as e:
                        print(f"Error processing level: {e}")


    







































except Exception as e:
    print("解析 JSON 失敗:", e)
    print("原始內容:", response.text)