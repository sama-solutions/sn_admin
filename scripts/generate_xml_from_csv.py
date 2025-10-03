#!/usr/bin/env python3
"""
Script pour générer les fichiers XML Odoo à partir des fichiers CSV
Usage: python3 scripts/generate_xml_from_csv.py
"""

import csv
import os
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def prettify_xml(elem):
    """Retourne une chaîne XML joliment formatée"""
    rough_string = tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ", encoding='utf-8').decode('utf-8')


def sanitize_id(text):
    """Nettoie un texte pour en faire un ID XML valide"""
    # Remplacer les caractères spéciaux
    replacements = {
        ' ': '_',
        "'": '',
        '"': '',
        ',': '',
        '.': '',
        '/': '_',
        '(': '',
        ')': '',
        'é': 'e',
        'è': 'e',
        'ê': 'e',
        'à': 'a',
        'â': 'a',
        'ô': 'o',
        'ù': 'u',
        'û': 'u',
        'ç': 'c',
        'É': 'E',
        'È': 'E',
        'Ê': 'E',
        'À': 'A',
        'Â': 'A',
        'Ô': 'O',
        'Ù': 'U',
        'Û': 'U',
        'Ç': 'C',
    }
    
    result = text.lower()
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Supprimer les caractères non alphanumériques (sauf _)
    result = ''.join(c if c.isalnum() or c == '_' else '' for c in result)
    
    # Supprimer les underscores multiples
    while '__' in result:
        result = result.replace('__', '_')
    
    return result.strip('_')


def generate_ministries_xml(csv_file, output_file):
    """Génère le fichier XML des ministères"""
    print(f"Génération de {output_file}...")
    
    root = Element('odoo')
    data = SubElement(root, 'data', noupdate='0')
    
    ministries = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Éviter les doublons
            if row['id'] in ministries:
                continue
            
            ministries[row['id']] = row
            
            record = SubElement(data, 'record', id=row['id'], model='sn.ministry')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Code
            code_field = SubElement(record, 'field', name='code')
            code_field.text = row['code'].strip()
            
            # Type
            type_field = SubElement(record, 'field', name='type')
            type_field.text = row['type'].strip()
            
            # État
            state_field = SubElement(record, 'field', name='state')
            state_field.text = 'active'
    
    # Écrire le fichier
    xml_string = prettify_xml(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✅ {len(ministries)} ministères générés")


def generate_categories_xml(csv_file, output_file):
    """Génère le fichier XML des catégories"""
    print(f"Génération de {output_file}...")
    
    root = Element('odoo')
    data = SubElement(root, 'data', noupdate='0')
    
    count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = SubElement(data, 'record', id=row['id'], model='sn.category')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Ministère (référence)
            ministry_field = SubElement(record, 'field', name='ministry_id', ref=row['ministry_id/id'].strip())
            
            # État
            state_field = SubElement(record, 'field', name='state')
            state_field.text = 'active'
            
            count += 1
    
    # Écrire le fichier
    xml_string = prettify_xml(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✅ {count} catégories générées")


def generate_directions_xml(csv_file, output_file):
    """Génère le fichier XML des directions"""
    print(f"Génération de {output_file}...")
    
    root = Element('odoo')
    data = SubElement(root, 'data', noupdate='0')
    
    count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = SubElement(data, 'record', id=row['id'], model='sn.direction')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Code (si présent)
            if row.get('code'):
                code_field = SubElement(record, 'field', name='code')
                code_field.text = row['code'].strip()
            
            # Type
            type_field = SubElement(record, 'field', name='type')
            type_field.text = row.get('type', 'generale').strip()
            
            # Ministère (référence)
            ministry_field = SubElement(record, 'field', name='ministry_id', ref=row['ministry_id/id'].strip())
            
            # Catégorie (référence si présente)
            if row.get('category_id/id'):
                category_field = SubElement(record, 'field', name='category_id', ref=row['category_id/id'].strip())
            
            # État
            state_field = SubElement(record, 'field', name='state')
            state_field.text = 'active'
            
            count += 1
    
    # Écrire le fichier
    xml_string = prettify_xml(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✅ {count} directions générées")


def generate_services_xml(csv_file, output_file, max_records=None):
    """Génère le fichier XML des services"""
    print(f"Génération de {output_file}...")
    
    root = Element('odoo')
    data = SubElement(root, 'data', noupdate='0')
    
    count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if max_records and count >= max_records:
                break
            
            record = SubElement(data, 'record', id=row['id'], model='sn.service')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Code (si présent)
            if row.get('code'):
                code_field = SubElement(record, 'field', name='code')
                code_field.text = row['code'].strip()
            
            # Type
            type_field = SubElement(record, 'field', name='type')
            type_field.text = row.get('type', 'service').strip()
            
            # Direction (référence)
            direction_field = SubElement(record, 'field', name='direction_id', ref=row['direction_id/id'].strip())
            
            # État
            state_field = SubElement(record, 'field', name='state')
            state_field.text = 'active'
            
            count += 1
    
    # Écrire le fichier
    xml_string = prettify_xml(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✅ {count} services générés")


def main():
    """Fonction principale"""
    print("=" * 60)
    print("Génération des fichiers XML à partir des CSV")
    print("=" * 60)
    
    # Chemins
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    
    # Vérifier que les fichiers CSV existent
    csv_files = {
        'ministries': data_dir / 'odoo_ministry.csv',
        'categories': data_dir / 'odoo_category.csv',
        'directions': data_dir / 'odoo_direction.csv',
        'services': data_dir / 'odoo_service.csv',
    }
    
    for name, path in csv_files.items():
        if not path.exists():
            print(f"❌ Fichier manquant : {path}")
            return
    
    print("\n📁 Tous les fichiers CSV trouvés\n")
    
    # Générer les XML
    try:
        # 1. Ministères
        generate_ministries_xml(
            csv_files['ministries'],
            data_dir / 'sn_ministry_data.xml'
        )
        
        # 2. Catégories
        generate_categories_xml(
            csv_files['categories'],
            data_dir / 'sn_category_data.xml'
        )
        
        # 3. Directions
        generate_directions_xml(
            csv_files['directions'],
            data_dir / 'sn_direction_data.xml'
        )
        
        # 4. Services (limiter à 1000 pour ne pas surcharger)
        generate_services_xml(
            csv_files['services'],
            data_dir / 'sn_service_data.xml',
            max_records=1000
        )
        
        print("\n" + "=" * 60)
        print("✅ Génération terminée avec succès !")
        print("=" * 60)
        print("\nFichiers générés :")
        print(f"  - {data_dir / 'sn_ministry_data.xml'}")
        print(f"  - {data_dir / 'sn_category_data.xml'}")
        print(f"  - {data_dir / 'sn_direction_data.xml'}")
        print(f"  - {data_dir / 'sn_service_data.xml'}")
        print("\nProchaines étapes :")
        print("  1. Vérifier les fichiers XML générés")
        print("  2. Ajouter sn_category_data.xml dans __manifest__.py")
        print("  3. Redémarrer Odoo et mettre à jour le module")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
