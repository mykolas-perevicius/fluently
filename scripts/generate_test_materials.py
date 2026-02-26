#!/usr/bin/env python3
"""
Generate test materials for the Fluently translation app.

Creates various test documents in scripts/test_materials/ including:
- A multi-page PDF with rich formatting (using PyMuPDF/fitz)
- A PII-laden business letter
- A simple plain text document
- A markdown sample document
- A multilingual PII document (English/Spanish)

Usage (from project root):
    python3 scripts/generate_test_materials.py
"""

from __future__ import annotations

import os
import sys
import textwrap
from typing import Optional

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_materials")

# Ensure the backend venv's packages are importable if needed
backend_venv_site = os.path.join(
    PROJECT_ROOT, "backend", ".venv", "lib"
)
if os.path.isdir(backend_venv_site):
    for entry in os.listdir(backend_venv_site):
        sp = os.path.join(backend_venv_site, entry, "site-packages")
        if os.path.isdir(sp) and sp not in sys.path:
            sys.path.insert(0, sp)

# Also allow imports from backend/src/
backend_src = os.path.join(PROJECT_ROOT, "backend", "src")
if os.path.isdir(backend_src) and backend_src not in sys.path:
    sys.path.insert(0, backend_src)

import fitz  # PyMuPDF


# ===================================================================
# 1. sample_report.pdf -- Multi-page PDF with rich formatting
# ===================================================================

