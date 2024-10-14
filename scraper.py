import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import os
import time

def extract_urls(base_url):
    print(f"Accediendo a la página principal: {base_url}")
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Error accediendo a {base_url}. Código de estado: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    print("Extrayendo URLs de los topics y subtopics...")
    
    urls = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/es/docs/'):  
            full_url = f"https://example.org{href}"
            urls.append(full_url)
    
    unique_urls = list(set(urls))  
    print(f"Se encontraron {len(unique_urls)} URLs únicas.")
    return unique_urls

def scrape_content(url):
    print(f"Accediendo a: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error accediendo a {url}. Código de estado: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Eliminar secciones de footnotes y overflow-hidden
        for footnotes_section in soup.find_all('section', class_='footnotes'):
            footnotes_section.decompose()

        # Eliminar secciones de overflow-hidden
        for overflow_section in soup.find_all('div', class_='overflow-hidden'):
            overflow_section.decompose()

        # Eliminar el último div dentro del contenedor 'markdown-page'
        markdown_page = soup.find('div', {'id': 'markdown-page'})
        if markdown_page:
            last_div = markdown_page.find_all('div')[-1] if markdown_page.find_all('div') else None
            if last_div:
                last_div.decompose()

        # Obtenemos el título y el contenido principal
        title = soup.find('h1').get_text() if soup.find('h1') else "Sin título"
        content = markdown_page.get_text() if markdown_page else "Sin contenido"

        print(f"Scrapeo exitoso: {title}")
        return {
            "title": title,
            "content": content,
            "url": url
        }
    except Exception as e:
        print(f"Error scrapeando {url}: {e}")
        return None



from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font('DejaVu', 'B', 12)  # Usamos la fuente DejaVu en negrita
        self.cell(0, 10, 'Learn Prompting - Topics and Subtopics', ln=True, align='C')

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 12)  # Usamos la fuente DejaVu en negrita
        self.cell(0, 10, title, ln=True)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 12)  # Usamos la fuente DejaVu normal
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)

def generate_pdf(content_list, output_filename):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Cargamos las variantes de la fuente DejaVu (normal y bold)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)

    # Añadir tabla de contenidos
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, 'Table of Contents', ln=True)

    for idx, content in enumerate(content_list):
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, f"{idx+1}. {content['title']}", ln=True)
    

    for content in content_list:
        pdf.add_chapter(content['title'], content['content'])
    
    pdf.output(output_filename)

def main():
    base_url = 'https://example.org/es/docs/introduction'
    
    urls = extract_urls(base_url)
    if not urls:
        print("No se encontraron URLs para procesar.")
        return
    
    content_list = []
    for url in urls:
        content = scrape_content(url)
        if content:
            content_list.append(content)
    
    output_filename = 'learn_prompting_topics.pdf'
    generate_pdf(content_list, output_filename)
    print(f"PDF generado: {output_filename}")

if __name__ == "__main__":
    main()
