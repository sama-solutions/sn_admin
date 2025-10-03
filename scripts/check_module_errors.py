#!/usr/bin/env python3
"""
Script de vérification complète du module sn_admin
Identifie toutes les erreurs potentielles avant l'installation
"""

import os
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def check_python_syntax():
    """Vérifier la syntaxe Python de tous les fichiers"""
    print("=" * 60)
    print("1. VÉRIFICATION SYNTAXE PYTHON")
    print("=" * 60)
    
    errors = []
    base_dir = Path(__file__).parent.parent
    models_dir = base_dir / 'models'
    
    for py_file in models_dir.glob('*.py'):
        print(f"\n📄 Vérification: {py_file.name}")
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier les imports
            if 'from odoo import' not in content and py_file.name != '__init__.py':
                errors.append(f"❌ {py_file.name}: Manque 'from odoo import'")
            
            # Vérifier les @api.depends sans compute
            depends_matches = re.findall(r'@api\.depends\([^)]+\)', content)
            for match in depends_matches:
                # Chercher la fonction qui suit
                pattern = match.replace('(', r'\(').replace(')', r'\)') + r'\s+def\s+(\w+)'
                func_match = re.search(pattern, content)
                if func_match:
                    func_name = func_match.group(1)
                    # Vérifier que la fonction est référencée dans un compute
                    if f"compute='{func_name}'" not in content and f'compute="{func_name}"' not in content:
                        print(f"⚠️  Fonction {func_name} a @api.depends mais pas de champ compute correspondant")
            
            # Vérifier les champs related ET compute sur le même champ
            field_pattern = r"(\w+)\s*=\s*fields\.\w+\([^)]*related=['\"]([^'\"]+)['\"][^)]*\)"
            related_fields = re.findall(field_pattern, content)
            
            for field_name, related_path in related_fields:
                compute_pattern = f"{field_name}\\s*=\\s*fields\\.\\w+\\([^)]*compute="
                if re.search(compute_pattern, content):
                    errors.append(f"❌ {py_file.name}: Champ '{field_name}' a à la fois 'related' ET 'compute'")
            
            # Vérifier @api.depends('id')
            if "@api.depends('id')" in content or '@api.depends("id")' in content:
                errors.append(f"❌ {py_file.name}: Contient @api.depends('id') qui est interdit")
            
            # Vérifier les {{ ... }}
            if '{{ ... }}' in content:
                errors.append(f"❌ {py_file.name}: Contient '{{{{ ... }}}}' (template non résolu)")
            
            # Compiler le code Python
            compile(content, py_file.name, 'exec')
            print(f"✅ Syntaxe Python valide")
            
        except SyntaxError as e:
            errors.append(f"❌ {py_file.name}: Erreur de syntaxe ligne {e.lineno}: {e.msg}")
            print(f"❌ Erreur de syntaxe: {e}")
        except Exception as e:
            errors.append(f"❌ {py_file.name}: Erreur: {e}")
            print(f"❌ Erreur: {e}")
    
    return errors


def check_xml_syntax():
    """Vérifier la syntaxe XML de tous les fichiers"""
    print("\n" + "=" * 60)
    print("2. VÉRIFICATION SYNTAXE XML")
    print("=" * 60)
    
    errors = []
    base_dir = Path(__file__).parent.parent
    
    xml_dirs = [
        base_dir / 'views',
        base_dir / 'security',
        base_dir / 'reports',
        base_dir / 'data',
    ]
    
    for xml_dir in xml_dirs:
        if not xml_dir.exists():
            continue
        
        for xml_file in xml_dir.glob('*.xml'):
            print(f"\n📄 Vérification: {xml_file.relative_to(base_dir)}")
            
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Vérifier les XPath
                for xpath_elem in root.findall('.//xpath'):
                    expr = xpath_elem.get('expr', '')
                    if not expr:
                        errors.append(f"❌ {xml_file.name}: XPath sans expression")
                    
                    # Vérifier les XPath problématiques
                    if "[@name='department_details']" in expr:
                        errors.append(f"❌ {xml_file.name}: XPath utilise 'department_details' qui n'existe pas")
                
                # Vérifier les attrs (obsolète Odoo 18)
                for elem in root.iter():
                    if 'attrs' in elem.attrib:
                        errors.append(f"❌ {xml_file.name}: Utilise 'attrs' (obsolète Odoo 18)")
                        break
                
                # Vérifier les <tree> (obsolète Odoo 18)
                for tree_elem in root.findall('.//tree'):
                    errors.append(f"❌ {xml_file.name}: Utilise <tree> au lieu de <list>")
                    break
                
                # Vérifier les accès via relation (ex: field.subfield)
                for field_elem in root.findall('.//field'):
                    field_name = field_elem.get('name', '')
                    if '.' in field_name and not field_name.startswith('parent_'):
                        print(f"⚠️  Accès via relation: {field_name} (peut ne pas fonctionner dans vue héritée)")
                
                print(f"✅ XML valide")
                
            except ET.ParseError as e:
                errors.append(f"❌ {xml_file.name}: Erreur XML: {e}")
                print(f"❌ Erreur XML: {e}")
            except Exception as e:
                errors.append(f"❌ {xml_file.name}: Erreur: {e}")
                print(f"❌ Erreur: {e}")
    
    return errors


