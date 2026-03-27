from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QStyle,
)


@dataclass
class VaultCredential:
    id: str | None
    service: str
    username: str
    password: str
    login_url: str | None = None
    notes: str | None = None
    category: str | None = None


class CredentialDialog(QDialog):
    def __init__(self, credential: VaultCredential | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Credencial")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.service_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Ingresa una contraseña segura")

        if credential:
            self.service_input.setText(credential.service)
            self.username_input.setText(credential.username)
            self.password_input.setText(credential.password)

        form.addRow("Servicio", self.service_input)
        form.addRow("Usuario", self.username_input)
        form.addRow("Contraseña", self.password_input)

        actions = QHBoxLayout()
        save_button = QPushButton("Guardar")
        save_button.setObjectName("PrimaryButton")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        actions.addWidget(cancel_button)
        actions.addWidget(save_button)

        layout.addLayout(form)
        layout.addLayout(actions)

    def get_data(self) -> VaultCredential:
        return VaultCredential(
            id=None,
            service=self.service_input.text().strip(),
            username=self.username_input.text().strip(),
            password=self.password_input.text(),
        )


class PasswordVaultView(QFrame):
    def __init__(self, api_client=None, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPanel")
        self.api_client = api_client
        self.credentials: list[VaultCredential] = []
        self.visible_passwords: set[int] = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_column = QVBoxLayout()
        title = QLabel("Password Vault")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Gestion segura de credenciales operativas y personales.")
        subtitle.setObjectName("MutedText")
        header_column.addWidget(title)
        header_column.addWidget(subtitle)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar servicio o usuario...")
        self.search_input.textChanged.connect(self.refresh_table)
        self.search_input.setMaximumWidth(260)

        add_button = QPushButton("Agregar nueva credencial")
        add_button.setObjectName("PrimaryButton")
        add_button.clicked.connect(self.add_credential)

        header_row.addLayout(header_column)
        header_row.addStretch(1)
        header_row.addWidget(self.search_input)
        header_row.addWidget(add_button)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Servicio", "Usuario", "Contraseña", "Acciones"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(header_row)
        layout.addWidget(self.table)

    def load_credentials(self) -> None:
        if not self.api_client:
            return
        try:
            items = self.api_client.list_credentials(self.search_input.text().strip())
            self.credentials = [
                VaultCredential(
                    id=item["id"],
                    service=item["service_name"],
                    username=item["login_username"],
                    password=item.get("password", ""),
                    login_url=item.get("login_url"),
                    notes=item.get("notes"),
                    category=item.get("category"),
                )
                for item in items
            ]
            self.refresh_table(skip_remote=True)
        except Exception as exc:
            self._show_warning(f"No se pudieron cargar las credenciales: {exc}")

    def filtered_credentials(self) -> list[tuple[int, VaultCredential]]:
        query = self.search_input.text().strip().lower()
        indexed_rows = list(enumerate(self.credentials))
        if not query:
            return indexed_rows
        return [
            (index, credential)
            for index, credential in indexed_rows
            if query in credential.service.lower() or query in credential.username.lower()
        ]

    def refresh_table(self, skip_remote: bool = False) -> None:
        if self.api_client and not skip_remote:
            self.load_credentials()
            return
        rows = self.filtered_credentials()
        self.table.setRowCount(len(rows))

        for row_index, (credential_index, credential) in enumerate(rows):
            self.table.setItem(row_index, 0, QTableWidgetItem(credential.service))
            self.table.setItem(row_index, 1, QTableWidgetItem(credential.username))

            password_item = QTableWidgetItem(self._display_password(credential_index, credential.password))
            self.table.setItem(row_index, 2, password_item)
            self.table.setCellWidget(row_index, 3, self._build_actions(credential_index))

        self.table.resizeColumnsToContents()

    def _display_password(self, credential_index: int, password: str) -> str:
        if credential_index in self.visible_passwords:
            return password
        return "•" * min(max(len(password), 8), 14)

    def _build_actions(self, credential_index: int) -> QFrame:
        actions_frame = QFrame()
        layout = QHBoxLayout(actions_frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        toggle_button = QPushButton("Ocultar" if credential_index in self.visible_passwords else "Ver")
        toggle_button.setIcon(
            self.style().standardIcon(
                QStyle.SP_DialogCloseButton if credential_index in self.visible_passwords else QStyle.SP_DialogOpenButton
            )
        )
        toggle_button.clicked.connect(lambda: self.toggle_password(credential_index))

        copy_button = QPushButton("Copiar")
        copy_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        copy_button.clicked.connect(lambda: self.copy_password(credential_index))

        edit_button = QPushButton("Editar")
        edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        edit_button.clicked.connect(lambda: self.edit_credential(credential_index))

        delete_button = QPushButton("Eliminar")
        delete_button.setObjectName("DangerButton")
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_button.clicked.connect(lambda: self.delete_credential(credential_index))

        layout.addWidget(toggle_button)
        layout.addWidget(copy_button)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addStretch(1)
        return actions_frame

    def add_credential(self) -> None:
        dialog = CredentialDialog(parent=self)
        if dialog.exec():
            credential = dialog.get_data()
            if not all([credential.service, credential.username, credential.password]):
                self._show_warning("Todos los campos son obligatorios.")
                return
            if self.api_client:
                try:
                    created = self.api_client.create_credential(
                        {
                            "service_name": credential.service,
                            "login_username": credential.username,
                            "password": credential.password,
                        }
                    )
                    self.credentials.append(
                        VaultCredential(
                            id=created["id"],
                            service=created["service_name"],
                            username=created["login_username"],
                            password=created["password"],
                            login_url=created.get("login_url"),
                            notes=created.get("notes"),
                            category=created.get("category"),
                        )
                    )
                except Exception as exc:
                    self._show_warning(f"No se pudo guardar la credencial: {exc}")
                    return
            else:
                self.credentials.append(credential)
            self.refresh_table(skip_remote=not bool(self.api_client))

    def edit_credential(self, index: int) -> None:
        dialog = CredentialDialog(self.credentials[index], self)
        if dialog.exec():
            credential = dialog.get_data()
            if not all([credential.service, credential.username, credential.password]):
                self._show_warning("Todos los campos son obligatorios.")
                return
            current = self.credentials[index]
            if self.api_client and current.id:
                try:
                    updated = self.api_client.update_credential(
                        current.id,
                        {
                            "service_name": credential.service,
                            "login_username": credential.username,
                            "password": credential.password,
                        },
                    )
                    self.credentials[index] = VaultCredential(
                        id=updated["id"],
                        service=updated["service_name"],
                        username=updated["login_username"],
                        password=updated["password"],
                        login_url=updated.get("login_url"),
                        notes=updated.get("notes"),
                        category=updated.get("category"),
                    )
                except Exception as exc:
                    self._show_warning(f"No se pudo actualizar la credencial: {exc}")
                    return
            else:
                self.credentials[index] = credential
            self.refresh_table(skip_remote=not bool(self.api_client))

    def delete_credential(self, index: int) -> None:
        credential = self.credentials[index]
        reply = QMessageBox.question(
            self,
            "Eliminar credencial",
            f"¿Eliminar la credencial de {credential.service}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            if self.api_client and credential.id:
                try:
                    self.api_client.delete_credential(credential.id)
                except Exception as exc:
                    self._show_warning(f"No se pudo eliminar la credencial: {exc}")
                    return
            self.credentials.pop(index)
            self.visible_passwords = {
                idx if idx < index else idx - 1
                for idx in self.visible_passwords
                if idx != index
            }
            self.refresh_table(skip_remote=not bool(self.api_client))

    def toggle_password(self, index: int) -> None:
        if index in self.visible_passwords:
            self.visible_passwords.remove(index)
        else:
            self.visible_passwords.add(index)
        self.refresh_table()

    def copy_password(self, index: int) -> None:
        QGuiApplication.clipboard().setText(self.credentials[index].password)
        QMessageBox.information(self, "Portapapeles", "Contraseña copiada sin exponerla en pantalla.")

    def _show_warning(self, message: str) -> None:
        QMessageBox.warning(self, "Validacion", message)