def generate_sample_report(path: str) -> None:
    """Create a 3-page PDF about climate change with varied formatting."""

    doc = fitz.open()  # new empty PDF

    # ----- helpers -----
    def _wrapped_lines(text: str, chars_per_line: int = 90) -> list[str]:
        """Word-wrap *text* into lines of roughly *chars_per_line* chars."""
        return textwrap.wrap(text, width=chars_per_line)

    def _insert_wrapped(page, x: float, y: float, text: str,
                        fontsize: float = 11, fontname: str = "helv",
                        chars_per_line: int = 90,
                        line_spacing: Optional[float] = None) -> float:
        """Insert word-wrapped text and return the y position after the last line."""
        if line_spacing is None:
            line_spacing = fontsize * 1.4
        for line in _wrapped_lines(text, chars_per_line):
            page.insert_text(fitz.Point(x, y), line,
                             fontsize=fontsize, fontname=fontname)
            y += line_spacing
        return y

    # ------------------------------------------------------------------ page 1
    page1 = doc.new_page(width=612, height=792)

    # Title
    page1.insert_text(fitz.Point(72, 80),
                      "Global Climate Change: A Comprehensive Overview",
                      fontsize=24, fontname="tibo")

    # Subtitle
    page1.insert_text(fitz.Point(72, 115),
                      "Understanding the Science, Impacts, and Pathways Forward",
                      fontsize=16, fontname="tiit")

    # Horizontal rule (thin rect)
    page1.draw_line(fitz.Point(72, 125), fitz.Point(540, 125))

    y = 155

    para1 = (
        "Climate change represents one of the most significant challenges facing "
        "humanity in the twenty-first century. The overwhelming consensus among "
        "climate scientists is that human activities, particularly the burning of "
        "fossil fuels and deforestation, have led to a measurable increase in "
        "global average temperatures. Since the pre-industrial era, Earth's mean "
        "surface temperature has risen by approximately 1.1 degrees Celsius, with "
        "the rate of warming accelerating in recent decades."
    )
    y = _insert_wrapped(page1, 72, y, para1)
    y += 8

    para2 = (
        "The Intergovernmental Panel on Climate Change (IPCC) has published "
        "extensive reports documenting the physical science basis of climate "
        "change. These reports draw on thousands of peer-reviewed studies and "
        "represent the work of hundreds of scientists from around the world. "
        "Key findings include rising sea levels, shrinking ice sheets, declining "
        "Arctic sea ice, ocean acidification, and an increase in extreme weather "
        "events such as heatwaves, droughts, and intense precipitation."
    )
    y = _insert_wrapped(page1, 72, y, para2)
    y += 8

    para3 = (
        "Addressing climate change requires a coordinated global effort that "
        "encompasses mitigation strategies to reduce greenhouse gas emissions, "
        "adaptation measures to cope with impacts that are already unavoidable, "
        "and investments in research and development of clean energy technologies. "
        "International agreements such as the Paris Agreement aim to limit global "
        "warming to well below 2 degrees Celsius above pre-industrial levels, "
        "with efforts to limit it to 1.5 degrees. Achieving these targets will "
        "demand transformative changes across energy, transportation, agriculture, "
        "and industrial sectors worldwide."
    )
    y = _insert_wrapped(page1, 72, y, para3)

    # Footer
    page1.insert_text(fitz.Point(290, 770), "- 1 -",
                      fontsize=10, fontname="helv")

    # ------------------------------------------------------------------ page 2
    page2 = doc.new_page(width=612, height=792)

    page2.insert_text(fitz.Point(72, 70),
                      "Key Contributing Factors",
                      fontsize=18, fontname="tibo")

    bullets = [
        "Fossil fuel combustion for electricity, heat, and transportation "
        "accounts for roughly 73% of global greenhouse gas emissions.",
        "Deforestation and land-use changes release stored carbon and reduce "
        "the planet's capacity to absorb CO2 from the atmosphere.",
        "Agricultural practices, including livestock farming and rice paddies, "
        "produce significant quantities of methane and nitrous oxide.",
        "Industrial processes such as cement and steel production generate "
        "substantial CO2 emissions that are difficult to abate.",
        "Waste decomposition in landfills produces methane, a greenhouse gas "
        "with roughly 80 times the warming potential of CO2 over 20 years.",
    ]

    y = 100
    for bullet in bullets:
        lines = _wrapped_lines(bullet, chars_per_line=85)
        for i, line in enumerate(lines):
            prefix = "\u2022  " if i == 0 else "   "
            page2.insert_text(fitz.Point(80, y), prefix + line,
                              fontsize=11, fontname="helv")
            y += 15.4
        y += 6

    y += 14
    page2.insert_text(fitz.Point(72, y),
                      "Projected Consequences",
                      fontsize=18, fontname="tibo")
    y += 28

    consequences = (
        "If emissions continue on their current trajectory, scientists project "
        "that global temperatures could rise by 2.5 to 4.5 degrees Celsius by "
        "the end of this century. Such warming would trigger cascading effects: "
        "sea-level rise of up to one meter threatening coastal cities, more "
        "frequent and severe weather events, disruption of agricultural systems "
        "leading to food insecurity, loss of biodiversity as ecosystems shift "
        "faster than species can adapt, and increased competition for fresh "
        "water resources. The economic costs of inaction are estimated to reach "
        "trillions of dollars annually by 2100, disproportionately affecting "
        "developing nations that have contributed least to the problem."
    )
    y = _insert_wrapped(page2, 72, y, consequences)
    y += 8

    solutions_intro = (
        "Transitioning to renewable energy sources such as solar, wind, and "
        "geothermal power is central to any viable climate strategy. Equally "
        "important are improvements in energy efficiency, electrification of "
        "transportation, sustainable agricultural practices, and the protection "
        "and restoration of forests and wetlands that serve as carbon sinks."
    )
    _insert_wrapped(page2, 72, y, solutions_intro)

    page2.insert_text(fitz.Point(290, 770), "- 2 -",
                      fontsize=10, fontname="helv")

    # ------------------------------------------------------------------ page 3
    page3 = doc.new_page(width=612, height=792)

    page3.insert_text(fitz.Point(72, 70),
                      "CO2 Emissions by Country (2024 Estimates)",
                      fontsize=18, fontname="tibo")

    # Table header
    col_x = [80, 250, 420]
    headers = ["Country", "Emissions (Mt CO2)", "% of Global"]
    y = 105
    for cx, hdr in zip(col_x, headers):
        page3.insert_text(fitz.Point(cx, y), hdr,
                          fontsize=11, fontname="tibo")

    # Separator line
    page3.draw_line(fitz.Point(75, y + 5), fitz.Point(535, y + 5))

    rows = [
        ("China",          "11,470",   "30.7%"),
        ("United States",  "5,010",    "13.4%"),
        ("India",          "2,880",    "7.7%"),
        ("European Union", "2,790",    "7.5%"),
    ]
    y += 22
    for country, emissions, pct in rows:
        page3.insert_text(fitz.Point(col_x[0], y), country,
                          fontsize=11, fontname="helv")
        page3.insert_text(fitz.Point(col_x[1], y), emissions,
                          fontsize=11, fontname="helv")
        page3.insert_text(fitz.Point(col_x[2], y), pct,
                          fontsize=11, fontname="helv")
        y += 18

    # Bottom line
    page3.draw_line(fitz.Point(75, y), fitz.Point(535, y))

    y += 30
    page3.insert_text(fitz.Point(72, y),
                      "Conclusion",
                      fontsize=18, fontname="tibo")
    y += 28

    conclusion = (
        "The data make clear that addressing climate change is both an urgent "
        "necessity and a shared responsibility. While the largest emitters bear "
        "a particular obligation to lead in reducing emissions, every nation must "
        "contribute to the transition toward a low-carbon economy. The scientific "
        "evidence is unequivocal: without rapid and sustained reductions in "
        "greenhouse gas emissions, the most severe impacts of climate change will "
        "become unavoidable. However, the same body of evidence also shows that "
        "meaningful action taken now can still avert the worst outcomes and create "
        "a more sustainable, resilient, and equitable world for future generations."
    )
    _insert_wrapped(page3, 72, y, conclusion)

    page3.insert_text(fitz.Point(290, 770), "- 3 -",
                      fontsize=10, fontname="helv")

    doc.save(path)
    doc.close()


