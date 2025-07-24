from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup

def configurar_driver():
    options = Options()
    # options.add_argument("--headless")  # Ative se quiser em segundo plano
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    return webdriver.Chrome(options=options)
    

def selecionar_estado_e_buscar(driver, estado_value):
    wait = WebDriverWait(driver, 10)

    try:
        autos = wait.until(EC.element_to_be_clickable((By.XPATH, '//p[text()="Autos"]')))
        autos.click()
        print("🚘 Clicou em 'Autos'")
    except Exception as e:
        print("❌ Não encontrou o botão Autos:", e)
        return

    sleep(3)

    dropdown = wait.until(EC.presence_of_element_located((By.ID, "location-selector")))
    select = Select(dropdown)
    select.select_by_value(estado_value)
    print(f"✅ Estado selecionado: {estado_value.upper()}")

    sleep(2)

    try:
        botao_cookies = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
        )
        botao_cookies.click()
        print("[✔] Cookies aceitos.")
    except:
        print("[!] Botão de cookies não encontrado ou já aceito.")

    try:
        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "search-bar-search-button"))
        )
        botao.click()
        print("[✔] Botão 'Buscar' clicado com sucesso.")
    except Exception as e:
        print(f"[!] Erro ao clicar no botão 'Buscar': {e}")

    sleep(3)

def extrair_dados_pagina(driver):
    sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    carros = soup.find_all('section', class_='olx-adcard olx-adcard__vertical undefined')

    dados = []
    for carro in carros:
        try:
            link_tag = carro.find('a', {'data-testid': 'adcard-link'})
            titulo = link_tag['title'].strip() if link_tag else 'N/A'
            link = link_tag['href'].strip() if link_tag else 'N/A'

            preco_tag = carro.find('h3', class_='olx-adcard__price')
            preco = preco_tag.text.strip() if preco_tag else 'N/A'

            detalhes = carro.find_all('div', class_='olx-adcard__detail')
            km = 'N/A'
            for d in detalhes:
                texto = d.get_text(strip=True)
                if 'km' in texto.lower():
                    km = texto
                    break

            dados.append({
                'Título': titulo,
                'Link': link,
                'Preço': preco,
                'KM': km
            })
        except Exception as e:
            print(f"[!] Erro ao extrair carro: {e}")
            continue

    return dados

def navegar_paginacao(driver):
    todos_dados = []
    pagina = 1

    while True:
        print(f"📄 Coletando página {pagina}")
        dados = extrair_dados_pagina(driver)
        todos_dados.extend(dados)

        try:
            botao_proxima = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@data-lurker-detail="forward_button"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView();", botao_proxima)
            botao_proxima.click()
            sleep(3)
            pagina += 1
        except:
            print("🔚 Fim da paginação")
            break

    return todos_dados

def main():
    estados = ["ac"]  # para testar, use apenas um estado

    driver = configurar_driver()

    todos_os_dados = []

    for estado in estados:
        print(f"\n🚗 Coletando dados do estado: {estado.upper()}")
        driver.get("https://www.olx.com.br/")
        selecionar_estado_e_buscar(driver, estado)
        dados_estado = navegar_paginacao(driver)
        todos_os_dados.extend(dados_estado)

    driver.quit()

    df = pd.DataFrame(todos_os_dados)
    print(df.head())
    df.to_csv("carros_olx.csv", index=False)

if __name__ == "__main__":
    main()
