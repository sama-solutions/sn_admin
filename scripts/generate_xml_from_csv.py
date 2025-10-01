#!/usr/bin/env python3
"""
Script de génération de fichiers XML Odoo depuis les CSV normalisés.
Génère les fichiers XML de PRODUCTION avec toutes les données.
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.dom import minidom
import html


def sanitize_xml_text(text):
    """Échapper les caractères spéciaux XML"""
    if not text:
        return ''
    return html.escape(str(text).strip())


def generate_external_id(record_type, code, parent_code=None):
    """Générer un external_id unique"""
    code_lower = code.lower().replace(' ', '_').replace('-', '_')
    if parent_code:
        parent_lower = parent_code.lower().replace(' ', '_').replace('-', '_')
        return f"{record_type}_{code_lower}_{parent_lower}"
    return f"{record_type}_{code_lower}"


def create_xml_record(record_id, model, fields_data):
    """Créer un élément XML record"""
    record = ET.Element('record', id=record_id, model=model)
    
    for field_name, field_value in fields_data.items():
        if field_value is not None and field_value != '':
            field = ET.SubElement(record, 'field', name=field_name)
            if field_name.endswith('_id') and not field_value.startswith('ref:'):
                # C'est une référence Many2one
                field.set('ref', field_value)
            else:
                field.text = sanitize_xml_text(field_value)
    
    return record


def generate_ministry_xml(input_dir, output_file):
    """Générer le fichier XML des ministères"""
    csv_file = os.path.join(input_dir, 'ministeres_normalized.csv')
    
    if not os.path.exists(csv_file):
        print(f"⚠️  Fichier {csv_file} introuvable. Ignoré.")
        return 0
    
    root = ET.Element('odoo')
    data = ET.SubElement(root, 'data', noupdate="0")
    
    count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('code'):
                continue
            
            record_id = generate_external_id('ministry', row['code'])
            
            fields = {
                'name': row.get('name', ''),
                'code': row.get('code', ''),
                'type': row.get('type', 'ministry'),
                'description': row.get('description', ''),
                'address': row.get('address', ''),
                'phone': row.get('phone', ''),
                'email': row.get('email', ''),
                'website': row.get('website', ''),
                'state': 'active',
                'active': 'True',
            }
            
            record = create_xml_record(record_id, 'sn.ministry', fields)
            data.append(record)
            count += 1
    
    # Écrire le fichier XML formaté
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"✓ {count} ministères générés dans {output_file}")
    return count


def generate_direction_xml(input_dir, output_file):
    """Générer le fichier XML des directions"""
    csv_file = os.path.join(input_dir, 'directions_normalized.csv')
    
    if not os.path.exists(csv_file):
        print(f"⚠️  Fichier {csv_file} introuvable. Ignoré.")
        return 0
    
    root = ET.Element('odoo')
    data = ET.SubElement(root, 'data', noupdate="0")
    
    count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('code') or not row.get('ministry_code'):
                continue
            
            record_id = generate_external_id('direction', row['code'], row['ministry_code'])
            ministry_ref = generate_external_id('ministry', row['ministry_code'])
            
            fields = {
                'name': row.get('name', ''),
                'code': row.get('code', ''),
                'type': row.get('type', 'generale'),
                'ministry_id': ministry_ref,
                'phone': row.get('phone', ''),
                'email': row.get('email', ''),
                'address': row.get('address', ''),
                'state': 'active',
                'active': 'True',
            }
            
            record = create_xml_record(record_id, 'sn.direction', fields)
            data.append(record)
            count += 1
    
    # Écrire le fichier XML formaté
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"✓ {count} directions générées dans {output_file}")
    return count


def generate_service_xml(input_dir, output_file):
    """Générer le fichier XML des services"""
    csv_file = os.path.join(input_dir, 'services_normalized.csv')
    
    if not os.path.exists(csv_file):
        print(f"⚠️  Fichier {csv_file} introuvable. Ignoré.")
        return 0
    
    root = ET.Element('odoo')
    data = ET.SubElement(root, 'data', noupdate="0")
    
    count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('code') or not row.get('direction_code') or not row.get('ministry_code'):
                continue
            
            record_id = generate_external_id('service', row['code'], row['direction_code'])
            direction_ref = generate_external_id('direction', row['direction_code'], row['ministry_code'])
            
            fields = {
                'name': row.get('name', ''),
                'code': row.get('code', ''),
                'type': row.get('type', 'service'),
                'direction_id': direction_ref,
                'phone': row.get('phone', ''),
                'email': row.get('email', ''),
                'state': 'active',
                'active': 'True',
            }
            
            record = create_xml_record(record_id, 'sn.service', fields)
            data.append(record)
            count += 1
    
    # Écrire le fichier XML formaté
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"✓ {count} services générés dans {output_file}")
    return count


def generate_agent_xml(input_dir, output_file):
    """Générer le fichier XML des agents"""
    csv_file = os.path.join(input_dir, 'agents_normalized.csv')
    
    if not os.path.exists(csv_file):
        print(f"⚠️  Fichier {csv_file} introuvable. Création d'un fichier vide.")
        # Créer un fichier XML vide
        root = ET.Element('odoo')
        ET.SubElement(root, 'data', noupdate="0")
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        return 0
    
    root = ET.Element('odoo')
    data = ET.SubElement(root, 'data', noupdate="0")
    
    count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('matricule') or not row.get('service_code'):
                continue
            
            record_id = generate_external_id('agent', row['matricule'])
            service_ref = generate_external_id('service', row['service_code'], row.get('direction_code', ''))
            
            fields = {
                'name': row.get('name', ''),
                'first_name': row.get('first_name', ''),
                'last_name': row.get('last_name', ''),
                'matricule': row.get('matricule', ''),
                'function': row.get('function', ''),
                'service_id': service_ref,
                'work_phone': row.get('work_phone', ''),
                'mobile_phone': row.get('mobile_phone', ''),
                'work_email': row.get('work_email', ''),
                'state': 'active',
                'active': 'True',
            }
            
            record = create_xml_record(record_id, 'sn.agent', fields)
            data.append(record)
            count += 1
    
    # Écrire le fichier XML formaté
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"✓ {count} agents générés dans {output_file}")
    return count


def validate_xml(xml_file):
    """Valider un fichier XML"""
    try:
        ET.parse(xml_file)
        print(f"✓ Validation XML réussie: {xml_file}")
        return True
    except ET.ParseError as e:
        print(f"✗ Erreur de validation XML dans {xml_file}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Générer les fichiers XML Odoo depuis les CSV normalisés'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/normalized/',
        help='Répertoire des CSV normalisés'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/',
        help='Répertoire de sortie des XML'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Générer tous les fichiers'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['ministry', 'direction', 'service', 'agent'],
        help='Générer un seul modèle'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Valider les XML générés'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbeux'
    )
    
    args = parser.parse_args()
    
    # Créer les répertoires si nécessaire
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Génération des fichiers XML Odoo depuis les CSV normalisés")
    print("=" * 70)
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print()
    
    total_count = 0
    
    if args.all or args.model == 'ministry':
        output_file = os.path.join(args.output, 'sn_ministry_data.xml')
        count = generate_ministry_xml(args.input, output_file)
        total_count += count
        if args.validate:
            validate_xml(output_file)
    
    if args.all or args.model == 'direction':
        output_file = os.path.join(args.output, 'sn_direction_data.xml')
        count = generate_direction_xml(args.input, output_file)
        total_count += count
        if args.validate:
            validate_xml(output_file)
    
    if args.all or args.model == 'service':
        output_file = os.path.join(args.output, 'sn_service_data.xml')
        count = generate_service_xml(args.input, output_file)
        total_count += count
        if args.validate:
            validate_xml(output_file)
    
    if args.all or args.model == 'agent':
        output_file = os.path.join(args.output, 'sn_agent_data.xml')
        count = generate_agent_xml(args.input, output_file)
        total_count += count
        if args.validate:
            validate_xml(output_file)
    
    print()
    print("=" * 70)
    print(f"✓ Génération terminée: {total_count} enregistrements au total")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
