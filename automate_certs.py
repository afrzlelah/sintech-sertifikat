import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import img2pdf

# ============================================================
# CONFIGURATION - DESIGN LOCKED
# ============================================================
CONFIG = {
    "paths": {
        "excel": r"C:\Users\afrzl\Downloads\SERTIF_SINTECH\Utils\daftar peserta sintech.xlsx",
        "img_main": r"C:\Users\afrzl\Downloads\SERTIF_SINTECH\Utils\PESERTA .png",
        "img_grades": r"C:\Users\afrzl\Downloads\SERTIF_SINTECH\Utils\PESERTA (1).png",
        "output_dir": r"C:\Users\afrzl\Downloads\SERTIF_SINTECH\Output_Sertifikat",
    },
    "fonts": {
        "main_font_path": r"C:\Users\afrzl\Downloads\Inter,Poppins\Poppins\Poppins-Bold.ttf",
        "sub_font_path": r"C:\Users\afrzl\Downloads\Inter,Poppins\Poppins\Poppins-Regular.ttf",
        "name_size": 60,
        "role_size": 35,
        "grade_size": 40,
    },
    "coords_main": {
        "name": {"x": 800, "y": 650, "color": (0, 0, 0)},
    },
    "coords_grades": {
        "x": 730,
        "y_start": 330,
        "y_gap": 230,
        "color": (80,159,214),
    }
}

def generate_certificates():
    if not os.path.exists(CONFIG["paths"]["output_dir"]):
        os.makedirs(CONFIG["paths"]["output_dir"])

    try:
        df = pd.read_excel(CONFIG["paths"]["excel"], header=2)
        df.columns = [str(col).strip() for col in df.columns]
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    try:
        font_bold = ImageFont.truetype(CONFIG["fonts"]["main_font_path"], CONFIG["fonts"]["name_size"])
        font_reg = ImageFont.truetype(CONFIG["fonts"]["sub_font_path"], CONFIG["fonts"]["role_size"])
        font_grade = ImageFont.truetype(CONFIG["fonts"]["sub_font_path"], CONFIG["fonts"]["grade_size"])
    except Exception as e:
        print(f"Font error: {e}. Using default font.")
        font_bold = font_reg = font_grade = ImageFont.load_default()

    print(f"Processing {len(df)} certificates into PDFs...")

    for index, row in df.iterrows():
        nama = str(row['Nama']).upper() if pd.notna(row['Nama']) else "UNKNOWN"
        grades = [
            str(row['Kehadiran&keaktifan']) if pd.notna(row['Kehadiran&keaktifan']) else "-",
            str(row['Tugas mandiri']) if pd.notna(row['Tugas mandiri']) else "-",
            str(row['proyek kelompok/mini projek']) if pd.notna(row['proyek kelompok/mini projek']) else "-",
            str(row['Sikap & kolaborasi']) if pd.notna(row['Sikap & kolaborasi']) else "-"
        ]

        # 1. Generate Main Certificate
        cert_path = os.path.join(CONFIG["paths"]["output_dir"], f"temp_cert_{nama}.png")
        with Image.open(CONFIG["paths"]["img_main"]) as img1:
            draw1 = ImageDraw.Draw(img1)
            width, height = img1.size
            name_x = width // 2 if CONFIG["coords_main"]["name"]["x"] is None else CONFIG["coords_main"]["name"]["x"]
            draw1.text((name_x, CONFIG["coords_main"]["name"]["y"]), nama, font=font_bold, fill=CONFIG["coords_main"]["name"]["color"], anchor="mt")
            img1.save(cert_path)

        # 2. Generate Grades Page
        grade_path = os.path.join(CONFIG["paths"]["output_dir"], f"temp_grade_{nama}.png")
        with Image.open(CONFIG["paths"]["img_grades"]) as img2:
            draw2 = ImageDraw.Draw(img2)
            for i, val in enumerate(grades):
                y_pos = CONFIG["coords_grades"]["y_start"] + (i * CONFIG["coords_grades"]["y_gap"])
                val_text = font_grade.getbbox(val)[2]
                val_x = CONFIG["coords_grades"]["x"] - (val_text // 2)
                draw2.text((val_x, y_pos), val, font=font_grade, fill=CONFIG["coords_grades"]["color"])
            img2.save(grade_path)

        # 3. Merge to PDF
        pdf_path = os.path.join(CONFIG["paths"]["output_dir"], f"Sertifikat_{nama}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert([cert_path, grade_path]))

        # Clean up temp images
        os.remove(cert_path)
        os.remove(grade_path)

    print(f"Success! All PDFs saved to: {CONFIG['paths']['output_dir']}")

if __name__ == "__main__":
    generate_certificates()
