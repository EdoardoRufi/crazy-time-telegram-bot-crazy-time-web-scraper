import os
import sys
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import paho.mqtt.client as mqtt


from selenium.webdriver.support.wait import WebDriverWait


# Funzione per ottenere l'URL dell'immagine dal tag HTML dell'immagine
def get_image_url(img_tag):
    if img_tag is None:
        return None
    return img_tag['src']


class Extraction:
    def __init__(self, bonus, date_time, multipliers):
        self._bonus = bonus
        self._date_time = date_time
        self._multipliers = multipliers

    def __init__(self):
        pass


def printExtraction(extraction_vo):
    # print the last extracted 
    print('Last bonus extracted: ' + extraction_vo.bonus + ' at ' +
          extraction_vo.date_time + '. Multipliers: ' + extraction_vo.multipliers)


def publishToMqtt(extraction_vo):
    # MQTT broker configuration
    broker = 'localhost'  # Update with the IP or hostname of your MQTT broker
    port = 1883  # MQTT broker port
    topic = 'Extractions'  # MQTT topic to publish to

    # Convert JSON data to a string
    message = json.dumps(extraction_vo.__dict__)

    # Create an MQTT client
    client = mqtt.Client()

    # Connect to the MQTT broker
    client.connect(broker, port)

    # Publish the message to the MQTT topic
    client.publish(topic, message)

    # Disconnect from the MQTT broker
    client.disconnect()

def get_full_date(input_time):
    # Get today's date
    today = datetime.today().date()

    # Convert the input time to datetime object
    time_obj = datetime.strptime(input_time, "%H:%M")

    # Combine today's date with the given time
    combined_datetime = datetime.combine(today, time_obj.time())

    # Return the combined datetime in ISO format
    return combined_datetime.isoformat()


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

        # Iniztialization of result object
        last_extraction_vo = Extraction()

        # Find the table element
        table = soup.find('table', id='spinHistoryTableCrazyTime', class_='table')

        # Find the rows within the table
        row = table.findAll('tr')[1]

        # LAST BONUS EXTRACTED
        td_last_spin = row.find('img', attrs={'alt': 'Spin Result'})
        png_last_spin = td_last_spin['src']
        last_extraction_vo.bonus = risultati.get(png_last_spin)

        # DATE_TIME LAST BONUS EXTRACTED
        last_spin_result_time = row.find('p', class_='dateTime_DateTime__time__HZhlD').text.strip()
        last_extraction_vo.date_time = get_full_date(last_spin_result_time)
        # Extract the time from the td element

        # LAST BONUS MULTIPLIERS valorize the json here
        column = row.findAll('td')[4]
        last_extraction_vo.multipliers = column.text.strip()

        if time_last_result_found == last_spin_result_time:
            print("Nothing new found")
        else:
            # send result object to mqtt
            publishToMqtt(last_extraction_vo)
            printExtraction(last_extraction_vo)
            time_last_result_found = last_spin_result_time

    except Exception as e:
        print(f"Si è verificato un errore: {str(e)}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    # Attendi 5 secondi prima di ripetere l'azione
    time.sleep(20)
