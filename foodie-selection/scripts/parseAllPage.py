import json
import glob
import os
import re
import yaml
from collections import OrderedDict
from datetime import datetime

# 讀取餐廳資料
json_files = [f for f in glob.glob('../data/**/*.json', recursive=True)]
all_restaurants = []
for file in json_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_restaurants.extend(data)

# 讀取篩選資料
with open('../static/data/city_districts.json', 'r', encoding='utf-8') as f:
    city_districts = json.load(f)

with open('../static/data/city_awards.json', 'r', encoding='utf-8') as f:
    city_awards = json.load(f)

with open('../static/data/year.json', 'r', encoding='utf-8') as f:
    years = json.load(f)

# 建立城市->獎項的映射字典
city_awards_dict = {item['city']: item['awards'] for item in city_awards}

# 主處理函式
def generate_pages():
    today = datetime.now().strftime("%Y-%m-%d")
    batch_size = 9
    
    # 遍歷所有篩選組合
    for city_data in city_districts:
        city_name = city_data['city']
        
        for district_name in city_data['district']:
            # 獲取當前城市對應的獎項
            awards = city_awards_dict.get(city_name, [])
            
            for award_name in awards:
                for year_name in years:
                    # 篩選符合條件的餐廳
                    filtered_restaurants = filter_restaurants(
                        all_restaurants,
                        city_name,
                        district_name,
                        award_name,
                        str(year_name)  # 確保年份是字串
                    )
                    
                    # 計算分頁數
                    total_count = len(filtered_restaurants)
                    num_pages = (total_count + batch_size - 1) // batch_size
                    
                    # 分頁處理
                    for page in range(num_pages):
                        start_idx = page * batch_size
                        end_idx = min(start_idx + batch_size, total_count)
                        page_restaurants = filtered_restaurants[start_idx:end_idx]
                        
                        # 生成Markdown內容
                        md_content = generate_md_content(
                            page_restaurants,
                            today,
                            city_name,
                            district_name,
                            award_name,
                            year_name,
                            page + 1,
                            total_count
                        )
                        
                        # 建立輸出路徑
                        dir_path = build_output_path(
                            city_name,
                            district_name,
                            award_name,
                            year_name,
                            page + 1
                        )
                        os.makedirs(dir_path, exist_ok=True)
                        file_path = os.path.join(dir_path, '_index.md')
                        
                        # 比較檔案內容（忽略 dateModified）
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                old_content = f.read()
                            if (remove_date_modified(old_content).strip() ==
                                    remove_date_modified(md_content).strip()):
                                # 內容未實質變動，跳過寫檔
                                continue
                        # 寫入檔案
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(md_content)

# 餐廳篩選函式
def filter_restaurants(restaurants, city, district, award, year):
    filtered = []
    
    for rest in restaurants:
        # 城市過濾
        if city != "所有城市" and rest.get('city') != city:
            continue
            
        # 行政區過濾
        if district != "所有行政區" and rest.get('district') != district:
            continue
            
        # 獎項過濾
        award_match = False
        if award != "所有獎項":
            for a in rest.get('award', []):
                if a.get('name') == award:
                    award_match = True
                    break
            if not award_match:
                continue
                
        # 年份過濾
        year_match = False
        if year != "所有年份":
            for a in rest.get('award', []):
                if str(a.get('year')) == year:
                    year_match = True
                    break
            if not year_match:
                continue
                
        filtered.append(rest)
        
    return filtered

# 建立輸出路徑函式
def build_output_path(city, district, award, year, page):
    path_parts = []
    
    # 動態建立路徑層級，跳過"所有..."選項
    if city != "所有城市":
        path_parts.append(city)
    if district != "所有行政區":
        path_parts.append(district)
    if award != "所有獎項":
        path_parts.append(award)
    if year != "所有年份":
        path_parts.append(str(year))
    
    path_parts.append(str(page))
    return os.path.join('../content', *path_parts)

# 生成Markdown內容函式
def generate_md_content(restaurants, today, city, district, award, year, page, count):
    title = '';
    if city != "所有城市":
        title += city
    if district != "所有行政區":
        title += district
    if year != "所有年份":
        title += year
        title += "年度"
    if award != "所有獎項":
        title += award
    title += "獲獎餐廳"
    
    # 基礎frontmatter
    md_content = f'''---
title: "{title} 第{page}頁"
description: "收錄{title}，從傳統小吃到精緻料理，帶您品嚐競賽認證的頂級美味。"
keywords:
  - 美食競賽
  - 台灣美食
  - 美食精選
datePublished: "2025-06-30"
dateModified: "{today}"
city: "{city}"
district: "{district}"
award: "{award}"
year: "{year}"
page: {page}
count: {count}

restaurants:
'''
    
    # 添加餐廳資料
    for rest in restaurants:
        replace_name = re.sub(r'[^\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ffa-zA-Z0-9\u00C0-\u017F\u0400-\u04FF\-_.]', '_', rest.get('name', ''))
        md_content += f'''  - name: "{rest.get('name', '')}"
    city: "{rest.get('city', '')}"
    district: "{rest.get('district', '')}"
    address: "{rest.get('address', '')}"
    phone: "{rest.get('phone', '')}"
    geo: "{rest.get('geo', '')}"
    link: "{rest.get('city', '')}/{rest.get('district', '')}/{replace_name}"
    googleMap: "{rest.get('googleMap', '')}"
    footinder: "{rest.get('footinder', '')}"
    award:
'''
        unique_awards = []
        seen = set()
        for award_info in rest.get('award', []):
            key = (award_info.get('name'), award_info.get('year'))
            if key not in seen:
                unique_awards.append(award_info)
                seen.add(key)
        for award_info in unique_awards:
            md_content += f'''    - name: "{award_info.get('name', '')}"
      year: "{award_info.get('year', '')}"\n'''
    
    md_content += '---'
    return md_content

def remove_date_modified(md_content):
    # 將 frontmatter 以 YAML 載入，移除 dateModified 再回存 string，方便比對
    sections = md_content.split('---')
    if len(sections) < 3:
        return md_content  # 格式非標準 Markdown frontmatter
    # sections[1] 是 frontmatter，sections[2]是正文
    frontmatter = yaml.safe_load(sections[1])
    if 'dateModified' in frontmatter:
        del frontmatter['dateModified']
    # 保留序，前後一致
    frontmatter_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    return f'---\n{frontmatter_str}---{sections[2]}'

# 執行主程式
generate_pages()
