#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de normalisation et validation des données extraites
Nettoie, valide et structure les données pour l'import Odoo
"""

import argparse
import logging
import sys
import re
from pathlib import Path
import pandas as pd
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from unidecode import unidecode

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('normalization_errors.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalisateur et validateur de données"""
    
    def __init__(self, input_dir, output_dir, fix_errors=True, strict=False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.fix_errors = fix_errors
        self.strict = strict
        
        # Statistiques
        self.stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'warnings': [],
            'errors': []
        }
        
        # Créer le répertoire de sortie
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialisation du normalisateur")
        logger.info(f"Répertoire source: {self.input_dir}")
        logger.info(f"Répertoire de sortie: {self.output_dir}")
        logger.info(f"Mode strict: {self.strict}")
    
    def normalize_column_name(self, col):
        """Normalise un nom de colonne"""
        # Supprimer les accents
        col = unidecode(col)
        # Minuscules
        col = col.lower()
        # Remplacer espaces et caractères spéciaux par underscore
        col = re.sub(r'[^a-z0-9]+', '_', col)
        # Supprimer underscores multiples
        col = re.sub(r'_+', '_', col)
        # Supprimer underscores en début/fin
        col = col.strip('_')
        return col
    
    def normalize_text(self, text):
        """Normalise un texte (noms, adresses)"""
        if pd.isna(text) or text == '':
            return ''
        text = str(text).strip()
        # Première lettre en majuscule pour chaque mot
        text = text.title()
        return text
    
    def normalize_code(self, code):
        """Normalise un code (majuscules, alphanumériques)"""
        if pd.isna(code) or code == '':
            return ''
        code = str(code).strip().upper()
        # Garder seulement alphanumériques
        code = re.sub(r'[^A-Z0-9]', '', code)
        return code
    
    def validate_email(self, email):
        """Valide et normalise un email"""
        if pd.isna(email) or email == '':
            return '', None
        
        email = str(email).strip().lower()
        
        try:
            # Validation RFC 5322
            valid = validate_email(email, check_deliverability=False)
            return valid.email, None
        except EmailNotValidError as e:
            if self.fix_errors:
                # Tentative de correction simple
                if '@' not in email and '.' in email:
                    # Peut-être manque le @
                    return '', f"Email invalide (pas de @): {email}"
                return '', f"Email invalide: {email} ({str(e)})"
            else:
                return email, f"Email invalide: {email} ({str(e)})"
    
    def validate_phone(self, phone, country='SN'):
        """Valide et formate un numéro de téléphone"""
        if pd.isna(phone) or phone == '':
            return '', None
        
        phone = str(phone).strip()
        
        try:
            # Parser le numéro
            parsed = phonenumbers.parse(phone, country)
            
            # Vérifier si valide
            if not phonenumbers.is_valid_number(parsed):
                if self.fix_errors:
                    return '', f"Téléphone invalide: {phone}"
                else:
                    return phone, f"Téléphone invalide: {phone}"
            
            # Formater en international
            formatted = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            return formatted, None
            
        except phonenumbers.NumberParseException as e:
            # Tentative de correction pour numéros sénégalais
            if self.fix_errors and phone.startswith(('33', '77', '78', '76', '70')):
                # Ajouter +221
                try:
                    parsed = phonenumbers.parse(f"+221{phone}", country)
                    if phonenumbers.is_valid_number(parsed):
                        formatted = phonenumbers.format_number(
                            parsed,
                            phonenumbers.PhoneNumberFormat.INTERNATIONAL
                        )
                        return formatted, None
                except:
                    pass
            
            return '', f"Téléphone invalide: {phone} ({str(e)})"
    
    def validate_url(self, url):
        """Valide et normalise une URL"""
        if pd.isna(url) or url == '':
            return '', None
        
        url = str(url).strip().lower()
        
        # Ajouter http:// si absent
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        
        # Validation basique
        if not re.match(r'^https?://[a-z0-9.-]+\.[a-z]{2,}', url):
            return '', f"URL invalide: {url}"
        
        return url, None
    
    def normalize_file(self, csv_file):
        """Normalise un fichier CSV"""
        logger.info(f"\nTraitement de: {csv_file.name}")
        
        try:
            # Lire le CSV
            df = pd.read_csv(csv_file, dtype=str)
            df = df.fillna('')
            
            original_rows = len(df)
            self.stats['total_rows'] += original_rows
            
            logger.info(f"  - {original_rows} lignes, {len(df.columns)} colonnes")
            
            # Normaliser les noms de colonnes
            old_columns = df.columns.tolist()
            new_columns = [self.normalize_column_name(col) for col in old_columns]
            df.columns = new_columns
            
            logger.info(f"  - Colonnes normalisées: {', '.join(new_columns)}")
            
            # Détecter les types de colonnes
            text_cols = [c for c in new_columns if any(k in c for k in ['nom', 'prenom', 'fonction', 'adresse', 'description', 'ministere', 'direction', 'service', 'interlocuteur'])]
            code_cols = [c for c in new_columns if 'code' in c or c == 'matricule']
            email_cols = [c for c in new_columns if 'email' in c or 'mail' in c]
            phone_cols = [c for c in new_columns if 'telephone' in c or 'tel' in c or 'phone' in c]
            url_cols = [c for c in new_columns if 'site' in c or 'web' in c or 'url' in c]
            
            # Normaliser les valeurs
            for col in text_cols:
                if col in df.columns:
                    df[col] = df[col].apply(self.normalize_text)
            
            for col in code_cols:
                if col in df.columns:
                    df[col] = df[col].apply(self.normalize_code)
            
            for col in email_cols:
                if col in df.columns:
                    results = df[col].apply(self.validate_email)
                    df[col] = results.apply(lambda x: x[0])
                    # Collecter les erreurs
                    for idx, (val, err) in enumerate(results):
                        if err:
                            self.stats['warnings'].append(f"{csv_file.name} ligne {idx+2}: {err}")
            
            for col in phone_cols:
                if col in df.columns:
                    results = df[col].apply(self.validate_phone)
                    df[col] = results.apply(lambda x: x[0])
                    # Collecter les erreurs
                    for idx, (val, err) in enumerate(results):
                        if err:
                            self.stats['warnings'].append(f"{csv_file.name} ligne {idx+2}: {err}")
            
            for col in url_cols:
                if col in df.columns:
                    results = df[col].apply(self.validate_url)
                    df[col] = results.apply(lambda x: x[0])
                    # Collecter les erreurs
                    for idx, (val, err) in enumerate(results):
                        if err:
                            self.stats['warnings'].append(f"{csv_file.name} ligne {idx+2}: {err}")
            
            # Supprimer les lignes complètement vides
            df = df.replace('', pd.NA)
            df = df.dropna(how='all')
            df = df.fillna('')
            
            # Supprimer les doublons
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                logger.warning(f"  - {duplicates} doublons détectés et supprimés")
                df = df.drop_duplicates()
            
            final_rows = len(df)
            self.stats['valid_rows'] += final_rows
            
            logger.info(f"  - {final_rows} lignes valides ({original_rows - final_rows} rejetées)")
            
            # Sauvegarder
            output_file = self.output_dir / f"{csv_file.stem}_normalized.csv"
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"  - Fichier créé: {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {csv_file.name}: {e}")
            self.stats['errors'].append(f"{csv_file.name}: {str(e)}")
            return None
    
    def normalize_all(self):
        """Normalise tous les fichiers CSV du répertoire"""
        csv_files = list(self.input_dir.glob('*.csv'))
        
        if not csv_files:
            logger.warning(f"Aucun fichier CSV trouvé dans {self.input_dir}")
            return []
        
        logger.info(f"Fichiers CSV trouvés: {len(csv_files)}")
        
        results = []
        for csv_file in csv_files:
            output_file = self.normalize_file(csv_file)
            if output_file:
                results.append(output_file)
        
        return results
    
    def generate_report(self):
        """Génère un rapport de qualité"""
        report_file = self.output_dir / 'quality_report.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT DE VALIDATION ===\n\n")
            f.write(f"Lignes totales traitées: {self.stats['total_rows']}\n")
            f.write(f"Lignes valides: {self.stats['valid_rows']}\n")
            f.write(f"Lignes rejetées: {self.stats['total_rows'] - self.stats['valid_rows']}\n\n")
            
            if self.stats['warnings']:
                f.write(f"⚠ {len(self.stats['warnings'])} avertissements:\n")
                for warning in self.stats['warnings'][:50]:  # Limiter à 50
                    f.write(f"  - {warning}\n")
                if len(self.stats['warnings']) > 50:
                    f.write(f"  ... et {len(self.stats['warnings']) - 50} autres\n")
                f.write("\n")
            
            if self.stats['errors']:
                f.write(f"✗ {len(self.stats['errors'])} erreurs:\n")
                for error in self.stats['errors']:
                    f.write(f"  - {error}\n")
                f.write("\n")
            
            if not self.stats['errors']:
                f.write("✓ Aucune erreur bloquante\n")
        
        logger.info(f"\nRapport de qualité généré: {report_file}")
        return report_file


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Normalisation et validation des données extraites'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Répertoire des fichiers CSV bruts'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Répertoire de sortie'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Générer un rapport de qualité'
    )
    
    parser.add_argument(
        '--fix-errors',
        action='store_true',
        default=True,
        help='Corriger automatiquement les erreurs mineures (défaut: activé)'
    )
    
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Mode strict (rejeter les enregistrements invalides)'
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
        normalizer = DataNormalizer(
            input_dir=args.input,
            output_dir=args.output,
            fix_errors=args.fix_errors,
            strict=args.strict
        )
        
        # Normaliser tous les fichiers
        results = normalizer.normalize_all()
        
        # Générer le rapport
        if args.report:
            normalizer.generate_report()
        
        # Résumé
        logger.info("\n=== RÉSUMÉ ===")
        logger.info(f"Fichiers traités: {len(results)}")
        logger.info(f"Lignes totales: {normalizer.stats['total_rows']}")
        logger.info(f"Lignes valides: {normalizer.stats['valid_rows']}")
        logger.info(f"Avertissements: {len(normalizer.stats['warnings'])}")
        logger.info(f"Erreurs: {len(normalizer.stats['errors'])}")
        
        if normalizer.stats['errors']:
            logger.warning("\n✗ Normalisation terminée avec erreurs")
            return 1
        else:
            logger.info("\n✓ Normalisation terminée avec succès")
            return 0
        
    except Exception as e:
        logger.error(f"\n✗ Erreur fatale: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
