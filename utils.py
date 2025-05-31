import os
from datetime import datetime
from werkzeug.utils import secure_filename
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import xlsxwriter
from decimal import Decimal

# Configuration pour les uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.lower().split('.')[-1] in ALLOWED_EXTENSIONS

def save_file(file):
    """Sauvegarde un fichier uploadé avec un nom sécurisé"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ajouter un timestamp au nom du fichier pour éviter les doublons
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{name}_{timestamp}{ext}"
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(file_path)
        return new_filename
    return None

def format_currency(amount):
    """Formate un montant en devise"""
    if isinstance(amount, (int, float, Decimal)):
        return "{:,.2f} DT".format(float(amount))
    return "0,00 DT"

def generate_pdf_report(rapport):
    """Génère un rapport PDF à partir des données"""
    buffer = BytesIO()
    
    # Création du document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Liste des éléments du document
    elements = []
    
    # En-tête du rapport
    elements.append(Paragraph(f"Rapport {rapport.type_rapport.replace('_', ' ').title()}", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Période : {rapport.periode_formatee}", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Contenu spécifique selon le type de rapport
    if rapport.type_rapport == 'flux_tresorerie':
        elements.extend(generate_flux_tresorerie_content(rapport))
    elif rapport.type_rapport == 'bilan':
        elements.extend(generate_bilan_content(rapport))
    elif rapport.type_rapport == 'resultats':
        elements.extend(generate_resultats_content(rapport))
    elif rapport.type_rapport == 'budget':
        elements.extend(generate_budget_content(rapport))
    elif rapport.type_rapport == 'vehicules':
        elements.extend(generate_vehicules_content(rapport))
    
    # Pied de page
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} par {rapport.created_by}",
        normal_style
    ))
    
    # Génération du PDF
    doc.build(elements)
    
    # Retour au début du buffer
    buffer.seek(0)
    return buffer

def generate_flux_tresorerie_content(rapport):
    """Génère le contenu pour un rapport de flux de trésorerie"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Tableau des transactions
    data = [['Date', 'Description', 'Type', 'Montant']]
    
    for transaction in rapport.contenu['transactions']:
        data.append([
            transaction['date'],
            transaction['description'],
            transaction['type'],
            format_currency(transaction['montant'])
        ])
    
    # Style du tableau
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)
    
    return elements

def generate_excel_report(rapport):
    """Génère un rapport Excel à partir des données"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Styles
    header_format = workbook.add_format({
        'bold': True,
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    currency_format = workbook.add_format({'num_format': '#,##0.00 "DT"'})
    
    # En-tête
    worksheet.write('A1', 'Date')
    worksheet.write('B1', 'Description')
    worksheet.write('C1', 'Type')
    worksheet.write('D1', 'Montant')
    
    # Données
    row = 1
    if rapport.type_rapport == 'flux_tresorerie':
        for transaction in rapport.contenu['transactions']:
            worksheet.write_datetime(row, 0, datetime.strptime(transaction['date'], '%Y-%m-%d'), date_format)
            worksheet.write(row, 1, transaction['description'])
            worksheet.write(row, 2, transaction['type'])
            worksheet.write_number(row, 3, float(transaction['montant']), currency_format)
            row += 1
    
    # Ajustement automatique de la largeur des colonnes
    worksheet.autofit()
    
    workbook.close()
    output.seek(0)
    return output

def calculate_financial_indicators(transactions, periode_debut, periode_fin):
    """Calcule les indicateurs financiers pour une période donnée"""
    revenus = sum(t.montant for t in transactions if t.type == 'Revenu')
    depenses = sum(t.montant for t in transactions if t.type == 'Dépense')
    
    return {
        'total_revenus': revenus,
        'total_depenses': depenses,
        'solde': revenus - depenses,
        'ratio_depenses': (depenses / revenus * 100) if revenus > 0 else 0
    }

def get_monthly_stats(transactions, year):
    """Retourne les statistiques mensuelles des transactions"""
    monthly_stats = {}
    
    for transaction in transactions:
        if transaction.date_transaction.year == year:
            month = transaction.date_transaction.month
            if month not in monthly_stats:
                monthly_stats[month] = {'revenus': 0, 'depenses': 0}
            
            if transaction.type == 'Revenu':
                monthly_stats[month]['revenus'] += float(transaction.montant)
            else:
                monthly_stats[month]['depenses'] += float(transaction.montant)
    
    return monthly_stats

def generate_budget_summary(budgets):
    """Génère un résumé des budgets"""
    total_prevu = sum(float(b.montant_prevu) for b in budgets)
    total_actuel = sum(float(b.montant_actuel) for b in budgets)
    
    return {
        'total_prevu': total_prevu,
        'total_actuel': total_actuel,
        'pourcentage_global': (total_actuel / total_prevu * 100) if total_prevu > 0 else 0,
        'budgets': [{
            'categorie': b.categorie,
            'prevu': float(b.montant_prevu),
            'actuel': float(b.montant_actuel),
            'pourcentage': float(b.pourcentage_utilisation)
        } for b in budgets]
    }