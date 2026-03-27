import flet as ft
from ui import create_login_layout

def main(page: ft.Page):
    page.title = "InventoryPro Web"
    page.window.maximized = True
    page.add(create_login_layout(page))

if __name__ == "__main__":
    ft.app(target=main)