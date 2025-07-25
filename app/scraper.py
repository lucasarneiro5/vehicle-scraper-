from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import os
import mysql.connector

#driver_path = "driver/chromedriver"  # ou chromedriver.exe no Windows
#service = Service(driver_path)
#driver = webdriver.Chrome(service=service)


def configurar_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    return webdriver.Chrome(options=options)
    

def aceitar_cookies(driver):
    try:
        botao = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "adopt-accept-all-button"))
        )
        botao.click()
    except TimeoutException:
        pass

def selecionar_estado_e_buscar(driver, estado_value):
    wait = WebDriverWait(driver, 10)

    try:
        autos = wait.until(EC.element_to_be_clickable((By.XPATH, '//p[text()="Autos"]')))
        autos.click()
        print("🚘 Clicou em 'Autos'")
    except Exception as e:
        print("❌ Não encontrou o botão Autos:", e)
        return

    time.sleep(3)

    dropdown = wait.until(EC.presence_of_element_located((By.ID, "location-selector")))
    select = Select(dropdown)
    select.select_by_value(estado_value)
    print(f"✅ Estado selecionado: {estado_value.upper()}")

    time.sleep(2)

    aceitar_cookies(driver)

    try:
        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "search-bar-search-button"))
        )
        botao.click()
        print("[✔] Botão 'Buscar' clicado com sucesso.")
    except Exception as e:
        print(f"[!] Erro ao clicar no botão 'Buscar': {e}")

    time.sleep(3)

def extrair_dados(driver, estado):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    anuncios = soup.find_all('section', class_='olx-adcard')
    dados = []

    for anuncio in anuncios:
        # Título
        titulo_tag = anuncio.find('h2', class_='olx-adcard__title')
        titulo = titulo_tag.text.strip() if titulo_tag else None


        # Quilometragem
        km_tag = anuncio.find('div', class_='olx-adcard__detail')
        km = km_tag.text.strip() if km_tag else None

        # Preço
        preco_tag = anuncio.find('h3', class_='olx-adcard__price')
        preco = preco_tag.text.strip() if preco_tag else None

        dados.append({
            'titulo': titulo,
            'km': km,
            'preco': preco,
            'estado': estado
        })

    return dados


def salvar_no_mysql(dados):
    conexao = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(255),
            km VARCHAR(255),
            preco VARCHAR(255),
            estado VARCHAR(2)
        )
    """)

    for item in dados:
        cursor.execute("""
            INSERT INTO veiculos (titulo, km, preco, estado)
            VALUES (%s, %s, %s, %s)
        """, (item['titulo'], item['km'], item['preco'], item['estado']))

    conexao.commit()
    cursor.close()
    conexao.close()



def main():
    estados = ["ac"]

    driver = configurar_driver()

    for estado in estados:
        print(f"\n🚗 Coletando dados do estado: {estado.upper()}")
        driver.get("https://www.olx.com.br/")
        aceitar_cookies(driver)
        selecionar_estado_e_buscar(driver, estado)
        time.sleep(3)

        todos_os_dados = []
        pagina = 1

        while True:
            print(f"📄 Coletando página {pagina}")
            dados = extrair_dados(driver)
            if not dados:
                print("⚠️ Nenhum dado encontrado. Encerrando.")
                break

            todos_os_dados.extend(dados)

            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.75);")
                time.sleep(2)

                proxima_pagina = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Próxima página")]'))
                )

                proxima_href = proxima_pagina.get_attribute("href")
                print(f"➡️ Indo para a próxima página: {proxima_href}")
                driver.get(proxima_href)
                time.sleep(3)
                pagina += 1
            except:
                print("🔚 Fim da paginação.")
                break

        driver.quit()

        df = pd.DataFrame(todos_os_dados)
        print(df.head())

        salvar_no_mysql(todos_os_dados)
        print(f"💾 {len(todos_os_dados)} registros salvos no banco para o estado {estado.upper()}")



if __name__ == "__main__":
    main()
