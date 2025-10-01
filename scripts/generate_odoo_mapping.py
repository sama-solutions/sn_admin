#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de génération du mapping Odoo
Analyse les données normalisées et génère le mapping vers les modèles Odoo
"""

import argparse
import logging
import sys
import json
from pathlib import Path
import pandas as pd
from collections import defaultdict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mapping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OdooMappingGenerator:
    """Générateur de mapping Odoo"""
    
    def __init__(self, input_dir, output_file):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        
        # Mapping des modèles Odoo
        self.models = {
            'sn.ministry': {
                'description': 'Ministères et institutions',
                'inherits': 'government.ministry',
                'source_columns': [],
                'odoo_fields': {},
                'required': ['name', 'code'],
                'relations': {}
            },
            'sn.direction': {
                'description': 'Directions générales et régionales',
                'source_columns': [],
                'odoo_fields': {},
                'required': ['name', 'ministry_id'],
                'relations': {
                    'ministry_id': {
                        'type': 'many2one',
                        'comodel': 'sn.ministry',
                        'required': True
                    }
                }
            },
            'sn.service': {
                'description': 'Services, bureaux, cellules',
                'source_columns': [],
                'odoo_fields': {},
                'required': ['name', 'direction_id'],
                'relations': {
                    'direction_id': {
                        'type': 'many2one',
                        'comodel': 'sn.direction',
                        'required': True
                    }
                }
            },
            'sn.agent': {
                'description': 'Agents publics',
                'source_columns': [],
                'odoo_fields': {},
                'required': ['name', 'function', 'service_id'],
                'relations': {
                    'service_id': {
                        'type': 'many2one',
                        'comodel': 'sn.service',
                        'required': True
                    },
                    'employee_id': {
                        'type': 'many2one',
                        'comodel': 'hr.employee',
                        'required': False
                    }
                }
            }
        }
        
        # Mapping des colonnes vers champs Odoo
        self.field_mappings = {
            # Ministères
            'nom_ministere': ('name', 'char', 'sn.ministry'),
            'nom_du_ministere': ('name', 'char', 'sn.ministry'),
            'code_ministere': ('code', 'char', 'sn.ministry'),
            'code': ('code', 'char', 'sn.ministry'),
            'type_ministere': ('type', 'selection', 'sn.ministry'),
            'type': ('type', 'selection', 'sn.ministry'),
            
            # Directions
            'nom_direction': ('name', 'char', 'sn.direction'),
            'code_direction': ('code', 'char', 'sn.direction'),
            'type_direction': ('type', 'selection', 'sn.direction'),
            
            # Services
            'nom_service': ('name', 'char', 'sn.service'),
            'code_service': ('code', 'char', 'sn.service'),
            'type_service': ('type', 'selection', 'sn.service'),
            
            # Agents
            'nom': ('name', 'char', 'sn.agent'),
            'prenom': ('first_name', 'char', 'sn.agent'),
            'nom_complet': ('name', 'char', 'sn.agent'),
            'fonction': ('function', 'char', 'sn.agent'),
            'poste': ('function', 'char', 'sn.agent'),
            'matricule': ('employee_id', 'char', 'sn.agent'),
            
            # Relations hiérarchiques (Many2one)
            'ministere': ('ministry_id', 'many2one', 'sn.direction'),
            'direction': ('direction_id', 'many2one', 'sn.service'),
            'service': ('service_id', 'many2one', 'sn.agent'),
            'interlocuteur': ('manager_id', 'many2one', 'all'),
            
            # Champs communs
            'adresse': ('address', 'text', 'all'),
            'telephone': ('phone', 'char', 'all'),
            'telephone_bureau': ('work_phone', 'char', 'all'),
            'telephone_mobile': ('mobile_phone', 'char', 'all'),
            'email': ('email', 'char', 'all'),
            'email_professionnel': ('work_email', 'char', 'all'),
            'site_web': ('website', 'char', 'all'),
            'description': ('description', 'text', 'all'),
            'responsable': ('manager_id', 'many2one', 'all'),
        }
        
        logger.info(f"Initialisation du générateur de mapping")
        logger.info(f"Répertoire source: {self.input_dir}")
        logger.info(f"Fichier de sortie: {self.output_file}")
    
    def analyze_file(self, csv_file):
        """Analyse un fichier CSV et détecte le modèle correspondant"""
        logger.info(f"\nAnalyse de: {csv_file.name}")
        
        try:
            df = pd.read_csv(csv_file, dtype=str, nrows=10)  # Lire seulement 10 lignes pour analyse
            columns = df.columns.tolist()
            
            logger.info(f"  - Colonnes détectées: {', '.join(columns)}")
            
            # Détecter le type de données
            detected_model = None
            score = defaultdict(int)
            
            for col in columns:
                col_lower = col.lower()
                if col_lower in self.field_mappings:
                    field_name, field_type, model = self.field_mappings[col_lower]
                    if model != 'all':
                        score[model] += 1
            
            # Modèle avec le score le plus élevé
            if score:
                detected_model = max(score, key=score.get)
                logger.info(f"  - Modèle détecté: {detected_model} (score: {score[detected_model]})")
            else:
                logger.warning(f"  - Aucun modèle détecté, analyse manuelle requise")
            
            # Mapper les colonnes
            mapped_fields = {}
            for col in columns:
                col_lower = col.lower()
                if col_lower in self.field_mappings:
                    field_name, field_type, model = self.field_mappings[col_lower]
                    if model == 'all' or model == detected_model:
                        mapped_fields[col] = {
                            'odoo_field': field_name,
                            'type': field_type
                        }
            
            return {
                'file': csv_file.name,
                'detected_model': detected_model,
                'columns': columns,
                'mapped_fields': mapped_fields,
                'unmapped_columns': [c for c in columns if c not in mapped_fields]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {csv_file.name}: {e}")
            return None
    
    def generate_mapping(self):
        """Génère le fichier de mapping complet"""
        csv_files = list(self.input_dir.glob('*_normalized.csv'))
        
        if not csv_files:
            logger.warning(f"Aucun fichier CSV normalisé trouvé dans {self.input_dir}")
            return None
        
        logger.info(f"Fichiers CSV trouvés: {len(csv_files)}")
        
        # Analyser tous les fichiers
        analyses = []
        for csv_file in csv_files:
            analysis = self.analyze_file(csv_file)
            if analysis:
                analyses.append(analysis)
        
        # Construire le mapping final
        mapping = {
            'metadata': {
                'version': '1.0',
                'odoo_version': '18.0',
                'generated_from': str(self.input_dir),
                'files_analyzed': len(analyses)
            },
            'models': {}
        }
        
        # Grouper par modèle
        for analysis in analyses:
            model = analysis['detected_model']
            if model and model in self.models:
                if model not in mapping['models']:
                    mapping['models'][model] = {
                        'description': self.models[model]['description'],
                        'source_files': [],
                        'fields': {},
                        'required_fields': self.models[model]['required'],
                        'relations': self.models[model].get('relations', {})
                    }
                    if 'inherits' in self.models[model]:
                        mapping['models'][model]['inherits'] = self.models[model]['inherits']
                
                mapping['models'][model]['source_files'].append(analysis['file'])
                
                # Ajouter les champs mappés
                for source_col, field_info in analysis['mapped_fields'].items():
                    odoo_field = field_info['odoo_field']
                    if odoo_field not in mapping['models'][model]['fields']:
                        mapping['models'][model]['fields'][odoo_field] = {
                            'type': field_info['type'],
                            'source_columns': [source_col],
                            'required': odoo_field in self.models[model]['required']
                        }
                    else:
                        # Ajouter la colonne source si pas déjà présente
                        if source_col not in mapping['models'][model]['fields'][odoo_field]['source_columns']:
                            mapping['models'][model]['fields'][odoo_field]['source_columns'].append(source_col)
        
        # Sauvegarder le mapping
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\nMapping généré: {self.output_file}")
        logger.info(f"Modèles détectés: {', '.join(mapping['models'].keys())}")
        
        return mapping
    
    def generate_analysis_report(self, mapping):
        """Génère un rapport d'analyse détaillé"""
        report_file = self.output_file.parent / 'mapping_analysis.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== ANALYSE DU MAPPING ODOO ===\n\n")
            
            f.write(f"Version Odoo: {mapping['metadata']['odoo_version']}\n")
            f.write(f"Fichiers analysés: {mapping['metadata']['files_analyzed']}\n")
            f.write(f"Modèles détectés: {len(mapping['models'])}\n\n")
            
            for model_name, model_info in mapping['models'].items():
                f.write(f"\n## Modèle: {model_name}\n")
                f.write(f"Description: {model_info['description']}\n")
                
                if 'inherits' in model_info:
                    f.write(f"Hérite de: {model_info['inherits']}\n")
                
                f.write(f"Fichiers source: {', '.join(model_info['source_files'])}\n")
                f.write(f"Champs mappés: {len(model_info['fields'])}\n")
                f.write(f"Champs obligatoires: {', '.join(model_info['required_fields'])}\n\n")
                
                f.write("### Champs:\n")
                for field_name, field_info in model_info['fields'].items():
                    required = "✓" if field_info['required'] else " "
                    f.write(f"  [{required}] {field_name} ({field_info['type']})\n")
                    f.write(f"      Source: {', '.join(field_info['source_columns'])}\n")
                
                if model_info['relations']:
                    f.write("\n### Relations:\n")
                    for rel_name, rel_info in model_info['relations'].items():
                        required = "obligatoire" if rel_info['required'] else "optionnel"
                        f.write(f"  - {rel_name} ({rel_info['type']}) → {rel_info['comodel']} ({required})\n")
        
        logger.info(f"Rapport d'analyse généré: {report_file}")
        return report_file


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Génération du mapping Odoo'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Répertoire des fichiers normalisés'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Fichier JSON de sortie'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Générer un rapport d\'analyse détaillé'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbeux'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        generator = OdooMappingGenerator(
            input_dir=args.input,
            output_file=args.output
        )
        
        # Générer le mapping
        mapping = generator.generate_mapping()
        
        if not mapping:
            logger.error("Échec de la génération du mapping")
            return 1
        
        # Générer le rapport d'analyse
        if args.analyze:
            generator.generate_analysis_report(mapping)
        
        logger.info("\n✓ Génération du mapping terminée avec succès")
        return 0
        
    except Exception as e:
        logger.error(f"\n✗ Erreur fatale: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
