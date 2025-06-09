from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QHBoxLayout, QFileDialog, QMenu,
    QDialog, QFormLayout, QGroupBox, QApplication, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from cryptography.fernet import Fernet
import json
import random
import string


class AddPasswordDialog(QDialog):
    password_generated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un nouvel élément")
        self.setFixedSize(400, 400)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: #2c2c3e; color: #ecf0f1; border-radius: 10px;")

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(15)

        input_group = QGroupBox("Informations sur le mot de passe")
        input_group.setStyleSheet(""" QGroupBox { font-size: 16px; font-weight: bold; color: #ecf0f1; margin-top: 10px; } """)

        # Champs d'entrée
        self.name_input = self.create_input_field()
        self.id_input = self.create_input_field()
        self.password_input = self.create_input_field()
        self.url_input = self.create_input_field()
        self.notes_input = self.create_input_field()

        # Ajouter les champs au formulaire
        form_layout.addRow("Nom :", self.name_input)
        form_layout.addRow("ID :", self.id_input)
        form_layout.addRow("Mot de passe :", self.password_input)
        form_layout.addRow("URL :", self.url_input)
        form_layout.addRow("Notes :", self.notes_input)

        input_group.setLayout(form_layout)

        # Boutons
        self.generate_password_button = self.create_button("Générer mot de passe", self.generate_password)
        self.add_button = self.create_button("Ajouter", self.accept)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addWidget(self.generate_password_button)
        button_layout.addWidget(self.add_button)

        main_layout.addWidget(input_group)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_input_field(self):
        field = QLineEdit()
        field.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e; 
                color: #ecf0f1; 
                border: 1px solid #B08F12; 
                border-radius: 5px; 
                padding: 5px;
            }
        """)
        return field

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #B08F12; 
                color: #1e1e2e; 
                font-size: 14px; 
                border-radius: 5px; 
                padding: 10px;
            }
            QPushButton:hover { background-color: #d4af37; }
        """)
        button.clicked.connect(callback)
        return button

    def get_details(self):
        return {
            "name": self.name_input.text(),
            "id": self.id_input.text(),
            "password": self.password_input.text(),
            "url": self.url_input.text(),
            "notes": self.notes_input.text()
        }

    def generate_password(self):
        length = 12
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        self.password_input.setText(password)
        self.password_generated.emit(password)

class ServicesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.passwords = {}
        self.load_key()  # Charger la clé avant tout
        self.setup_ui()  # Configure l'interface graphique
        self.load_passwords()  # Charger les mots de passe après l'UI

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        vault_label = QLabel("Coffre-Fort à Mots de Passe")
        vault_label.setStyleSheet("color: #ecf0f1; font-size: 18px; font-weight: bold;")

        self.password_list = QListWidget()
        self.password_list.setStyleSheet("""
                QListWidget {
                    background-color: #1e1e2e; 
                    color: #ecf0f1; 
                    border-radius: 5px;
                    padding: 10px;
                }
                QListWidget::item {
                    border: 1px solid #B08F12;
                    border-radius: 5px;
                    padding: 5px;
                    margin: 5px 20px;
                }
                QListWidget::item:selected {
                    background-color: #B08F12;
                    color: #1e1e2e;
                }
                QScrollBar:vertical {
                    background: #2c2c3e;  /* Couleur de fond */
                    width: 14px;          /* Largeur de la barre */
                    margin: 5px 5px 5px 5px; /* Marges */
                    border-radius: 7px;   /* Arrondi */
                }

                QScrollBar::handle:vertical {
                    background: #B08F12; /* Couleur du curseur */
                    border-radius: 7px;  /* Arrondi */
                    min-height: 20px;    /* Hauteur minimale du curseur */
                }

                QScrollBar::handle:vertical:hover {
                    background: #D4A017; /* Couleur au survol */
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none; /* Supprime les boutons haut/bas */
                }

                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none; /* Zones cliquables invisibles */
                }
            """)
        # Activer le menu contextuel personnalisé
        self.password_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.password_list.customContextMenuRequested.connect(self.show_context_menu)

        self.password_list.itemDoubleClicked.connect(self.edit_password)

        add_button = self.create_button("Ajouter", self.add_password)
        export_button = self.create_button("Exporter", self.export_passwords)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(export_button)

        # Ajout d'un QLabel pour afficher les messages temporaires
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: #dc7b6a; font-size: 14px; font-style: italic;")
        self.message_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(vault_label)
        layout.addWidget(self.password_list)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addWidget(self.message_label)  # Ajout du QLabel sous les boutons
        self.setLayout(layout)

    def show_context_menu(self, position):
        item = self.password_list.itemAt(position)
        if item is None:
            return  # Ne rien faire si aucun élément n'est sélectionné

        menu = QMenu(self)
        copy_action = menu.addAction("Copier le mot de passe")
        edit_action = menu.addAction("Modifier")
        delete_action = menu.addAction("Supprimer")

        action = menu.exec(self.password_list.mapToGlobal(position))
        if action == copy_action:
            self.copy_password(item)
        elif action == edit_action:
            self.edit_password(item)
        elif action == delete_action:
            self.delete_password(item)

    def copy_password(self, item):
        name = item.text()
        if name in self.passwords:
            password = self.passwords[name]["password"]
            QApplication.clipboard().setText(password)
            self.show_message("Mot de passe copié dans le presse-papiers !")

    def show_message(self, message):
        """Affiche un message temporaire dans la QLabel."""
        self.message_label.setText(message)
        QTimer.singleShot(5000, lambda: self.message_label.clear())  # Efface après 5 secondes

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet("background-color: #B08F12; color: #1e1e2e; font-size: 14px;")
        button.clicked.connect(callback)
        return button

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet("background-color: #B08F12; color: #1e1e2e; font-size: 14px;")
        button.clicked.connect(callback)
        return button

    def load_key(self):
        try:
            with open("key.key", "rb") as key_file:
                self.key = key_file.read()
        except FileNotFoundError:
            self.key = Fernet.generate_key()
            with open("key.key", "wb") as key_file:
                key_file.write(self.key)
        self.cipher = Fernet(self.key)

    def load_passwords(self):
        try:
            with open("passwords.json", "r") as file:
                data = self.cipher.decrypt(file.read().encode())
                self.passwords = json.loads(data)
        except (FileNotFoundError, json.JSONDecodeError):
            self.passwords = {}
            self.save_passwords()  # Crée un fichier JSON vide si absent ou invalide
        self.update_password_list()

    def save_passwords(self):
        try:
            encrypted_data = self.cipher.encrypt(json.dumps(self.passwords).encode())
            with open("passwords.json", "wb") as file:  # Écrire en mode binaire
                file.write(encrypted_data)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder les mots de passe : {e}")

    def add_password(self):
        dialog = AddPasswordDialog(self)
        if dialog.exec():
            details = dialog.get_details()
            if details["name"] and details["password"]:
                self.passwords[details["name"]] = details
                self.save_passwords()
                self.update_password_list()

    def edit_password(self, item):
        name = item.text()
        if name in self.passwords:
            details = self.passwords[name]
            dialog = AddPasswordDialog(self)
            dialog.name_input.setText(name)
            dialog.id_input.setText(details.get("id", ""))
            dialog.password_input.setText(details.get("password", ""))
            dialog.url_input.setText(details.get("url", ""))
            dialog.notes_input.setText(details.get("notes", ""))


            if dialog.exec():
                updated_details = dialog.get_details()
                del self.passwords[name]  # Supprimer l'ancien enregistrement
                self.passwords[updated_details["name"]] = updated_details  # Ajouter l'enregistrement mis à jour
                self.save_passwords()
                self.update_password_list()

    def delete_password(self, item):
        name = item.text()
        if name in self.passwords:
            confirm = QMessageBox.question(
                self, "Confirmation",
                f"Êtes-vous sûr de vouloir supprimer le mot de passe pour '{name}' ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                del self.passwords[name]
                self.save_passwords()
                self.update_password_list()
                QMessageBox.information(self, "Succès", f"Mot de passe pour '{name}' supprimé.")

    def update_password_list(self):
        if not hasattr(self, 'password_list'):
            print("Erreur : 'password_list' n'a pas été défini.")
            return
        self.password_list.clear()
        for name in self.passwords.keys():
            self.password_list.addItem(name)

    def export_passwords(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter les mots de passe", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, "w") as file:
                for name, details in self.passwords.items():
                    file.write(f"{name}: {details}\n")
                    self.show_message("Mot de passes exporté !")

    def closeEvent(self, event):
        self.save_passwords()
        print("Mots de passe sauvegardés avant la fermeture.")  # Pour debug
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ServicesWidget()
    window.show()
    sys.exit(app.exec())
