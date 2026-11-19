import os
import json

sfx_root = r'd:\video_youtube\sfx'
catalog = {
    'total_files': 0,
    'description': 'Kho SFX chất lượng cao cho video editing, hoạt hình 2D và HyperFrames',
    'categories': {}
}

total = 0
for cat in sorted(os.listdir(sfx_root)):
    cat_path = os.path.join(sfx_root, cat)
    if not os.path.isdir(cat_path):
        continue
    catalog['categories'][cat] = {
        'count': 0,
        'subcategories': {},
        'files': []
    }
    for root, dirs, files in os.walk(cat_path):
        rel_sub = os.path.relpath(root, cat_path)
        sub_name = '' if rel_sub == '.' else rel_sub.replace('\\', '/')
        for f in sorted(files):
            if f.lower().endswith(('.wav', '.mp3', '.ogg')):
                total += 1
                rel_path = os.path.relpath(os.path.join(root, f), sfx_root).replace('\\', '/')
                catalog['categories'][cat]['count'] += 1
                item = {
                    'name': f,
                    'path': rel_path,
                    'format': os.path.splitext(f)[1].replace('.', '').upper()
                }
                if sub_name:
                    if sub_name not in catalog['categories'][cat]['subcategories']:
                        catalog['categories'][cat]['subcategories'][sub_name] = []
                    catalog['categories'][cat]['subcategories'][sub_name].append(item)
                else:
                    catalog['categories'][cat]['files'].append(item)

catalog['total_files'] = total
with open(os.path.join(sfx_root, 'catalog.json'), 'w', encoding='utf-8') as fp:
    json.dump(catalog, fp, indent=2, ensure_ascii=False)

print(f"Catalog updated: {total} files across {len(catalog['categories'])} categories.")
