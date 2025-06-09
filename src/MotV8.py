from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QSlider, QProgressBar, QApplication)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal
import sys
import random
import string

class MotDePasseWidget(QWidget):
    password_generated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        length_layout = QHBoxLayout()
        length_label = QLabel("Longueur :")

        length_slider = QSlider(Qt.Horizontal)
        length_slider.setRange(6, 32)
        length_slider.setValue(12)
        length_slider.setTickPosition(QSlider.TicksBelow)
        length_slider.setTickInterval(1)
        self.length_label = QLabel(str(length_slider.value()))

        length_slider.valueChanged.connect(lambda: self.generate_password(
            length_slider, digits_checkbox, letters_checkbox, special_chars_checkbox, result_label, strength_bar,
            complexity_label
        ))
        length_slider.valueChanged.connect(self.update_length_label)
        length_layout.addWidget(length_label)
        length_layout.addWidget(length_slider)
        length_layout.addWidget(self.length_label)

        digits_checkbox = QCheckBox("Inclure des chiffres")
        digits_checkbox.setChecked(True)

        letters_checkbox = QCheckBox("Inclure des lettres")
        letters_checkbox.setChecked(True)

        special_chars_checkbox = QCheckBox("Inclure des caractères spéciaux")
        special_chars_checkbox.setChecked(True)

        generate_button = QPushButton("Générer")
        mix_button = QPushButton("Mélanger")
        copy_button = QPushButton("Copier")
        result_label = QLabel()
        complexity_label = QLabel("Complexité : ")

        # Mettre en avant le mot de passe généré
        result_label.setFont(QFont("Arial", 16, QFont.Bold))
        result_label.setStyleSheet("color: #dc7b6a ; background-color: #1e1e2e; border: 2px solid #1e1e2e ; padding: 1px;")

        # Ajouter une barre de force du mot de passe avec un dégradé de couleur minimaliste
        strength_bar = QProgressBar()
        strength_bar.setRange(0, 100)
        strength_bar.setValue(0)
        strength_bar.setTextVisible(False)
        strength_bar.setFixedHeight(10)  # Hauteur réduite pour un look minimaliste

        # Appliquer une feuille de style CSS pour le dégradé de couleur
        strength_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                background: #1e1e2e;
                height: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 red,
                    stop:0.25 orange,
                    stop:0.5 yellow,
                    stop:0.75 lightgreen,
                    stop:1 green
                );
                border-radius: 5px;
            }
        """)

        generate_button.clicked.connect(lambda: self.generate_password(length_slider, digits_checkbox, letters_checkbox, special_chars_checkbox, result_label, strength_bar, complexity_label))
        mix_button.clicked.connect(lambda: self.mix_password(result_label))
        copy_button.clicked.connect(lambda: self.copy_password(result_label.text()))

        layout = QVBoxLayout(self)
        layout.addLayout(length_layout)
        layout.addWidget(digits_checkbox)
        layout.addWidget(letters_checkbox)
        layout.addWidget(special_chars_checkbox)

        button_layout = QHBoxLayout()
        button_layout.addWidget(generate_button)
        button_layout.addWidget(mix_button)
        button_layout.addWidget(copy_button)

        layout.addLayout(button_layout)
        layout.addWidget(result_label, alignment=Qt.AlignCenter)
        layout.addWidget(strength_bar)
        layout.addWidget(complexity_label, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def update_length_label(self, value):
        self.length_label.setText(str(value))

    def generate_password(self, length_slider, digits_checkbox, letters_checkbox, special_chars_checkbox, result_label,
                          strength_bar, complexity_label):
        length = length_slider.value()
        use_digits = digits_checkbox.isChecked()
        use_letters = letters_checkbox.isChecked()
        use_special_chars = special_chars_checkbox.isChecked()

        # Construire la liste des caractères disponibles
        characters = ''
        if use_digits:
            characters += string.digits
        if use_letters:
            characters += string.ascii_letters
        if use_special_chars:
            characters += string.punctuation

        if not characters:
            result_label.setText("Veuillez sélectionner au moins un type de caractère.")
            return

        # 4. Vérification des caractères minimums
        # Ajouter au moins un caractère de chaque type sélectionné
        password = []
        if use_digits:
            password.append(random.choice(string.digits))
        if use_letters:
            password.append(random.choice(string.ascii_letters))
        if use_special_chars:
            password.append(random.choice(string.punctuation))

        # Compléter avec des caractères aléatoires pour atteindre la longueur souhaitée
        password.extend(random.choices(characters, k=length - len(password)))
        random.shuffle(password)  # Mélanger pour répartir les caractères
        password = ''.join(password)

        # Afficher le mot de passe généré
        result_label.setText(password)

        # Émettre un signal avec le mot de passe généré
        self.password_generated.emit(password)

        # Évaluer la force du mot de passe
        strength, complexity_text = self.evaluate_password_strength(password)
        strength_bar.setValue(strength)
        complexity_label.setText(f"Complexité : {complexity_text}")

    def mix_password(self, result_label):
        password = result_label.text()
        if password:
            mixed_password = ''.join(random.sample(password, len(password)))
            result_label.setText(mixed_password)

    def evaluate_password_strength(self, password):
        length = len(password)
        has_digits = any(c.isdigit() for c in password)
        has_letters = any(c.isalpha() for c in password)
        has_special = any(c in string.punctuation for c in password)

        # Calcul de la force du mot de passe basé sur le tableau Hive Systems
        strength = 0
        complexity_text = "Très Faible"

        if length < 8:
            strength = 10
            complexity_text = "Très Faible"
        elif length < 10:
            if has_digits and has_letters and has_special:
                strength = 30
                complexity_text = "Faible"
            elif has_digits and has_letters:
                strength = 25
                complexity_text = "Faible"
            else:
                strength = 20
                complexity_text = "Très Faible"
        elif length < 12:
            if has_digits and has_letters and has_special:
                strength = 50
                complexity_text = "Moyenne"
            elif has_digits and has_letters:
                strength = 40
                complexity_text = "Moyenne"
            else:
                strength = 30
                complexity_text = "Faible"
        elif length < 15:
            if has_digits and has_letters and has_special:
                strength = 70
                complexity_text = "Bonne"
            elif has_digits and has_letters:
                strength = 60
                complexity_text = "Bonne"
            else:
                strength = 50
                complexity_text = "Moyenne"
        elif length < 20:
            if has_digits and has_letters and has_special:
                strength = 90
                complexity_text = "Très Bonne"
            elif has_digits and has_letters:
                strength = 80
                complexity_text = "Très Bonne"
            else:
                strength = 70
                complexity_text = "Bonne"
        else:
            strength = 100
            complexity_text = "Excellente"

        return min(strength, 100), complexity_text

    def copy_password(self, password):
        clipboard = QApplication.clipboard()
        clipboard.setText(password)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MotDePasseWidget()
    window.show()
    sys.exit(app.exec())

