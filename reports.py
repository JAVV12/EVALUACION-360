from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
import io

def generate_pdf_report(leader_name, company_name, stats):
    """
    Generates a PDF report for a specific leader.
    stats: Dict with commitment keys -> {Self, Observers, Gap}
    Returns a bytes buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', parent=styles['Heading1'], alignment=1))
    
    # Header
    elements.append(Paragraph(f"Reporte de Liderazgo 360: {leader_name}", styles['CenterTitle']))
    elements.append(Paragraph(f"Empresa: {company_name}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Data Table
    data = [["Compromiso", "Auto", "Otros", "Brecha"]]
    categories = list(stats.keys())
    
    # Prepare data for charts
    self_scores = []
    obs_scores = []
    
    for cat in categories:
        s = stats[cat]["Self"]
        o = stats[cat]["Observers"]
        g = stats[cat]["Gap"]
        data.append([cat, s, o, g])
        self_scores.append(s)
        obs_scores.append(o)
        
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 24))
    
    # Radar Chart (Spider Chart in ReportLab)
    # Note: ReportLab SpiderChart needs data as list of lists.
    d = Drawing(400, 200)
    sc = SpiderChart()
    sc.x = 50
    sc.y = 10
    sc.height = 180
    sc.width = 180
    sc.data = [self_scores, obs_scores]
    sc.labels = categories
    sc.strands.strokeColor = colors.white
    sc.fillColor = colors.lightblue
    sc.strands[0].strokeColor = colors.blue
    sc.strands[1].strokeColor = colors.red
    # Adding legend is manual in basic ReportLab shapes, simplified here by convention
    # Self = Blue, Observers = Red (implicitly, explaining in text below)
    
    d.add(sc)
    elements.append(Paragraph("<b>Gráfico de Radar</b> (Azul: Auto, Rojo: Observadores)", styles['Normal']))
    elements.append(d)
    elements.append(Spacer(1, 12))
    
    # Bar Chart
    d_bar = Drawing(400, 200)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = [self_scores, obs_scores]
    bc.categoryAxis.categoryNames = categories
    bc.bars[0].fillColor = colors.blue
    bc.bars[1].fillColor = colors.red
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 5
    
    d_bar.add(bc)
    elements.append(Paragraph("<b>Comparativa por Pilar</b>", styles['Normal']))
    elements.append(d_bar)
    elements.append(Spacer(1, 12))
    
    # Automated Insights (Feedback)
    # We need to import logic here or copy logic. Ideally we pass the insights text.
    # But since I didn't pass insights text to this function, I will re-generate or just generic text.
    # Let's simple re-generate using standard rules if we can, or just skip it.
    # To keep it loosely coupled, I should have passed insights.
    # I'll replicate simple logic here for the PDF or update the signature. 
    # Let's keep it simple: Just general analysis.
    
    elements.append(Paragraph("<b>Feedback Automático:</b>", styles['Heading2']))
    
    # Re-impl logic locally or import? Import is better.
    try:
        from logic import generate_insights
        insights = generate_insights(stats)
        for ins in insights:
            # Clean markdown basic symbols
            ins_clean = ins.replace("**", "").replace("⚠️", "[ATENCION]").replace("🌟", "[FORTALEZA]").replace("📉", "[MEJORA]")
            elements.append(Paragraph(ins_clean, styles['Normal']))
            elements.append(Spacer(1, 6))
    except ImportError:
        elements.append(Paragraph("Detalles disponibles en el dashboard interactivo.", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
