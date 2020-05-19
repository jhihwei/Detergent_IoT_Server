# 增加系統路徑---------------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
libs_dir_path = parent_dir_path+'/libs'
sys.path.insert(0, libs_dir_path)
# --------------------------------------
# Dot ENV 預載模組-----------------------
from struct import *
from dotenv import load_dotenv
from ast import literal_eval
load_dotenv()
#---------------------------------------
import paho.mqtt.client as mqtt
from datetime import datetime
import psycopg2
import random
import time
import json
from pandas.core.frame import DataFrame

class Sales():

    def __init__(self):    
        self.conn = psycopg2.connect(database=str(os.getenv('DB')), user=str(os.getenv('DB_ACC')),
                                password=str(os.getenv('DB_PWD')), host=str(os.getenv('SERVER_IP')), port=str(os.getenv('DB_PORT')))
        print("Opened database successfully")
        self.cur = self.conn.cursor()

        self.MQTT_TOPIC = [literal_eval(i.strip()) for i in os.getenv('TOPIC').split('|')]
        client_uniq = "pubclient_"+str(random.randint(1, 1000))
        self.mqttclient = mqtt.Client(client_uniq, False)  # nocleanstart
        self.mqttclient.connect(os.getenv('SERVER_IP'), 1883, 60)
        self.mqttclient.on_message = self.on_message
        self.mqttclient.on_connect = self.on_connect
        self.mqttclient.subscribe(self.MQTT_TOPIC)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            global Connected  # Use global variable
            Connected = True  # Signal connection
        else:
            print("Connection failed")


    def on_message(self, client, userdata, message):
        #將byte轉換成json
        data = json.loads(message.payload)
        sales_data = data['value'].split(',')[:-1]
        terminal_id = data['terminal_id']
        try:
            total_flow, gross_income, flow, income, receipt = self.extract_data(sales_data)
            print(total_flow, gross_income, flow, income, receipt)
            self.cur.execute(f"INSERT INTO sales (total_flow, gross_income, flow, income, receipt, terminal_id) \
                    VALUES ({total_flow}, {gross_income}, {flow}, {income}, {receipt}, '{terminal_id}')")
            self.conn.commit()
        except Exception as e:
            print(e)


    def extract_data(self, d):
        total_flow = f'{self.fix_number(d[5])}{self.fix_number(d[4])}{self.fix_number(d[3])}{self.fix_number(d[2])}{self.fix_number(d[1])}'
        gross_income = f'{self.fix_number(d[10])}{self.fix_number(d[9])}{self.fix_number(d[8])}{self.fix_number(d[7])}{self.fix_number(d[6])}'
        flow = f'{self.fix_number(d[15])}{self.fix_number(d[14])}{self.fix_number(d[13])}{self.fix_number(d[12])}{self.fix_number(d[11])}'
        income = f'{self.fix_number(d[20])}{self.fix_number(d[19])}{self.fix_number(d[18])}{self.fix_number(d[17])}{self.fix_number(d[16])}'
        receipt = f'{self.fix_number(d[25])}{self.fix_number(d[24])}{self.fix_number(d[23])}{self.fix_number(d[22])}{self.fix_number(d[21])}'

        return int(total_flow), int(gross_income), int(flow), int(income), int(receipt)

    def fix_number(self, number):
        number = int(number, 16)
        if number == 0:
            return '00'
        elif number < 10:
            return f'0{number}'
        else:
            return number

    def start(self):
        pass

if __name__ == '__main__':
    salse = Sales()
    salse.mqttclient.loop_forever()