def check_manifest():
    """Vérifier le fichier __manifest__.py"""
    print("\n" + "=" * 60)
    print("3. VÉRIFICATION __manifest__.py")
    print("=" * 60)
    
    errors = []
    base_dir = Path(__file__).parent.parent
    manifest_file = base_dir / '__manifest__.py'
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compiler le manifest
        manifest_dict = eval(content)
        
        # Vérifier les dépendances
        depends = manifest_dict.get('depends', [])
        print(f"\n📦 Dépendances: {', '.join(depends)}")
        
        enterprise_modules = ['account_accountant', 'social_media', 'studio', 'planning']
        for dep in depends:
            if dep in enterprise_modules:
                errors.append(f"❌ Dépendance Enterprise détectée: {dep}")
        
        # Vérifier que tous les fichiers data existent
        data_files = manifest_dict.get('data', [])
        print(f"\n📄 Fichiers data: {len(data_files)}")
        
        for data_file in data_files:
            file_path = base_dir / data_file
            if not file_path.exists():
                errors.append(f"❌ Fichier manquant: {data_file}")
                print(f"❌ Manquant: {data_file}")
            else:
                print(f"✅ {data_file}")
        
        print(f"\n✅ Manifest valide")
        
    except Exception as e:
        errors.append(f"❌ __manifest__.py: Erreur: {e}")
        print(f"❌ Erreur: {e}")
    
    return errors


def check_security():
    """Vérifier les fichiers de sécurité"""
    print("\n" + "=" * 60)
    print("4. VÉRIFICATION SÉCURITÉ")
    print("=" * 60)
    
    errors = []
    base_dir = Path(__file__).parent.parent
    security_dir = base_dir / 'security'
    
    # Vérifier ir.model.access.csv
    access_file = security_dir / 'ir.model.access.csv'
    if access_file.exists():
        print(f"\n📄 Vérification: ir.model.access.csv")
        
        with open(access_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        models = set()
        for i, line in enumerate(lines[1:], start=2):  # Skip header
            if line.strip():
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    model_ref = parts[2]  # model_id:id
                    models.add(model_ref)
        
        print(f"✅ {len(models)} modèles avec droits d'accès")
        
        # Vérifier que les modèles principaux sont couverts
        required_models = [
            'model_sn_ministry',
            'model_sn_category',
            'model_sn_direction',
            'model_sn_service',
            'model_sn_agent',
        ]
        
        for model in required_models:
            if model not in models:
                errors.append(f"❌ Modèle {model} n'a pas de droits d'accès")
    
    return errors


def main():
    """Fonction principale"""
    print("\n" + "🔍" * 30)
    print("VÉRIFICATION COMPLÈTE DU MODULE sn_admin")
    print("🔍" * 30 + "\n")
    
    all_errors = []
    
    # 1. Python
    all_errors.extend(check_python_syntax())
    
    # 2. XML
    all_errors.extend(check_xml_syntax())
    
    # 3. Manifest
    all_errors.extend(check_manifest())
    
    # 4. Sécurité
    all_errors.extend(check_security())
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    
    if all_errors:
        print(f"\n❌ {len(all_errors)} ERREUR(S) DÉTECTÉE(S):\n")
        for error in all_errors:
            print(f"  {error}")
        print("\n⚠️  Le module NE PEUT PAS être installé en l'état !")
        return 1
    else:
        print("\n✅ AUCUNE ERREUR DÉTECTÉE")
        print("✅ Le module peut être installé")
        return 0


if __name__ == '__main__':
    sys.exit(main())
