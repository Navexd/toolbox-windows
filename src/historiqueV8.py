from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QApplication, QFileDialog, QMenu
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QClipboard

class HistoriqueWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Label pour l'historique des mots de passe
        history_label = QLabel("Historique des Mots de Passe")
        history_label.setStyleSheet("color: #ecf0f1; font-size: 16px;")

        # Message par défaut pour l'historique vide
        self.default_message_label = QLabel("Aucun mot généré pour le moment")
        self.default_message_label.setStyleSheet("color: #ecf0f1; font-size: 14px;")
        self.default_message_label.setAlignment(Qt.AlignCenter)

        # Liste pour afficher l'historique des mots de passe
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
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
                margin: 10px 20px;
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
        # Label de confirmation pour les copies
        self.copy_confirmation_label = QLabel("")
        self.copy_confirmation_label.setStyleSheet("color: #dc7b6a; font-size: 12px;")
        self.copy_confirmation_label.setAlignment(Qt.AlignCenter)
        self.copy_confirmation_label.setVisible(False)

        # Bouton pour exporter l'historique
        self.export_button = QPushButton("Exporter")
        self.export_button.setStyleSheet("background-color: #B08F12; color: #1e1e2e; font-size: 14px;")
        self.export_button.setEnabled(False)  # Désactiver initialement
        self.export_button.clicked.connect(self.export_history)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)

        layout.addWidget(history_label)
        layout.addWidget(self.default_message_label)
        layout.addWidget(self.history_list)
        layout.addWidget(self.copy_confirmation_label)  # Ajouter le label de confirmation
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Ajout d'un menu contextuel pour la copie
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)

    def add_password_to_history(self, password):
        """Ajoute un mot de passe à l'historique."""
        if self.history_list.count() == 0:
            self.default_message_label.setVisible(False)
        item = QListWidgetItem(password)
        self.history_list.addItem(item)
        self.update_export_button_state()

    def copy_selected_password(self):
        """Copie le mot de passe sélectionné dans le presse-papier."""
        selected_item = self.history_list.currentItem()
        if selected_item:
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_item.text())
            self.show_copy_confirmation()

    def export_history(self):
        """Exporte l'historique dans un fichier texte."""
        if self.history_list.count() == 0:
            self.copy_confirmation_label.setText("Historique vide, rien à exporter.")
            self.copy_confirmation_label.setStyleSheet("color: red; font-size: 12px;")
            self.copy_confirmation_label.setVisible(True)
            QTimer.singleShot(2000, self.hide_copy_confirmation)
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter l'Historique", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w') as file:
                for index in range(self.history_list.count()):
                    file.write(self.history_list.item(index).text() + "\n")
            self.copy_confirmation_label.setText("Historique exporté avec succès !")
            self.copy_confirmation_label.setStyleSheet("color: #dc7b6a; font-size: 12px;")
            self.copy_confirmation_label.setVisible(True)
            QTimer.singleShot(2000, self.hide_copy_confirmation)

    def show_context_menu(self, position):
        """Affiche un menu contextuel avec l'option de copie."""
        context_menu = QMenu()
        copy_action = context_menu.addAction("Copier")
        action = context_menu.exec_(self.history_list.viewport().mapToGlobal(position))
        if action == copy_action:
            self.copy_selected_password()

    def show_copy_confirmation(self):
        """Affiche une confirmation après une copie."""
        self.copy_confirmation_label.setText("Mot de passe copié dans le presse-papier.")
        self.copy_confirmation_label.setStyleSheet("color: #dc7b6a; font-size: 12px;")
        self.copy_confirmation_label.setVisible(True)
        QTimer.singleShot(2000, self.hide_copy_confirmation)

    def hide_copy_confirmation(self):
        """Cache le message de confirmation."""
        self.copy_confirmation_label.setVisible(False)

    def update_export_button_state(self):
        """Active ou désactive le bouton Exporter selon l'état de l'historique."""
        self.export_button.setEnabled(self.history_list.count() > 0)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = HistoriqueWidget()
    window.show()
    sys.exit(app.exec())
