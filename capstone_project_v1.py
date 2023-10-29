import os
import sqlite3
import csv
import json
from datetime import datetime



class Contact:
    def __init__(self, first_name, last_name, phone, email, created_at=None, last_modified=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.created_at = current_time if not created_at else created_at
        self.last_modified = current_time

class FileManager:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self._create_folder_if_not_exists()

    def _create_folder_if_not_exists(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def save(self, data):
        pass

    def load(self):
        pass

class SQLManager(FileManager):

    def __init__(self, folder_path):
        super().__init__(folder_path)
        self.conn = sqlite3.connect(f"{folder_path}/contacts.db")
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                email TEXT,
                created_at TEXT,
                last_modified TEXT
            )
        """)
        self.conn.commit()

    def save(self, contact):
        self.cursor.execute("""
            INSERT INTO contacts VALUES (?, ?, ?, ?, ?, ?)
        """, (contact.first_name, contact.last_name, contact.phone, contact.email, contact.created_at, contact.last_modified))
        self.conn.commit()

    def delete(self, contact):
        self.cursor.execute("""
            DELETE FROM contacts
            WHERE first_name = ? AND last_name = ? AND email = ?
        """, (contact.first_name, contact.last_name, contact.email))
        self.conn.commit()

    def list_contacts(self):
        self.cursor.execute("SELECT * FROM contacts")
        return self.cursor.fetchall()

    def edit_contact(self, old_contact, new_contact):
        self.cursor.execute("""
            UPDATE contacts
            SET first_name = ?, last_name = ?, phone = ?, email = ?, last_modified = ?
            WHERE first_name = ? AND last_name = ? AND email = ?
        """, (
            new_contact.first_name, new_contact.last_name, new_contact.phone, new_contact.email, new_contact.last_modified,
            old_contact.first_name, old_contact.last_name, old_contact.email
        ))
        self.conn.commit()

    def load(self):
        self.cursor.execute("SELECT * FROM contacts")
        return self.cursor.fetchall()
    
    def search(self, term):
        self.cursor.execute("SELECT * FROM contacts WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?", ('%' + term + '%', '%' + term + '%', '%' + term + '%'))
        return self.cursor.fetchall()



class CSVManager(FileManager):

    def __init__(self, folder_path):
        super().__init__(folder_path)
        self.file_path = f"{folder_path}/contacts.csv"
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["first_name", "last_name", "phone", "email", "created_at", "last_modified"])

    def save(self, contact):
        with open(f"{self.folder_path}/contacts.csv", "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([contact.first_name, contact.last_name, contact.phone, contact.email, contact.created_at, contact.last_modified])

    def list_contacts(self):
        with open(self.file_path, "r") as file:
            reader = csv.reader(file)
            return list(reader)[1:]  

    def load(self):
        with open(f"{self.folder_path}/contacts.csv", "r") as file:
            reader = csv.reader(file)
            return list(reader)
    
    
    def delete(self, contact):
        rows = self.load()
        rows = [row for row in rows if not (row[0] == contact.first_name and row[1] == contact.last_name and row[3] == contact.email)]
        with open(f"{self.folder_path}/contacts.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    
    def edit_contact(self, old_contact, new_contact):
        rows = self.load()
        updated_rows = []
        for row in rows:
            if row[0] == old_contact.first_name and row[1] == old_contact.last_name and row[3] == old_contact.email:
                updated_rows.append([new_contact.first_name, new_contact.last_name, new_contact.phone, new_contact.email, new_contact.created_at, new_contact.last_modified])
            else:
                updated_rows.append(row)
        with open(self.file_path, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

    def search(self, term):
        results = []
        with open(f"{self.folder_path}/contacts.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if term.lower() in row[0].lower() or term.lower() in row[1].lower() or term.lower() in row[3].lower():
                    results.append(row)
        return results

        
class JSONManager(FileManager):

    def __init__(self, folder_path):
        super().__init__(folder_path)
        self.file_path = f"{folder_path}/contacts.json"
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump([], file)  

    def save(self, contact):
        data = {
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "phone": contact.phone,
            "email": contact.email,
            "created_at": contact.created_at,
            "last_modified": contact.last_modified
        }
        with open(self.file_path, "r") as file:
            contacts_list = json.load(file)

        contacts_list.append(data)

        with open(self.file_path, "w") as file:
            json.dump(contacts_list, file)
    
    def delete(self, contact):
        contacts = self.load()
        contacts = [c for c in contacts if not (c['first_name'] == contact.first_name and c['last_name'] == contact.last_name and c['email'] == contact.email)]
        with open(f"{self.folder_path}/contacts.json", "w") as file:
            json.dump(contacts, file)

    def list_contacts(self):
        with open(self.file_path, "r") as file:
            return json.load(file)

    def edit_contact(self, old_contact, new_contact):
        contacts = self.load()
        updated_contacts = []
        for contact in contacts:
            if contact['first_name'] == old_contact.first_name and contact['last_name'] == old_contact.last_name and contact['email'] == old_contact.email:
                updated_contact = {
                    "first_name": new_contact.first_name,
                    "last_name": new_contact.last_name,
                    "phone": new_contact.phone,
                    "email": new_contact.email,
                    "created_at": contact['created_at'],  
                    "last_modified": new_contact.last_modified
                }
                updated_contacts.append(updated_contact)
            else:
                updated_contacts.append(contact)
        with open(self.file_path, "w") as file:
            json.dump(updated_contacts, file)

    def load(self):
        with open(f"{self.folder_path}/contacts.json", "r") as file:
            return json.load(file)
    
    def search(self, term):
        results = []
        with open(f"{self.folder_path}/contacts.json", "r") as file:
            data = json.load(file)
            for contact in data:
                if term.lower() in contact["first_name"].lower() or term.lower() in contact["last_name"].lower() or term.lower() in contact["email"].lower():
                    results.append(contact)
        return results

        
class IsmetifyManager(FileManager):

    def __init__(self, folder_path):
        super().__init__(folder_path)
        self.file_path = f"{folder_path}/contacts.ismetify"
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                pass  

    def save(self, contact):
        with open(f"{self.folder_path}/contacts.ismetify", "a") as file:
            file.write(f"{contact.first_name}|{contact.last_name}|{contact.phone}|{contact.email}|{contact.created_at}|{contact.last_modified}\n")

    def delete(self, contact):
        lines = self.load()
        lines = [line for line in lines if not (line[0] == contact.first_name and line[1] == contact.last_name and line[3] == contact.email)]
        with open(f"{self.folder_path}/contacts.ismetify", "w") as file:
            for line in lines:
                file.write("|".join(line) + '\n')

    def list_contacts(self):
        with open(self.file_path, "r") as file:
            return [line.strip().split("|") for line in file.readlines()]

    def edit_contact(self, old_contact, new_contact):
        lines = self.load()
        updated_lines = []
        for line in lines:
            if line[0] == old_contact.first_name and line[1] == old_contact.last_name and line[3] == old_contact.email:
                updated_line = [new_contact.first_name, new_contact.last_name, new_contact.phone, new_contact.email, new_contact.created_at, new_contact.last_modified]
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)
        with open(self.file_path, "w") as file:
            for line in updated_lines:
                file.write("|".join(line) + '\n')

    def load(self):
        with open(f"{self.folder_path}/contacts.ismetify", "r") as file:
            return [line.strip().split("|") for line in file.readlines()]
    
    def search(self, term):
        results = []
        with open(f"{self.folder_path}/contacts.ismetify", "r") as file:
            lines = file.readlines()
            for line in lines:
                if term.lower() in line.split('|')[0].lower() or term.lower() in line.split('|')[1].lower() or term.lower() in line.split('|')[3].lower():
                    results.append(line.strip().split("|"))
        return results

        

sql_manager = SQLManager("sql_folder")
csv_manager = CSVManager("csv_folder")
json_manager = JSONManager("json_folder")
ismetify_manager = IsmetifyManager("ismetify_folder")

managers = [sql_manager, csv_manager, json_manager, ismetify_manager]


def main_menu():
    menu_options = [
        "Kişi Ekle",
        "Kişi Sil",
        "Kişileri Listele",
        "Kişi Düzenle",
        "Yedekten Geri Yükle",
        "Çıkış"
    ]

    while True:
        print("Ana Menü")
        for idx, option in enumerate(menu_options, 1):
            print(f"{idx}. {option}")

        try:
            choice = int(input("Seçiminizi yapınız (1-6): "))

            if choice == 1:
                add_contact()
            elif choice == 2:
                delete_contact()
            elif choice == 3:
                list_contacts()
            elif choice == 4:
                edit_contact()
            elif choice == 5:
                restore_from_backup()
            elif choice == 6:
                print("Tekrardan bekleriz!!")
                quit()
            else:
                print("Lütfen 1-6 arasında bir seçenek girin.")
        except ValueError:
            print("Lütfen geçerli bir numara girin.")



def add_contact():
    first_name = input("İsim: ")
    last_name = input("Soyisim: ")
    phone = input("Telefon: ")
    email = input("Email: ")

    contact = Contact(first_name, last_name, phone, email)
    for manager in managers:
        manager.save(contact) 

def delete_contact():
    term = input("Silinecek kişinin ismi veya soyismi: ")
    
    found = False
    for manager in managers:
        results = manager.search(term)
        if results:
            contact_data = results[0]
            contact_to_delete = Contact(contact_data[0], contact_data[1], contact_data[2], contact_data[3])

            
            confirmation = input(f"{contact_to_delete.first_name} {contact_to_delete.last_name} adlı kişiyi silmek istediğinize emin misiniz? (Evet/Hayır): ").lower()
            if confirmation == 'evet':
                manager.delete(contact_to_delete)
                print("Kişi başarıyla silindi!")
                found = True
                break  
            else:
                print("Silme işlemi iptal edildi.")
                return

    if not found:
        print("Aradığınız isimde bir kişi bulunamadı.")


def list_contacts():
    term = input("Aranacak terimi girin (ad, soyad veya email): ")

    
    for manager in managers:
        results = manager.search(term)
        if results:
            print(f"{type(manager).__name__} kaynaklı sonuçlar:")
            for contact in results:
                if isinstance(manager, SQLManager) or isinstance(manager, CSVManager):
                    print(f"Ad: {contact[0]}, Soyad: {contact[1]}, Telefon: {contact[2]}, Email: {contact[3]}")
                elif isinstance(manager, JSONManager):
                    print(f"Ad: {contact['first_name']}, Soyad: {contact['last_name']}, Telefon: {contact['phone']}, Email: {contact['email']}")
                elif isinstance(manager, IsmetifyManager):
                    print(f"Ad: {contact[0]}, Soyad: {contact[1]}, Telefon: {contact[2]}, Email: {contact[3]}")
            break  
    else:
        print(f"'{term}' terimi için hiçbir sonuç bulunamadı.")

def edit_contact():
    term = input("Düzenlenecek kişinin adını, soyadını veya email'ini girin: ")

    old_contact = None
    for manager in managers:
        results = manager.search(term)
        if results:
            
            old_contact = results[0]
            break
    
    if old_contact is None:
        print(f"'{term}' terimi için hiçbir sonuç bulunamadı.")
        return

    print("Yeni bilgileri girin (boş bırakırsanız, eski bilgi korunur):")
    first_name = input(f"Yeni İsim [{old_contact[0]}]: ") or old_contact[0]
    last_name = input(f"Yeni Soyisim [{old_contact[1]}]: ") or old_contact[1]
    phone = input(f"Yeni Telefon [{old_contact[2]}]: ") or old_contact[2]
    email = input(f"Yeni Email [{old_contact[3]}]: ") or old_contact[3]

    new_contact = Contact(first_name, last_name, phone, email, created_at=old_contact[4], last_modified=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    for manager in managers:
        manager.edit_contact(old_contact, new_contact)

    print("Kişi bilgileri başarıyla güncellendi.")


def restore_from_backup():
    master_data = set()  

    def create_key(contact):
        return (contact[0], contact[1], contact[2], contact[3])

    def contact_to_tuple(contact):
        if isinstance(contact, dict):
            return (contact['first_name'], contact['last_name'], contact['phone'], contact['email'])
        elif isinstance(contact, tuple) or isinstance(contact, list):
            return tuple(contact)
        else:
            raise ValueError(f"Unsupported contact type: {type(contact)}")

    for manager in managers:
        contacts = manager.load()
        for contact in contacts:
            master_data.add(create_key(contact_to_tuple(contact)))

    for manager in managers:
        current_data = set(create_key(contact_to_tuple(contact)) for contact in manager.load())
        missing_data = master_data - current_data

        for missing_contact in missing_data:
            contact = Contact(*missing_contact)  
            try:
                manager.save(contact)
            except Exception as e:
                print(f"Failed to save contact: {missing_contact}, error: {e}")

    print("Veriler başarıyla geri yüklendi ve senkronize edildi.")



if __name__ == "__main__":
    while True:
        main_menu()
