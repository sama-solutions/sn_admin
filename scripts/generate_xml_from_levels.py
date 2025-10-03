#!/usr/bin/env python3
"""
Script pour générer les fichiers XML Odoo à partir des fichiers orgadmin_levels
Usage: python3 scripts/generate_xml_from_levels.py
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


def sanitize_code(name):
    """Génère un code à partir du nom"""
    # Prendre les premières lettres des mots
    words = name.upper().split()
    if len(words) <= 3:
        code = ''.join(word[:3] for word in words)
    else:
        code = ''.join(word[0] for word in words if word[0].isalpha())
    
    # Limiter à 10 caractères
    return code[:10]


def convert_id(old_id):
    """Convertit L1_xxx en sn_min_xxx"""
    if old_id.startswith('L1_'):
        return 'sn_min_' + old_id[3:]
    elif old_id.startswith('L2_'):
        return 'sn_cat_' + old_id[3:]
    elif old_id.startswith('L3_'):
        return 'sn_dir_' + old_id[3:]
    elif old_id.startswith('L4_'):
        return 'sn_srv_' + old_id[3:]
    return old_id


def generate_level1_xml(csv_file, output_file):
    """Génère le fichier XML des ministères (Level 1)"""
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
            
            record_id = convert_id(row['id'])
            record = SubElement(data, 'record', id=record_id, model='sn.ministry')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Code (généré)
            code_field = SubElement(record, 'field', name='code')
            code_field.text = sanitize_code(row['name'])
            
            # Type
            type_field = SubElement(record, 'field', name='type')
            if 'PRESIDENCE' in row['name'].upper():
                type_field.text = 'presidency'
            elif 'PRIMATURE' in row['name'].upper():
                type_field.text = 'primature'
            else:
                type_field.text = 'ministry'
            
            # État
            state_field = SubElement(record, 'field', name='state')
            state_field.text = 'active'
    
    # Écrire le fichier
    xml_string = prettify_xml(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✅ {len(ministries)} ministères générés")
    return ministries


def generate_level2_xml(csv_file, output_file, ministries):
    """Génère le fichier XML des catégories (Level 2)"""
    print(f"Génération de {output_file}...")
    
    root = Element('odoo')
    data = SubElement(root, 'data', noupdate='0')
    
    count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Vérifier que le ministère parent existe
            if row['parent_level1'] not in ministries:
                print(f"⚠️  Ministère parent non trouvé : {row['parent_level1']}")
                continue
            
            record_id = convert_id(row['id'])
            record = SubElement(data, 'record', id=record_id, model='sn.category')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Code (généré)
            code_field = SubElement(record, 'field', name='code')
            code_field.text = sanitize_code(row['name'])
            
            # Ministère (référence)
            ministry_ref = convert_id(row['parent_level1'])
            ministry_field = SubElement(record, 'field', name='ministry_id', ref=ministry_ref)
            
            # État
            state_field = SubElement(record, 'field', name='state')
            state_field.text = 'active'
            
            count += 1
    
    # Écrire le fichier
    xml_string = prettify_xml(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✅ {count} catégories générées")


def generate_level3_xml(csv_file, output_file):
    """Génère le fichier XML des directions (Level 3)"""
    print(f"Génération de {output_file}...")
    
    root = Element('odoo')
    data = SubElement(root, 'data', noupdate='0')
    
    count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record_id = convert_id(row['id'])
            record = SubElement(data, 'record', id=record_id, model='sn.direction')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Code (généré)
            code_field = SubElement(record, 'field', name='code')
            code_field.text = sanitize_code(row['name'])
            
            # Type
            type_field = SubElement(record, 'field', name='type')
            if 'GENERALE' in row['name'].upper() or 'GENERAL' in row['name'].upper():
                type_field.text = 'generale'
            elif 'REGIONALE' in row['name'].upper():
                type_field.text = 'regionale'
            else:
                type_field.text = 'departementale'
            
            # Ministère (référence)
            ministry_ref = convert_id(row['parent_level1'])
            ministry_field = SubElement(record, 'field', name='ministry_id', ref=ministry_ref)
            
            # Catégorie (référence si présente)
            if row.get('parent_level2') and row['parent_level2'].strip():
                category_ref = convert_id(row['parent_level2'])
                category_field = SubElement(record, 'field', name='category_id', ref=category_ref)
            
            # État
            state_field = SubElement(record, 'field', name='state')
            state_field.text = 'active'
            
            count += 1
    
    # Écrire le fichier
    xml_string = prettify_xml(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✅ {count} directions générées")


def generate_level4_xml(csv_file, output_file, max_records=1000):
    """Génère le fichier XML des services (Level 4)"""
    print(f"Génération de {output_file}...")
    
    root = Element('odoo')
    data = SubElement(root, 'data', noupdate='0')
    
    count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if max_records and count >= max_records:
                break
            
            record_id = convert_id(row['id'])
            record = SubElement(data, 'record', id=record_id, model='sn.service')
            
            # Nom
            name_field = SubElement(record, 'field', name='name')
            name_field.text = row['name'].strip()
            
            # Code (généré)
            code_field = SubElement(record, 'field', name='code')
            code_field.text = sanitize_code(row['name'])
            
            # Type
            type_field = SubElement(record, 'field', name='type')
            name_upper = row['name'].upper()
            if 'SERVICE' in name_upper:
                type_field.text = 'service'
            elif 'BUREAU' in name_upper:
                type_field.text = 'bureau'
            elif 'CELLULE' in name_upper:
                type_field.text = 'cellule'
            elif 'DIVISION' in name_upper:
                type_field.text = 'division'
            else:
                type_field.text = 'service'
            
            # Direction (référence)
            direction_ref = convert_id(row['parent_level3'])
            direction_field = SubElement(record, 'field', name='direction_id', ref=direction_ref)
            
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
    print("Génération des fichiers XML à partir de orgadmin_levels")
    print("=" * 60)
    
    # Chemins
    base_dir = Path(__file__).parent.parent
    levels_dir = base_dir / 'orgadmin_levels'
    data_dir = base_dir / 'data'
    
    # Vérifier que les fichiers CSV existent
    csv_files = {
        'level1': levels_dir / 'orgadmin_level1.csv',
        'level2': levels_dir / 'orgadmin_level2.csv',
        'level3': levels_dir / 'orgadmin_level3.csv',
        'level4': levels_dir / 'orgadmin_level4.csv',
    }
    
    for name, path in csv_files.items():
        if not path.exists():
            print(f"❌ Fichier manquant : {path}")
            return
    
    print("\n📁 Tous les fichiers CSV trouvés\n")
    
    # Générer les XML
    try:
        # 1. Ministères (Level 1)
        ministries = generate_level1_xml(
            csv_files['level1'],
            data_dir / 'sn_ministry_data.xml'
        )
        
        # 2. Catégories (Level 2)
        generate_level2_xml(
            csv_files['level2'],
            data_dir / 'sn_category_data.xml',
            ministries
        )
        
        # 3. Directions (Level 3)
        generate_level3_xml(
            csv_files['level3'],
            data_dir / 'sn_direction_data.xml'
        )
        
        # 4. Services (Level 4) - Limiter à 1000
        generate_level4_xml(
            csv_files['level4'],
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
        print("  2. Redémarrer Odoo et mettre à jour le module")
        print("  3. Les données seront automatiquement importées")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
