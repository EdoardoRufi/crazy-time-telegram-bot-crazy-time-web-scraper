import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json

from selenium.webdriver.support.wait import WebDriverWait


# Funzione per ottenere l'URL dell'immagine dal tag HTML dell'immagine
def get_image_url(img_tag):
    if img_tag is None:
        return None
    return img_tag['src']


# Opzioni per il driver di Chrome
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# Variabili per l'ultimo risultato estratto
time_last_result_found = ""

while True:
    try:
        # Inizializza il driver di Chrome
        driver = webdriver.Chrome(options=chrome_options)

        # URL della pagina da analizzare
        url = 'https://casinoscores.com/crazy-time/'

        # Carica la pagina utilizzando il driver di Chrome
        driver.get(url)

        # Wait for the page to load completely
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, 'spinHistoryTableCrazyTime')))

        # Ottiene il contenuto HTML della pagina
        html_content = driver.page_source

        # Chiude il driver di Chrome
        driver.quit()

        # Analizza l'HTML della risposta
        soup = BeautifulSoup(html_content, 'html.parser')

        # Dizionario per associare le immagini ai risultati
        risultati = {
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/one-card.png': '1',
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/two-card.png': '2',
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/five-card.png': '5',
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/ten-card.png': '10',
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/coin-flip-card.png': 'Coin flip',
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/cash-hunt-card.png': 'Cash hunt',
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/pachiko-card.png': 'Pachinko',
            'https://res.cloudinary.com/casinogrounds/image/upload/f_auto,q_auto,w_0.45,c_scale/gameshows/evolution-gaming/crazy-time/crazy-time-card.png': 'Crazy Time'
        }

        # Find the table element
        table = soup.find('table', id='spinHistoryTableCrazyTime', class_='table')

        # Find the rows within the table
        rows = table.findAll('tr')

        td_last_spin = rows[1].find('img', attrs={'alt': 'Spin Result'})
        # Extract the text from the td element
        png_last_spin = td_last_spin['src']

        last_spin_result_time = rows[1].find('p', class_='dateTime_DateTime__time__HZhlD').text.strip()
        # Extract the time from the td element

        if time_last_result_found == last_spin_result_time:
            print("Still nothing new found")
        else:
            # print the last extracted
            print('Last bonus extracted: ' + risultati.get(png_last_spin) + ' at ' + last_spin_result_time)
            time_last_result_found = last_spin_result_time




    except Exception as e:
        print(f"Si è verificato un errore: {str(e)}")

    # Attendi 5 secondi prima di ripetere l'azione
    time.sleep(5)