# ===================================================================
# 2. pii_document.txt -- Business letter loaded with PII
# ===================================================================

PII_DOCUMENT = textwrap.dedent("""\
    CONFIDENTIAL MEMORANDUM

    Meridian Consulting Group
    1742 Oakwood Boulevard, Suite 310
    San Francisco, CA 94107

    Date: January 15, 2026
    To: All Department Heads
    From: Jonathan R. Whitfield, Chief Operating Officer
    Re: Annual Client Data Audit and Security Review

    Dear Colleagues,

    As we begin the new fiscal year, I want to address several matters related to
    our client data management practices and the upcoming security audit scheduled
    for March 2026. This memorandum outlines the key action items and contacts for
    each department.

    First, I would like to acknowledge the outstanding work of our data governance
    team, led by Dr. Amelia Chen. Her team completed a comprehensive review of our
    data retention policies last quarter and identified several areas for
    improvement. Dr. Chen can be reached at amelia.chen@meridianconsulting.com or
    by phone at (415) 555-0198 for any questions regarding the updated policies.

    Our external auditor, Marcus Delgado from TrueNorth Compliance Partners, will
    be on site during the first two weeks of March. Marcus has requested that all
    departments prepare documentation of their data handling procedures. He can be
    contacted at m.delgado@truenorthcompliance.com or 1-800-555-7342 if you need
    clarification on the audit requirements before his arrival.

    For the purposes of the test environment, our IT department has set up a
    sandbox server at 192.168.14.203 that mirrors our production systems. Please
    direct all test queries to this server rather than the live environment. The
    sandbox uses sample data, including the following test records that should
    never appear in production:

        Test Customer: Rebecca Okonkwo
        Test SSN: 123-45-6789
        Test Credit Card: 4532 8901 2345 6780
        Test Email: r.okonkwo@testdomain.example.com

    These test records are clearly marked in the database with a flag value of
    "TEST_ONLY" and should be purged after the audit concludes.

    I also want to remind everyone of the importance of protecting personally
    identifiable information in our day-to-day operations. Under both federal and
    state regulations, the mishandling of PII can result in substantial penalties
    for the firm. Every employee is responsible for ensuring that sensitive data
    such as Social Security numbers, financial account details, medical records,
    and personal contact information are stored, transmitted, and disposed of in
    accordance with our Information Security Policy (ISP-2024-07).

    During last year's audit, TrueNorth Compliance Partners identified three minor
    findings related to access controls and encryption at rest. All three findings
    have since been remediated, and the patches were verified by our internal
    security team in November 2025. The remediation report is available on the
    shared drive under /security/audits/2025/remediation_final.pdf.

    Each department head should submit a completed Data Handling Questionnaire by
    February 28, 2026. The questionnaire template is attached to this memo and
    should be returned to me directly at j.whitfield@meridianconsulting.com. Please
    ensure that your responses are thorough and accurate, as they will form the
    basis of our pre-audit self-assessment.

    Looking ahead, Meridian Consulting Group is committed to maintaining the
    highest standards of data privacy and security. Our clients trust us with
    their most sensitive information, and that trust is the foundation of our
    business. I am confident that with your continued diligence and cooperation,
    we will pass the upcoming audit with distinction.

    Thank you for your attention to these matters. Please do not hesitate to
    reach out if you have any questions or concerns.

    Sincerely,

    Jonathan R. Whitfield
    Chief Operating Officer
    Meridian Consulting Group
""")


