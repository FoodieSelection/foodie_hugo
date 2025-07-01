import json
import glob
import os

# 讀取所有 json 檔案
output_filename = 'city_awards.json'
json_files = [
    f for f in glob.glob('../data/**/*.json', recursive=True)
    if not f.endswith(output_filename)
]

all_data = []
for file in json_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for idx, item in enumerate(data, 1):
            # 檢查必要欄位
            try:
                item['city']
                item['award']
                for award in item.get('award', []):
                    award['name']
            except KeyError as e:
                print(f'檔案: {file}, 第 {idx} 筆資料缺少 key: {e}')
                print(f'資料內容: {item}')
                continue
        all_data.extend(data)

# 用字典暫存每個城市的獎項名稱（不重複）
city_awards = {}
all_cities_awards = set()
for item in all_data:
    city = item.get('city')
    if city not in city_awards:
        city_awards[city] = set()
    for award in item.get('award', []):
        name = award.get('name')
        if name:
            city_awards[city].add(name)
            all_cities_awards.add(name)

# 整理成輸出格式
output_data = [
    {
        "city": city,
        "awards": ["所有獎項"] + sorted(list(awards))
    }
    for city, awards in city_awards.items()
]
# 加入「全部城市」的獎項集合
output_data.append({
    "city": "所有城市",
    "awards": ["所有獎項"] + sorted(list(all_cities_awards))
})

# 寫入檔案
output_path = f'../static/data/{output_filename}'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
