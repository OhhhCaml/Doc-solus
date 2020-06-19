from selenium import webdriver
from PIL import Image
from selenium.webdriver.chrome.options import Options
import numpy as np
import time
from io import BytesIO
import os


Adresse = "" #Adresse mail de connection
Password = "" #Mot de passe Doc Solus



chrome_options = Options()
chrome_options.add_argument("--kiosk") #Pour le plein écran
driver = webdriver.Chrome("chromedriver.exe",options= chrome_options)

def connection():
    driver.get("https://www.doc-solus.fr/bin/users/connexion.html")
    driver.find_element_by_id("focus").send_keys(Adresse)
    driver.find_element_by_name("passwd").send_keys(Password)
    driver.find_element_by_name("save").click()
    

def page(link):
    #Renvoie la liste des liens des différentes pages du corrigé du sujet donné en input
    driver.get(link)
    lp = []
    resultat = driver.find_elements_by_xpath("/html/body/div[3]/section[1]/a")
    for element in resultat:
        try :
            lp.append(element.get_attribute("href"))
        except:
            pass
    return(lp)

def priorité(lien):
    #Définit dans quel ordre on récupère les corrigés
    return(int(lien[-4::]) > 2015 and not("X_2" in lien))

def corrigé():
    #Ecrit dans un fichier "lien.csv" les liens des corrigés compris dans l'abonnement DOC SOLUS
    driver.get("https://www.doc-solus.fr/prepa/sci/adc/bin/favoris.html")
    with open("lien.csv",'w') as l:
        b = True
        i = 1
        while b:
            try :
            element = driver.find_element_by_css_selector("body > div.center > ul > li:nth-child("+str(i)+") > a")
            l.write(element.get_attribute("href")+","+element.text + "\n")
            i+=1
            except:
                b = False
        

def full_screenshot(driver, save_path):
    #Enregistre une capture d'écran d'une page entière et l'enregistre dans save_path
    if save_path[-4::] != ".png":
        save_path = save_path +".png"

    img_li = []
    offset = 0

    height = driver.execute_script('return Math.max('
                                   'document.documentElement.clientHeight, window.innerHeight);')

    max_window_height = driver.execute_script('return Math.max('
                                              'document.body.scrollHeight, '
                                              'document.body.offsetHeight, '
                                              'document.documentElement.clientHeight, '
                                              'document.documentElement.scrollHeight, '
                                              'document.documentElement.offsetHeight);')

    while offset < max_window_height:

        driver.execute_script(f'window.scrollTo(0, {offset});')
        img = Image.open(BytesIO((driver.get_screenshot_as_png())))
        img_li.append(img)
        offset += height

    img_frame_height = sum([img_frag.size[1] for img_frag in img_li])
    img_frame = Image.new('RGB', (img_li[0].size[0], img_frame_height))
    offset = 0
    for img_frag in img_li:
        img_frame.paste(img_frag, (0, offset))
        offset += img_frag.size[1]
    img_frame.save(save_path)

def tout_scanner():
    #Récupère l'ensemble des corrigés compris dans l'abonnement, chacun dans un fichier différent
    connection()
    déjà_récupéré = np.genfromtxt("déjà vu.txt", dtype = 'str')
    lecture = np.flip(np.genfromtxt("lien.csv", dtype = str, delimiter = ","))
    with open("déjà vu.txt","a") as out:
        time.sleep(1)
        for sujet in lecture:
            if priorité(sujet[1]) and not( sujet[0] in déjà_récupéré):
                try :
                    lp = page(sujet[1])
                    i = 0
                    if not os.path.exists(sujet[0]):
                        try:
                            os.makedirs(sujet[0])
                        except:
                            pass
                    for lien in lp:
                        driver.get(lien)
                        time.sleep(2)
                        full_screenshot(driver,sujet[0]+"/"+str(i))
                        i +=1
                    out.write(sujet[1]+"\n")
                except :
                    print(sujet[0])
                    print(sujet[1])
                

def cherche(link):
    #Récupère le nom du sujet associé à un lien
    lien2 = np.genfromtxt("lien.csv", dtype = str, delimiter = ",")
    for data in lien2:
        if data[0] == link:
            return(data[1])
    else: return("sujet")

def scanner(link):
    #Ne scanne que le sujet donné
    connection()
    lp = page(link)
    i = 0
    début = cherche(link)
    if not os.path.exists(début):
        try:
            os.makedirs(début)
        except:
            pass
    for lien in lp:
        driver.get(lien)
        time.sleep(2)
        full_screenshot(driver,début+"/"+str(i))
        i +=1

