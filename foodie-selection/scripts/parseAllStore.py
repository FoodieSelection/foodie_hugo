import json
import glob
import os
import re
import yaml
from collections import defaultdict
from datetime import datetime

def generate_md_content(restaurant, today):
    """
    根據餐廳資料生成 Markdown Front Matter，
    並將同一獎項（name, year）聚合成 entries 巢狀結構。
    """
    # 基礎 front matter
    md_lines = [
        '---',
        f'title: "{restaurant.get("name", "")}"',
        f'description: "{restaurant.get("name", "")}"',
        'layout: shop',
        'keywords:',
        '  - 美食競賽',
        '  - 台灣美食',
        '  - 美食精選',
        'datePublished: "2025-06-30"',
        f'dateModified: "{today}"',
        f'city: "{restaurant.get("city", "")}"',
        f'district: "{restaurant.get("district", "")}"',
        f'address: "{restaurant.get("address", "")}"',
        f'phone: "{restaurant.get("phone", "")}"',
        f'geo: "{restaurant.get("geo", "")}"',
        f'googleMap: "{restaurant.get("googleMap", "")}"',
        f'footinder: "{restaurant.get("footinder", "")}"',
        f'official: "{restaurant.get("official", "")}"',
        'award:'
    ]

    # 將 award 以 (name, year) 聚合
    grouped = defaultdict(list)
    for a in restaurant.get('award', []):
        key = (a.get('name', ''), a.get('year', ''))
        grouped[key].append(a)

    # 輸出每組聚合後的獎項
    for (name, year), items in grouped.items():
        md_lines.append(f'  - name: "{name}"')
        md_lines.append(f'    year: "{year}"')
        md_lines.append('    entries:')
        for a in items:
            if name == '500盤':
                md_lines.append('      - dishes:')
                for d in a.get('dishes', []):
                    md_lines.append(f'          - "{d}"')
            elif name == '台北國際牛肉麵節':
                md_lines.append('      - group: "{}"'.format(a.get('group', '')))
                md_lines.append('        cookingStyle: "{}"'.format(a.get('cookingStyle', '')))
                md_lines.append('        rank: "{}"'.format(a.get('rank', '')))
            elif name == '夜市王':
                md_lines.append('      - nightMarket: "{}"'.format(a.get('nightMarket', '')))
                md_lines.append('        foodType: "{}"'.format(a.get('foodType', '')))
                md_lines.append('        rank: "{}"'.format(a.get('rank', '')))
            else:
                # 若有其他獎項結構，可直接序列化欄位
                md_lines.append('      - ' + json.dumps(a, ensure_ascii=False))
        # 空行分隔
        md_lines.append('')

    md_lines.append('---')
    return '\n'.join(md_lines)

def generate_pages():
    """
    讀取 ../data/**/*.json 資料，
    為每筆餐廳生成對應的 _index.md。
    """
    json_files = glob.glob('../data/**/*.json', recursive=True)
    all_restaurants = []
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_restaurants.extend(data)

    today = datetime.now().strftime("%Y-%m-%d")
    for restaurant in all_restaurants:
        md_content = generate_md_content(restaurant, today)
        # 清理檔名中的非法字元
        # safe_name = re.sub(r'[<>:"/\\|?* ()#%{},;@&=+]', '_', restaurant.get('name', ''))
        # safe_name = safe_name.replace('³', '3')
        safe_name = re.sub(r'[^\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ffa-zA-Z0-9\u00C0-\u017F\u0400-\u04FF\-_.]', '_', restaurant.get('name', ''))
        dir_path = os.path.join(
            "../content",
            restaurant.get('city', ''),
            restaurant.get('district', ''),
            safe_name
        )
        os.makedirs(dir_path, exist_ok=True)
        
        # 比較檔案內容（忽略 dateModified）
        file_path = os.path.join(dir_path, '_index.md')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            if (remove_date_modified(old_content).strip() ==
                    remove_date_modified(md_content).strip()):
                # 內容未實質變動，跳過寫檔
                continue
        
        with open(os.path.join(dir_path, '_index.md'), 'w', encoding='utf-8') as f:
            f.write(md_content)

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

if __name__ == "__main__":
    generate_pages()
