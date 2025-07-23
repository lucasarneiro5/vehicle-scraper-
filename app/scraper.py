from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup

def configurar_driver():
    options = Options()
    #options.add_argument("--headless")  # comente esta linha se quiser ver o navegador
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Chrome(options=options)
    return driver

def selecionar_estado_e_buscar(driver, estado_value):
    wait = WebDriverWait(driver, 10)

    # Clicar em "Autos"
    try:
        autos = wait.until(EC.element_to_be_clickable((By.XPATH, '//p[text()="Autos"]')))
        autos.click()
        print("🚘 Clicou em 'Autos'")
    except Exception as e:
        print("❌ Não encontrou o botão Autos:", e)
        return

    sleep(2)

    # Dropdown de estado
    dropdown = wait.until(EC.presence_of_element_located((By.ID, "location-selector")))
    select = Select(dropdown)
    select.select_by_value(estado_value)
    print(f"✅ Estado selecionado: {estado_value.upper()}")

    sleep(1)

    # Botão "Buscar"
    botao_buscar = wait.until(EC.element_to_be_clickable((By.ID, "search-bar-search-button")))
    botao_buscar.click()
    print("🔍 Clicou no botão Buscar")

    sleep(3)


def extrair_dados(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    anuncios = soup.find_all('a', {'data-testid': 'adcard-link'})

    dados_extraidos = []

    for anuncio in anuncios:
        titulo = anuncio.get('title', '').strip()

        detalhes = anuncio.find_all('div', class_='olx-adcard__detail')
        km = ''
        cor = ''
        for detalhe in detalhes:
            info = detalhe.get('aria-label', '')
            if 'quilômetro' in info:
                km = ''.join(filter(str.isdigit, info)) + ' km'
            elif 'Cor' in info:
                cor = info.replace('Cor ', '').strip()

        # 🟡 Preço
        preco_tag = anuncio.find('h3', class_='olx-adcard__price')
        preco = preco_tag.get_text(strip=True) if preco_tag else ''

        # 🟡 Localização
        local_tag = anuncio.find('p', class_='olx-adcard__location')
        local = local_tag.get_text(strip=True) if local_tag else ''

        dados_extraidos.append({
            'titulo': titulo,
            'km': km,
            'cor': cor,
            'preco': preco,
            'local': local
        })

    print("\n📦 Anúncios encontrados:")
    for d in dados_extraidos:
        print(f"- {d['titulo']} | {d['km']} | {d['cor']} | {d['preco']} | {d['local']}")

    return dados_extraidos




def main():
    estados = [
        "ac", "al", "ap", "am", "ba", "ce", "df", "es", "go", "ma", "mt", "ms",
        "mg", "pa", "pb", "pr", "pe", "pi", "rj", "rn", "rs", "ro", "rr", "sc",
        "sp", "se", "to"
    ]

    driver = configurar_driver()
    todos_os_dados = []

    for estado in estados:
        print(f"\n🚗 Coletando dados do estado: {estado.upper()}")
        driver.get("https://www.olx.com.br/")

        try:
            selecionar_estado_e_buscar(driver, estado)
            dados = extrair_dados(driver)
            todos_os_dados.extend(dados)
        except Exception as e:
            print(f"❌ Falha ao processar {estado.upper()}: {e}")

    driver.quit()

    # Exibe ou salva os dados
    for item in todos_os_dados:
        print(item)

if __name__ == "__main__":
    main()
