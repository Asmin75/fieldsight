from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

styleSheet = getSampleStyleSheet()
 
class MyPrint:


    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
 
        # Header
        header = Paragraph('Fieldsight   ' * 5, styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin)
 
        # Footer
        footer = Paragraph('Naxalicious  ' * 5, styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
 
        # Release the canvas
        canvas.restoreState()


    def print_users(self, forms):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=72,
                                bottomMargin=72,
                                pagesize=self.pagesize)
 
        # Our container for 'Flowable' objects
        elements = []
        
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        elements.append(Paragraph('Site Resonses', styles['Heading1']))
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        # users = [
           
        # ]
        # # elements.append(Paragraph('My User Names', styles['Heading1']))
        # # print data
        # # for i, user in enumerate(users):
        # #         elements.append(Paragraph(user['name'], styles['Normal']))
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        ts1 = TableStyle([
            ('ALIGN', (0,0), (-1,0), 'RIGHT'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                ])

        for form in forms:
            elements.append(Paragraph(form.xf.title, styles['Normal']))

            t1 = Table([
                ('plain text','plain text','shortpara','plain text', 'long para'),
                ('Text','more text', Paragraph('Is this para level?', styBackground), 'Back to text', Paragraph('Short para again', styBackground)),
                ('Text',
                    'more text',
                    Paragraph('Is this level?', styBackground),
                    'This is plain\ntext with line breaks\nto compare against\nthe para on right',
                    Paragraph('Long paragraph we expect to wrap over several lines accurately', styBackground)),
                
                ])
            t1.setStyle(ts1)
            elements.append(t1)









     
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
 
        # Get the value of the BytesIO buffer and write it to the response.
        #pdf = buffer.getvalue()
        #buffer.close()
        #return pdf

    '''
        Usage with django
    @staff_member_required
    def print_users(request):
        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="My Users.pdf"'
     
        buffer = BytesIO()
     
        report = MyPrint(buffer, 'Letter')
        pdf = report.print_users()
     
        response.write(pdf)
        return response
    '''


class NumberedCanvas(canvas.Canvas):


    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
 

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
 

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
 
 
    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(211 * mm, 15 * mm + (0.2 * inch),
                             "Page %d of %d" % (self._pageNumber, page_count))




# if __name__ == '__main__':
#     buffer = BytesIO()
     
#     report = MyPrint(buffer, 'Letter')
#     pdf = report.print_users()
#     buffer.seek(0)
 
#     with open('arquivo.pdf', 'wb') as f:
#         f.write(buffer.read())

# def site_responses_report(data):
#     buffer = BytesIO()
     
#     report = MyPrint(buffer, 'Letter')
#     pdf = report.print_users(data)
#     buffer.seek(0)
 
#     with open('arquivo.pdf', 'wb') as f:
#         f.write(buffer.read())    
