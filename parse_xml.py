import csv
import unittest
import requests
import zipfile
import xml.etree.ElementTree as ET
import logging
import os
import pandas as pd


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.url = 'https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100'
        self.file_type = 'DLTINS'
        self.zip_name = 'DLTINS.zip'
        self.xml_name = 'DLTINS.xml'
        self.csv_name = 'DLTINS.csv'

    def test_download_xml(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
        root = ET.fromstring(response.content)
        download_link = None
        for doc in root.iter('doc'):
            file_type = doc.find(".//str[@name='file_type']")
            if file_type is not None and file_type.text == self.file_type:
                download_link = doc.find(".//str[@name='download_link']")
                break
        self.assertIsNotNone(download_link)
        zip_url = download_link.text
        response = requests.get(zip_url)
        self.assertEqual(response.status_code, 200)
        with open(self.zip_name, 'wb') as f:
            f.write(response.content)
        self.assertTrue(os.path.isfile(self.zip_name))

    def test_extract_xml(self):
        with zipfile.ZipFile(self.zip_name, 'r') as zip_ref:
            zip_ref.extractall('.')
        self.assertTrue(os.path.isfile(self.xml_name))

    def test_xml_to_csv(self):
        # Load the XML file
        tree = ET.parse('DLTINS_20210117_01of01.xml')
        
        root = tree.getroot()
        data = [['FinInstrmGnlAttrbts.Id', 'FinInstrmGnlAttrbts.FullNm', 'FinInstrmGnlAttrbts.ClssfctnTp', 'FinInstrmGnlAttrbts.CmmdtyDerivInd', 'FinInstrmGnlAttrbts.NtnlCcy', 'Issr']]
        for child in root:
            row = []
            for elem in child.iter():
                if elem.tag == 'FinInstrmGnlAttrbts.Id':
                    row.append(elem.text)
                elif elem.tag == 'FinInstrmGnlAttrbts.FullNm':
                    row.append(elem.text)
                elif elem.tag == 'FinInstrmGnlAttrbts.ClssfctnTp':
                    row.append(elem.text)
                elif elem.tag == 'FinInstrmGnlAttrbts.CmmdtyDerivInd':
                    row.append(elem.text)
                elif elem.tag == 'FinInstrmGnlAttrbts.NtnlCcy':
                    row.append(elem.text)
                elif elem.tag == 'Issr':
                    row.append(elem.text)
                if row:
                    data.append(row)
        with open(self.csv_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        self.assertTrue(os.path.isfile(self.csv_name))



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()

