#app/export.py
from calendar import month_name
import locale
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import io
from io import BytesIO
from app.calculations import calculate_annual_production, calculate_monthly_production
from app.data_manager import load_turbines
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from reportlab.platypus import Image

# Set absolute path to the font file
#font_path = 'C:\\Users\\Niko\\OneDrive - Univerza v Mariboru\\Namizje\\FERI\\PraktikumDEM_KONCNA\\resources\\fonts\\DejaVuSans.ttf'
#bold_font_path = 'C:\\Users\\Niko\\OneDrive - Univerza v Mariboru\\Namizje\\FERI\\PraktikumDEM_KONCNA\\resources\\fonts\\DejaVuSansCondensed-Bold.ttf'

current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, '..', 'resources', 'fonts', 'DejaVuSans.ttf')
bold_font_path = os.path.join(current_dir, '..', 'resources', 'fonts', 'DejaVuSansCondensed-Bold.ttf')

if not os.path.exists(font_path):
    raise FileNotFoundError(f"Font file not found: {font_path}")
if not os.path.exists(bold_font_path):
    raise FileNotFoundError(f"Font file not found: {bold_font_path}")

pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))

#Točka 0 FIX PODATKI
def add_fixed_first_page(elements):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        fontName='DejaVuSans',
        fontSize=18,
        leading=22,
        spaceAfter=14,
    )
    subtitle_style = ParagraphStyle(
        'subtitle_style',
        parent=styles['Heading2'],
        fontName='DejaVuSans',
        fontSize=14,
        leading=18,
        spaceAfter=12,
        spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        'normal_style',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
    )
    bullet_style = ParagraphStyle(
        'bullet_style',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
        leftIndent=20,
        bulletIndent=10,
        spaceBefore=5,
    )

    elements.append(Paragraph("PRELIMINARNI IZRAČUN LETNE PROIZVODNJE ELEKTRIČNE ENERGIJE", title_style))
    elements.append(Spacer(1, 12))

    generation_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    elements.append(Paragraph(f"Datum izračuna: {generation_date}", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("OPIS:", subtitle_style))
    description = """
    - Dokument predstavlja informativni izračun letne proizvodnje električne energije za določene lokacije in izbrane turbine.
    - Podatki o vetru so vzeti iz Open-Meteo API, edinega API-a ki nam omogoča neomejeno število klicev zgodovinskih podatkov, vendar le na višini 100 m od površine.
    - Open-Meteo API ponuja pregled podatkov o vetru vsako uro v zadnjih 84 letih.
    - Pri izračunu proizvodnje smo vsako uro uporabili razpoložljive podatke.
    """
    for line in description.split('\n'):
        elements.append(Paragraph(line.strip(), bullet_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("VSEBINA:", subtitle_style))
    contents = """
    - Podatki o lokaciji
    - Izbrane turbine
    - Podatki o vetru
    - Izračun proizvodnje električne energije
    """
    for line in contents.split('\n'):
        elements.append(Paragraph(line.strip(), bullet_style))
    elements.append(Spacer(1, 12))
    elements.append(PageBreak())

#Točka 1 PODATKI O LOKACIJI
def add_location_data(elements, coordinates, map_image_path):
    styles = getSampleStyleSheet()
    subtitle_style = ParagraphStyle(
        'subtitle_style',
        parent=styles['Heading2'],
        fontName='DejaVuSans',
        fontSize=14,
        leading=18,
        spaceAfter=12,
        spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        'normal_style',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
    )
    bold_style = ParagraphStyle(
        'bold_style',
        parent=styles['Normal'],
        fontName='DejaVuSans-Bold',
        fontSize=12,
        leading=15,
    )

    elements.append(Paragraph("1. PODATKI O LOKACIJI", subtitle_style))
    elements.append(Spacer(1, 12))

    if map_image_path:
        elements.append(Image(map_image_path, width=15 * cm, height=10 * cm))
        elements.append(Spacer(1, 12))

    for i, coord in enumerate(coordinates, start=1):
        if (i == 4) or (i > 3 and (i - 4) % 9 == 0):
            elements.append(PageBreak())

        elements.append(Paragraph(f"OPIS LOKACIJE {i}", bold_style))
        elements.append(Spacer(1, 12))
        data = [
            ["", "Decimalne koordinate", "DMS"],
            ["Geografska širina", f"{coord[0]:.6f}", decimal_to_dms(coord[0])],
            ["Geografska dolžina", f"{coord[1]:.6f}", decimal_to_dms(coord[1])]
        ]
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (1, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (1, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (1, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
#Točka 2 IZBRANE TURBINE
from reportlab.platypus import KeepTogether, Image


def add_turbine_data(elements, selected_turbines):
    styles = getSampleStyleSheet()
    subtitle_style = ParagraphStyle(
        'subtitle_style',
        parent=styles['Heading2'],
        fontName='DejaVuSans',
        fontSize=14,
        leading=18,
        spaceAfter=12,
        spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        'normal_style',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
    )

    elements.append(PageBreak())
    elements.append(Paragraph("2. IZBRANE TURBINE", subtitle_style))
    elements.append(Spacer(1, 12))

    seen_turbines = set()

    for coords, turbines in selected_turbines.items():
        for turbine_name in turbines:
            if turbine_name not in seen_turbines:
                seen_turbines.add(turbine_name)
                turbine = next(t for t in load_turbines() if t['name'] == turbine_name)

                img_buf = plot_power_curve(turbine)
                table_data = [["Wind Speed [m/s]", "Power [kW]"]]
                for speed, power in zip(turbine['speeds'], turbine['powers']):
                    table_data.append([speed, power])

                # Split table data into two parts
                half = len(table_data) // 2
                table_data_1 = table_data[:half]
                table_data_2 = table_data[half:]

                # Create two smaller tables
                table_1 = Table(table_data_1, colWidths=[1.3 * inch, 1.3 * inch])
                table_2 = Table(table_data_2, colWidths=[1.3 * inch, 1.3 * inch])

                for table in [table_1, table_2]:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))

                # Combine turbine name, graph, and the two tables in a single row
                elements.append(Paragraph(f"• Naziv turbine: {turbine_name}", normal_style))
                elements.append(Spacer(1, 12))
                elements.append(Image(img_buf, width=10 * cm, height=6 * cm))
                elements.append(Spacer(1, 12))

                combined_table = Table(
                    [
                        [table_1, table_2]
                    ],
                    colWidths=[3 * inch, 3 * inch]
                )
                elements.append(combined_table)
                elements.append(Spacer(1, 12))

def plot_power_curve(turbine):
    fig, ax = plt.subplots(figsize=(6, 4))  # Adjust the figure size to fit better
    speeds = list(map(float, turbine["speeds"]))
    powers = list(map(float, turbine["powers"]))
    ax.plot(speeds, powers, label=turbine['name'])
    ax.set_xlabel('Wind Speed (m/s)')
    ax.set_ylabel('Power (kW)')
    ax.set_title(f'Power Curve for {turbine["name"]}')
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

#Točka 3 PODATKI O VETRU
def add_wind_data(elements, wind_data_dict):
    styles = getSampleStyleSheet()
    subtitle_style = ParagraphStyle(
        'subtitle_style',
        parent=styles['Heading2'],
        fontName='DejaVuSans',
        fontSize=14,
        leading=18,
        spaceAfter=12,
        spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        'normal_style',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
    )
    elements.append(Paragraph("3. PODATKI O VETRU", subtitle_style))
    elements.append(Spacer(1, 8))

    for coords, wind_data in wind_data_dict.items():
        elements.append(Paragraph(f"Lokacija: Koordinate lokacije v DMS {format_coords(coords)}", normal_style))
        elements.append(Paragraph(f"Obseg podatkov: 1.1.2023 – 31.12.2023", normal_style))
        elements.append(Spacer(1, 8))

        monthly_stats = wind_data.resample('M').agg({
            'wind_speed_100m': ['mean', 'min', 'max']
        }).reset_index()

        # Uporaba slovenske lokalne nastavitve za prikaz imen mesecev
        monthly_stats['month'] = monthly_stats['date'].dt.month.apply(lambda x: month_name[x])

        data = [['Mesec', 'Povprečna hitrost', 'Minimalna hitrost', 'Maksimalna hitrost']]
        for index, row in monthly_stats.iterrows():
            data.append(
                [row['month'].to_string(), f"{row[('wind_speed_100m', 'mean')]:.2f}", f"{row[('wind_speed_100m', 'min')]:.2f}",
                 f"{row[('wind_speed_100m', 'max')]:.2f}"])

        # Zmanjšanje velikosti tabele
        table = Table(data,
                      colWidths=[1.45 * inch, 1.37 * inch, 1.45 * inch, 1.37 * inch],
                      rowHeights=[0.34 * inch] * len(data))
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

        # Plotting graph
        fig, ax = plt.subplots(figsize=(8, 6))  # Increase the size of the graph
        ax.plot(monthly_stats['month'], monthly_stats[('wind_speed_100m', 'mean')], label='Povprečna hitrost')
        ax.plot(monthly_stats['month'], monthly_stats[('wind_speed_100m', 'min')], label='Minimalna hitrost')
        ax.plot(monthly_stats['month'], monthly_stats[('wind_speed_100m', 'max')], label='Maksimalna hitrost')
        ax.set_xlabel('Mesec')
        ax.set_ylabel('Hitrost vetra [m/s]')
        ax.set_title('Povprečna, minimalna in maksimalna hitrost vetra po mesecih')
        ax.legend()

        # Save the plot to a BytesIO object
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)

        # Increase the size of the graph in the PDF
        elements.append(Image(buf, width=15 * cm, height=8.5 * cm))
        elements.append(Spacer(1, 12))
        elements.append(PageBreak())


#Točka 4 IZRAČUN PROIZVODNJE ELEKTRIČNE ENERGIJE
def add_production_data(elements, wind_data_dict, selected_turbines):
    styles = getSampleStyleSheet()
    subtitle_style = ParagraphStyle(
        'subtitle_style',
        parent=styles['Heading2'],
        fontName='DejaVuSans',
        fontSize=14,
        leading=18,
        spaceAfter=12,
        spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        'normal_style',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
    )
    elements.append(Paragraph("4. IZRAČUN PROIZVODNJE ELEKTRIČNE ENERGIJE", subtitle_style))
    elements.append(Spacer(1, 12))

    location_count = 0

    for coords, turbines in selected_turbines.items():
        if location_count > 0 and location_count % 2 == 0:
            elements.append(PageBreak())

        elements.append(Paragraph(f"Lokacija: {format_coords(coords)}", normal_style))
        elements.append(Spacer(1, 12))

        turbine_names = []
        productions = []

        for turbine_name in turbines:
            turbine = next(t for t in load_turbines() if t['name'] == turbine_name)
            wind_data = wind_data_dict[coords]
            production = calculate_annual_production(wind_data, [turbine], 1)
            elements.append(Paragraph(f"{turbine_name}: <b>{production / 1000:.2f}</b> MWh", normal_style))
            turbine_names.append(turbine_name)
            productions.append(production / 1000)
            monthly_production, graph_image = calculate_monthly_production(wind_data, [turbine], 1)
            elements.append(graph_image)  # Dodajanje slike grafa v PDF

        # Ustvarite graf letne proizvodnje
        fig, ax = plt.subplots(figsize=(8, 6))  # Adjust size as needed
        ax.bar(turbine_names, productions, color='skyblue')
        ax.set_xlabel('Tip turbine')
        ax.set_ylabel('Proizvodnja (MWh)')
        ax.set_title('Letna proizvodnja za posamezno lokacijo')

        # Shranite graf v BytesIO objekt
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close(fig)
        img_buf.seek(0)

        # Dodajte graf kot sliko v PDF
        elements.append(Image(img_buf,  width=3.2 * inch, height=1.9 * inch))
        elements.append(Spacer(1, 6))
        elements.append(PageBreak())

        location_count += 1


def create_pdf(report_text, wind_data_dict, coordinates, selected_turbines, map_image_path, filename="report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    add_fixed_first_page(elements)
    add_location_data(elements, coordinates, map_image_path)
    add_turbine_data(elements, selected_turbines)
    add_wind_data(elements, wind_data_dict)
    add_production_data(elements, wind_data_dict, selected_turbines)
    elements = remove_empty_pages(elements)

    doc.build(elements)

def remove_empty_pages(elements):
    non_empty_elements = []
    for index, element in enumerate(elements):
        if isinstance(element, PageBreak):
            # Preveri, ali je naslednji element prazen
            if index + 1 < len(elements):
                next_element = elements[index + 1]
                # Če je naslednji element prazen, preskoči PageBreak
                if isinstance(next_element, Spacer):
                    continue
        non_empty_elements.append(element)
    return non_empty_elements
def export_to_pdf(report_text, wind_data_dict, coordinates, selected_turbines, map_image_path=None,
                  filename="report.pdf"):
    create_pdf(report_text, wind_data_dict, coordinates, selected_turbines, map_image_path, filename)

def format_coords(coords):
    lat_dms = decimal_to_dms(coords[0])
    lon_dms = decimal_to_dms(coords[1])
    lat_dir = "N" if coords[0] >= 0 else "S"
    lon_dir = "E" if coords[1] >= 0 else "W"
    return f"{lat_dms} {lat_dir}, {lon_dms} {lon_dir}"

def decimal_to_dms(decimal):
    degrees = int(decimal)
    minutes = int((abs(decimal) - abs(degrees)) * 60)
    seconds = (abs(decimal) - abs(degrees) - minutes / 60) * 3600
    return f"{abs(degrees)}°{minutes}'{seconds:.2f}\""
