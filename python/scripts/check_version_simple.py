#!/usr/bin/env python3
"""
Simple script to check version detection in .csproj file
"""
import xml.etree.ElementTree as ET

def check_version(csproj_path):
    """Check version in .csproj file."""
    print(f"Проверка файла: {csproj_path}")
    
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()
        
        print(f"✅ XML файл успешно распарсен")
        print(f"Корневой элемент: {root.tag}")
        
        # Try to find ApplicationDisplayVersion
        found = False
        for prop_group in root.findall('.//PropertyGroup'):
            display_version_elem = prop_group.find('ApplicationDisplayVersion')
            if display_version_elem is not None:
                print(f"\n✅ Найден элемент ApplicationDisplayVersion")
                print(f"   Значение: '{display_version_elem.text}'")
                if display_version_elem.text:
                    stripped = display_version_elem.text.strip()
                    print(f"   После strip(): '{stripped}'")
                    found = True
                else:
                    print(f"   ⚠️  Элемент пустой (text is None)")
        
        if not found:
            print(f"\n❌ Элемент ApplicationDisplayVersion не найден в файле")
            print(f"\nСписок всех PropertyGroup элементов:")
            for i, prop_group in enumerate(root.findall('.//PropertyGroup')):
                print(f"\n  PropertyGroup {i+1}:")
                for child in prop_group:
                    text = child.text if child.text else "(пусто)"
                    if len(text) > 50:
                        text = text[:50] + "..."
                    print(f"    - {child.tag}: {text}")
                    
    except Exception as e:
        print(f"❌ Ошибка при парсинге XML: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("Проверка версии в TechnouprApp.Client на ветке main")
    print("=" * 80)
    check_version("/home/olinyavod/projects/easybuild_bot/repos/TechnouprApp.Client/TechnouprApp.Client/TechnouprApp.Client.csproj")

