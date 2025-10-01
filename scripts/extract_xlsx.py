#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script d'extraction du fichier snadmin.xlsx
Extrait les feuilles Excel en fichiers CSV ou JSON
"""

import argparse
import logging
import sys
from pathlib import Path
import pandas as pd
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ExcelExtractor:
    """Extracteur de fichiers Excel vers CSV/JSON"""
    
    def __init__(self, excel_path, output_dir, output_format='csv', encoding='utf-8'):
        self.excel_path = Path(excel_path)
        self.output_dir = Path(output_dir)
        self.output_format = output_format.lower()
        self.encoding = encoding
        
        # Vérifier que le fichier existe
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Fichier Excel introuvable: {self.excel_path}")
        
        # Créer le répertoire de sortie
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialisation de l'extracteur")
        logger.info(f"Fichier source: {self.excel_path}")
        logger.info(f"Répertoire de sortie: {self.output_dir}")
        logger.info(f"Format: {self.output_format}")
    
    def list_sheets(self):
        """Liste toutes les feuilles du classeur"""
        try:
            excel_file = pd.ExcelFile(self.excel_path, engine='openpyxl')
            sheets = excel_file.sheet_names
            logger.info(f"Feuilles disponibles ({len(sheets)}): {', '.join(sheets)}")
            return sheets
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier: {e}")
            raise
    
    def extract_sheet(self, sheet_name):
        """Extrait une feuille spécifique"""
        try:
            logger.info(f"Extraction de la feuille: {sheet_name}")
            
            # Lire la feuille (dtype=str pour préserver les zéros initiaux)
            df = pd.read_excel(
                self.excel_path,
                sheet_name=sheet_name,
                engine='openpyxl',
                dtype=str
            )
            
            # Remplacer les NaN par des chaînes vides
            df = df.fillna('')
            
            logger.info(f"  - {len(df)} lignes, {len(df.columns)} colonnes")
            logger.info(f"  - Colonnes: {', '.join(df.columns.tolist())}")
            
            # Générer le nom de fichier
            safe_name = self._sanitize_filename(sheet_name)
            
            if self.output_format == 'csv':
                output_file = self.output_dir / f"{safe_name}.csv"
                df.to_csv(output_file, index=False, encoding=self.encoding)
            elif self.output_format == 'json':
                output_file = self.output_dir / f"{safe_name}.json"
                df.to_json(
                    output_file,
                    orient='records',
                    force_ascii=False,
                    indent=2
                )
            else:
                raise ValueError(f"Format non supporté: {self.output_format}")
            
            logger.info(f"  - Fichier créé: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de '{sheet_name}': {e}")
            raise
    
    def extract_all(self):
        """Extrait toutes les feuilles"""
        sheets = self.list_sheets()
        results = []
        
        logger.info(f"Début de l'extraction de {len(sheets)} feuille(s)")
        
        for i, sheet in enumerate(sheets, 1):
            logger.info(f"[{i}/{len(sheets)}] Traitement de '{sheet}'")
            try:
                output_file = self.extract_sheet(sheet)
                results.append({
                    'sheet': sheet,
                    'file': str(output_file),
                    'status': 'success'
                })
            except Exception as e:
                logger.error(f"Échec de l'extraction de '{sheet}': {e}")
                results.append({
                    'sheet': sheet,
                    'file': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Résumé
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"\n=== RÉSUMÉ ===")
        logger.info(f"Feuilles traitées: {len(sheets)}")
        logger.info(f"Succès: {success_count}")
        logger.info(f"Échecs: {len(sheets) - success_count}")
        
        return results
    
    def _sanitize_filename(self, name):
        """Nettoie un nom de fichier"""
        # Remplacer les caractères interdits
        safe = name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        safe = ''.join(c for c in safe if c.isalnum() or c in ('_', '-'))
        return safe.lower()


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Extraction du fichier snadmin.xlsx en CSV/JSON'
    )
    
    parser.add_argument(
        '--sheet',
        type=str,
        help='Nom de la feuille à extraire (défaut: toutes)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Extraire toutes les feuilles'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'json'],
        default='csv',
        help='Format de sortie (défaut: csv)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='../data/extracted/',
        help='Répertoire de sortie (défaut: ../data/extracted/)'
    )
    
    parser.add_argument(
        '--encoding',
        type=str,
        default='utf-8',
        help='Encodage des fichiers (défaut: utf-8)'
    )
    
    parser.add_argument(
        '--list-sheets',
        action='store_true',
        help='Lister les feuilles disponibles et quitter'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbeux'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Chemin du fichier Excel (relatif au script)
    script_dir = Path(__file__).parent
    excel_path = script_dir.parent / 'snadmin.xlsx'
    
    try:
        extractor = ExcelExtractor(
            excel_path=excel_path,
            output_dir=args.output_dir,
            output_format=args.format,
            encoding=args.encoding
        )
        
        if args.list_sheets:
            sheets = extractor.list_sheets()
            print("\nFeuilles disponibles:")
            for i, sheet in enumerate(sheets, 1):
                print(f"  {i}. {sheet}")
            return 0
        
        if args.all or not args.sheet:
            # Extraire toutes les feuilles
            results = extractor.extract_all()
        else:
            # Extraire une feuille spécifique
            extractor.extract_sheet(args.sheet)
        
        logger.info("\n✓ Extraction terminée avec succès")
        return 0
        
    except Exception as e:
        logger.error(f"\n✗ Erreur fatale: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