# ===================================================================
# 3. simple_text.txt -- Plain text about technology
# ===================================================================

SIMPLE_TEXT = textwrap.dedent("""\
    The Rapid Evolution of Technology in Everyday Life

    Over the past two decades, technology has transformed nearly every aspect of
    daily life in ways that earlier generations could scarcely have imagined.
    Smartphones, once considered luxury gadgets, have become indispensable tools
    for communication, navigation, banking, entertainment, and even health
    monitoring. The average person now carries more computing power in their
    pocket than was available to the entire Apollo space program. This
    democratization of technology has reshaped how we work, learn, socialize,
    and interact with the world around us.

    Artificial intelligence and machine learning represent the next frontier of
    technological progress. From voice assistants that understand natural language
    to recommendation algorithms that curate our media consumption, AI systems
    are woven into the fabric of modern digital experiences. In professional
    settings, machine learning models analyze vast datasets to uncover patterns
    that would take human researchers years to identify. Medical imaging, drug
    discovery, financial modeling, and climate science have all benefited from
    these advances. Yet the rapid adoption of AI also raises important questions
    about bias, transparency, accountability, and the future of employment in
    an increasingly automated economy.

    Looking further ahead, emerging technologies such as quantum computing,
    augmented reality, and brain-computer interfaces promise to push the
    boundaries of what is possible even further. Quantum computers, still in
    their early stages, could eventually solve problems in cryptography,
    materials science, and optimization that are intractable for classical
    machines. Augmented reality overlays digital information onto the physical
    world, offering new possibilities for education, design, and remote
    collaboration. Brain-computer interfaces, meanwhile, are already enabling
    paralyzed patients to control prosthetic limbs and communicate through
    thought alone. As these technologies mature, society will face profound
    choices about how to harness their potential while safeguarding privacy,
    equity, and human dignity.
""")


# ===================================================================
# 4. markdown_sample.md -- Markdown with varied formatting
# ===================================================================

MARKDOWN_SAMPLE = textwrap.dedent("""\
    # Introduction to Sustainable Energy

    Sustainable energy is energy that meets the needs of the present without
    compromising the ability of future generations to meet their own needs.
    As global demand for electricity continues to rise, the transition from
    fossil fuels to renewable sources has become one of the defining
    challenges of our time.

    ## Types of Renewable Energy

    There are several major categories of renewable energy:

    - **Solar Power** -- Converts sunlight directly into electricity using
      photovoltaic cells or concentrates it to produce thermal energy.
    - **Wind Power** -- Harnesses kinetic energy from wind using turbines,
      both onshore and offshore.
    - **Hydroelectric Power** -- Generates electricity from the gravitational
      force of falling or flowing water.
    - **Geothermal Energy** -- Taps into heat stored beneath the Earth's
      surface for electricity generation and direct heating.
    - **Biomass Energy** -- Derives energy from organic materials such as
      wood, agricultural residues, and dedicated energy crops.

    ## Key Benefits

    1. **Reduced Greenhouse Gas Emissions** -- Renewables produce little to no
       direct carbon emissions during operation.
    2. **Energy Independence** -- Countries can reduce reliance on imported
       fossil fuels.
    3. **Job Creation** -- The renewable energy sector is one of the fastest-
       growing sources of employment worldwide.

    ## Challenges and Considerations

    Despite their advantages, renewable energy sources face challenges:

    | Challenge           | Description                                        |
    |---------------------|----------------------------------------------------|
    | Intermittency       | Solar and wind depend on weather conditions.        |
    | Storage             | Battery technology must improve for grid-scale use. |
    | Infrastructure      | Existing grids need upgrades to handle renewables.  |
    | Land Use            | Large installations require significant space.      |

    > "The stone age did not end for lack of stone, and the oil age will end
    > long before the world runs out of oil."
    > -- Sheikh Ahmed Zaki Yamani

    ## Further Reading

    - [International Renewable Energy Agency (IRENA)](https://www.irena.org/)
    - [U.S. Department of Energy -- Renewable Energy](https://www.energy.gov/eere/renewable-energy)
    - [IPCC Special Report on Renewable Energy](https://www.ipcc.ch/report/renewable-energy-sources-and-climate-change-mitigation/)

    ---

    *Last updated: February 2026*
""")


