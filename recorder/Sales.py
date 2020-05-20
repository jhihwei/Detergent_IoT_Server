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
from Data_Format import Data_Format

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
        timestamp = data['time']
        try:
            d_format = Data_Format()
            total_flow, gross_income, flow, income, receipt = d_format.extract_data(sales_data)
            print(total_flow, gross_income, flow, income, receipt)
            self.cur.execute(f"INSERT INTO sales (total_flow, gross_income, flow, income, receipt, terminal_id, timestamp) \
                    VALUES ({total_flow}, {gross_income}, {flow}, {income}, {receipt}, '{terminal_id}', '{timestamp}')")
            self.conn.commit()
        except Exception as e:
            print(e)

    def start(self):
        pass

if __name__ == '__main__':
    salse = Sales()
    salse.mqttclient.loop_forever()
