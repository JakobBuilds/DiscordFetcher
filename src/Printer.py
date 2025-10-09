import os

from datetime import datetime
from PIL import Image as PILImage
from reportlab.platypus import Image as RLImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.lib.styles import getSampleStyleSheet


def skaliere_bild(printer_buffer, img_bytestream):
    frame = printer_buffer.frame
    max_width = frame.width - frame.leftPadding - frame.rightPadding
    max_height = (frame.height - frame.topPadding - frame.bottomPadding) /2.7

    # Originalbildgröße
    try:
        pil_img = PILImage.open(img_bytestream)
        width_pt, height_pt = pil_img.size  # Pixel → später in Punkte konvertieren
        ratio = min(max_width / width_pt, max_height / height_pt, 1.0)
        width_pt *= ratio
        height_pt *= ratio
        # Für PDF
        pdf_image = RLImage(img_bytestream, width=width_pt, height=height_pt)
        return pdf_image
    except Exception as e:
        printer_buffer.elements.append(Paragraph(f"[Problem scaling picture: {e}]", printer_buffer.styles['Italic']))
        return None


class PrinterBuffer:
    def __init__(self, output_name):
        self.message_count = 0
        # create doc
        self.elements = []
        self.styles = getSampleStyleSheet()

        folder = "discord_thread_downloads"
        os.makedirs(folder, exist_ok=True)
        self.output_name = output_name
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d")
        formatted2 = now.strftime("%H%M%S")
        # full path: folder/output_name YYYY-MM-DD.pdf
        filename = f"{formatted} {self.output_name} {formatted2}.pdf"
        full_path = os.path.join(folder, filename)

        self.doc = SimpleDocTemplate(full_path, pagesize=letter)
        self.frame = Frame(50, 50, 456, 636, id="normal")

    def add_message(self, author, timestamp, content, message_id, images_list = None):
        self.message_count += 1
        # Add author and text
        author_text = f"<b>{author}:</b> {content}   [{timestamp}]"
        self.elements.append(Paragraph(author_text, self.styles['Normal']))
        self.elements.append(Spacer(1, 8))

        # Add image if exists
        if images_list is not None and images_list: # nonempty list
            try:
                for img in images_list:
                    #image = Image(img, width=200, height=200)
                    image = skaliere_bild(self, img)
                    if image is not None:
                        self.elements.append(image)
                        self.elements.append(Spacer(1, 12))
                    else:
                        self.elements.append(
                            Paragraph(
                                "Bild konnte nicht skaliert werden (pdf? link?) für Zeitpunkt: "
                                + str(timestamp) + " und message id: " + str(message_id),
                                self.styles['Italic']  # or 'Normal'
                            )
                        )
            except Exception as e:
                self.elements.append(Paragraph(f"[Image could not be loaded: {e}]", self.styles['Italic']))

    def build_pdf(self):
        if self.message_count > 1:
            self.doc.build(self.elements)
            print("PDF created: " + self.output_name)
        else:
            print("Keine neuen nachrichten in diesem Thread: " + self.output_name)