# ===================================================================
# 5. multilingual_pii.txt -- English & Spanish with PII
# ===================================================================

MULTILINGUAL_PII = textwrap.dedent("""\
    AVISO INTERNO / INTERNAL NOTICE
    Fecha / Date: 10 de febrero de 2026

    Estimados miembros del equipo,

    Les escribo para informarles sobre los cambios recientes en nuestro sistema
    de gestion de datos de clientes. Como parte de la actualizacion del sistema,
    se han migrado todos los registros al nuevo servidor centralizado. Si
    experimentan algun problema de acceso, comuniquense con nuestro equipo de
    soporte tecnico.

    Dear team members,

    I am writing to inform you about the recent changes to our client data
    management system. As part of the system upgrade, all records have been
    migrated to the new centralized server. If you experience any access issues,
    please contact our technical support team.

    --- Contactos / Contacts ---

    Soporte tecnico / Technical Support:
        Nombre: Carlos Enrique Montoya
        Correo: carlos.montoya@empresaglobal.com.mx
        Telefono: +52 55 4321 8765

    Coordinadora de proyecto / Project Coordinator:
        Name: Sarah Elizabeth Thompson
        Email: s.thompson@globalventures.co.uk
        Phone: +44 20 7946 0958

    Auditor externo / External Auditor:
        Nombre: Luis Fernando Reyes Gutierrez
        Correo: lf.reyes@auditoriaexterna.es
        Telefono: +34 91 123 4567

    --- Datos de prueba / Test Data ---

    Los siguientes registros son ficticios y se utilizan unicamente para
    verificar el correcto funcionamiento del sistema de deteccion de datos
    personales. No deben ser considerados datos reales.

    The following records are fictitious and are used solely to verify the
    correct functioning of the personal data detection system. They should
    not be treated as real data.

        Nombre / Name: Ana Sofia Delgado Ruiz
        Numero de Seguro Social / SSN: 987-65-4321
        Tarjeta de credito / Credit Card: 5412 7534 9012 3456
        Direccion IP / IP Address: 10.0.42.117
        Direccion fisica / Physical Address:
            Calle Reforma 2450, Piso 8
            Colonia Juarez, Ciudad de Mexico, CP 06600

    Es fundamental que todos los departamentos revisen sus procedimientos de
    manejo de informacion personal antes del 1 de marzo de 2026. La proteccion
    de los datos personales de nuestros clientes es una responsabilidad
    compartida y una obligacion legal.

    It is essential that all departments review their personal information
    handling procedures before March 1, 2026. The protection of our clients'
    personal data is a shared responsibility and a legal obligation.

    Atentamente / Regards,

    Carlos Enrique Montoya
    Director de Tecnologia / Chief Technology Officer
    EmpresaGlobal S.A. de C.V.
""")


# ===================================================================
# Main
# ===================================================================

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}\n")

    # 1. PDF
    pdf_path = os.path.join(OUTPUT_DIR, "sample_report.pdf")
    generate_sample_report(pdf_path)
    print(f"[1/5] Created {pdf_path}")

    # 2. PII document
    pii_path = os.path.join(OUTPUT_DIR, "pii_document.txt")
    with open(pii_path, "w", encoding="utf-8") as f:
        f.write(PII_DOCUMENT)
    print(f"[2/5] Created {pii_path}")

    # 3. Simple text
    simple_path = os.path.join(OUTPUT_DIR, "simple_text.txt")
    with open(simple_path, "w", encoding="utf-8") as f:
        f.write(SIMPLE_TEXT)
    print(f"[3/5] Created {simple_path}")

    # 4. Markdown sample
    md_path = os.path.join(OUTPUT_DIR, "markdown_sample.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(MARKDOWN_SAMPLE)
    print(f"[4/5] Created {md_path}")

    # 5. Multilingual PII
    multi_path = os.path.join(OUTPUT_DIR, "multilingual_pii.txt")
    with open(multi_path, "w", encoding="utf-8") as f:
        f.write(MULTILINGUAL_PII)
    print(f"[5/5] Created {multi_path}")

    print(f"\nDone. Generated 5 test material files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
