from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import math


def solicitar_porcentagens(num_alternativas):
    while True:
        porcentagens = []
        soma_porcentagens = 0
        for i in range(num_alternativas):
            while True:
                try:
                    porcentagem = float(input(f"Digite a porcentagem para a alternativa {i + 1}: "))
                    if 0 <= porcentagem <= 100:
                        porcentagens.append(porcentagem)
                        soma_porcentagens += porcentagem
                        break
                    else:
                        print("Porcentagem deve estar entre 0 e 100. Tente novamente.")
                except ValueError:
                    print("Por favor, insira um valor numérico válido.")
        if soma_porcentagens == 100:
            return porcentagens
        else:
            print("Erro: A soma das porcentagens não é igual a 100%. Por favor, tente novamente.")


def calcular_respostas_misturadas(porcentagens, numero_respostas):
    respostas_misturadas = []
    for i, porcentagem in enumerate(porcentagens):
        quantidade = math.floor((porcentagem / 100) * numero_respostas)
        respostas_misturadas.extend([i] * quantidade)
    while len(respostas_misturadas) < numero_respostas:
        for i in range(len(porcentagens)):
            if len(respostas_misturadas) < numero_respostas:
                respostas_misturadas.append(i)
            else:
                break
    random.shuffle(respostas_misturadas)
    return respostas_misturadas


def clicar_elemento_com_js(driver, elemento):
    driver.execute_script("arguments[0].scrollIntoView();", elemento)  # Scroll até o elemento
    driver.execute_script("arguments[0].click();", elemento)  # Clique via JavaScript


numero_respostas = int(input("Quantas respostas você quer enviar? "))
driver = webdriver.Chrome()
form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeZt8GU4jVOe-XP-eCgPSJqbO6DZNhzfAIiGC-uh8jsFKlfuQ/viewform'

try:
    driver.get(form_url)
    time.sleep(2)
    perguntas = driver.find_elements(By.CLASS_NAME, "geS5n")
    todas_respostas_misturadas = []
    for index, pergunta in enumerate(perguntas):
        alternativas = pergunta.find_elements(By.CLASS_NAME, "ulDsOb")
        if alternativas:
            porcentagens = solicitar_porcentagens(len(alternativas))
            respostas_misturadas = calcular_respostas_misturadas(porcentagens, numero_respostas)
            todas_respostas_misturadas.append(respostas_misturadas)

    for resposta_count in range(numero_respostas):
        print(f'\nEnviando resposta {resposta_count + 1}/{numero_respostas}...\n')
        driver.get(form_url)
        time.sleep(2)

        perguntas = driver.find_elements(By.CLASS_NAME, "geS5n")
        for index, pergunta in enumerate(perguntas):
            alternativas = pergunta.find_elements(By.CLASS_NAME, "ulDsOb")
            if alternativas:
                escolha_alternativa = todas_respostas_misturadas[index][resposta_count]
                alternativa_escolhida = alternativas[escolha_alternativa]

                # Tenta clicar usando JavaScript caso o clique normal falhe
                try:
                    alternativa_escolhida.find_element(By.XPATH, './/span').click()
                except:
                    print(f"Elemento bloqueado para clique normal, usando JavaScript para clicar na alternativa {escolha_alternativa + 1}")
                    clicar_elemento_com_js(driver, alternativa_escolhida.find_element(By.XPATH, './/span'))

        # Aguarda o botão de envio e clica nele
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "uArJ5e.UQuaGc.Y5sE8d.VkkpIf.QvWxOd"))).click()
        time.sleep(2)

        # Tenta clicar no botão "Enviar outra resposta"
        try:
            link_enviar_outra_resposta = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='c2gzEf']/a[contains(@href, 'form_confirm')]")))
            link_enviar_outra_resposta.click()
        except:
            print("Botão 'Enviar outra resposta' não encontrado, recarregando o formulário...")
            driver.get(form_url)
            time.sleep(2)

finally:
    print("Fechando o navegador...")
    driver.quit()
