import flet as ft
import data
from data import registrar_snapshot, export_relatorio_diario
import tkinter as tk
from zoneinfo import ZoneInfo
import time
import os
from datetime import datetime

# ------------------------------------------------------------------
# 1) Tela de login
# ------------------------------------------------------------------
def create_login_layout(page: ft.Page):
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            do_login(e)
    page.on_keyboard_event = on_keyboard
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    error_text = ft.Text("", color=ft.Colors.RED, size=14)
    # cpf_input  = ft.TextField(label="CPF",   width=300, hint_text="Só números")
    senha_input= ft.TextField(label="Código de login", width=300,
                              password=True, can_reveal_password=True)
    
    
    def do_login(e):
        # Obtém a data e hora atuais
        agora = datetime.now()
        # Formata a senha como dia, mês, ano, hora e minuto
        senha_correta1 = agora.strftime("%d%m%Y%H%M")
        senha_correta2 = str(int(agora.strftime("%d%m%Y%H%M"))-1)
        senha_input.value = senha_correta1 #APAGAR
        if senha_input.value.strip() == senha_correta1 or senha_input.value.strip() == senha_correta2:
            page.controls.clear()
            page.add(create_layout(page))
        else:
            error_text.value = "Senha inválida. Verifique o Código de login"
        page.update()
        

    def forgot_password(e):
        page.controls.clear()
        page.add(create_recuperacao_senha_layout(page))
        page.update()

    login_form = ft.Column(
        [
            ft.Text("InventoryPro", size=36, weight="bold"),
            ft.Divider(thickness=2, color=ft.Colors.BLUE),
            ft.Text("Login", size=28, weight="bold"),
            senha_input,
            ft.ElevatedButton("Entrar",            on_click=do_login),
            ft.ElevatedButton("Esqueci a senha",   on_click=forgot_password),
            error_text,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
    )

    return ft.Container(
        content=ft.Container(
            login_form,
            bgcolor=ft.Colors.GREY_900,
            padding=30,
            border_radius=10,
            width=400,
            height=480,
            alignment=ft.Alignment(0, 0)
        ),
        bgcolor=ft.Colors.BLUE_GREY_700,
        expand=True,
        alignment=ft.Alignment(0, 0)
    )

# ------------------------------------------------------------------
# 2) Recuperação de senha (placeholder)
# ------------------------------------------------------------------
def create_recuperacao_senha_layout(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    def voltar(e):
        page.controls.clear()
        page.add(create_login_layout(page))
        page.update()

    content = ft.Column(
        [
            ft.Text("InventoryPro", size=36, weight="bold"),
            ft.Divider(thickness=2, color=ft.Colors.BLUE),
            ft.Text("Recuperação de Senha", size=28, weight="bold"),
            ft.Container(
                ft.Text(
                    "Página em manutenção, em breve será possível recuperar a senha",
                    size=19, color=ft.Colors.GREY, weight="bold", text_align="center"
                ),
                alignment=ft.Alignment(0, 0),
                padding=20
            ),
            ft.ElevatedButton("Voltar", on_click=voltar),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
    )

    return ft.Container(
        content=ft.Container(
            content,
            bgcolor=ft.Colors.GREY_900,
            padding=30,
            border_radius=10,
            width=400,
            height=500,
            alignment=ft.Alignment(0, 0)
        ),
        bgcolor=ft.Colors.BLUE_GREY_700,
        expand=True,
        alignment=ft.Alignment(0, 0)
    )



# ------------------------------------------------------------------
# 3) Layout principal
# ------------------------------------------------------------------
def create_layout(page: ft.Page):
    report_items = {"equipamento": [], "patrimonio": []}
    report_rows  = {"equipamento": [], "patrimonio": []}
    
    # Cor de destaque – âmbar claro (legível em tema escuro)
    HIGHLIGHT_COLOR = ft.Colors.RED_800
    # --------------------------------------------------------------
    # 3.1  helpers
    # --------------------------------------------------------------
    def set_row_highlight(tipo, row_idx):
        """Ativa ou limpa o destaque da linha baseada na quantidade."""
        try:
            qtd = int(report_items[tipo][row_idx][4])
            report_rows[tipo][row_idx].color = (
                HIGHLIGHT_COLOR if qtd <= 5 else None
            )
        except Exception:
            report_rows[tipo][row_idx].color = None

    def edit_item(tipo, event, index, column):
        report_items[tipo][index][column] = event.control.value
        # Se coluna 4 (quantidade) mudou manualmente:
        if column == 4:
            set_row_highlight(tipo, index)
            page.update()

    # --------------------------------------------------------------
    # 3.2 Formulário de adição
    # --------------------------------------------------------------
    def build_add_form(tipo):
        equipamento_input = ft.TextField(label="Equipamento", expand=True)
        marca_input       = ft.TextField(label="Marca",       expand=True)

        quantidade_field = ft.TextField(
            label="Quantidade", value="0", expand=True,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(regex_string=r"\d*"),
        )
        quantidade_field.on_change = lambda e: (
            setattr(quantidade_field, "value",
                    "".join(c for c in quantidade_field.value if c.isdigit())),
            page.update()
        )

        def inc_q(e):
            quantidade_field.value = str(int(quantidade_field.value or 0) + 1)
            page.update()

        def dec_q(e):
            quantidade_field.value = str(max(0, int(quantidade_field.value or 0) - 1))
            page.update()

        quantidade_row = ft.Row(
            [ft.IconButton(ft.Icons.REMOVE, on_click=dec_q),
             quantidade_field,
             ft.IconButton(ft.Icons.ADD,    on_click=inc_q)],
            alignment=ft.MainAxisAlignment.CENTER, expand=True
        )

        validade_input = ft.TextField(
            label="Validade (DD/MM/AAAA)", expand=True, hint_text="DD/MM/AAAA",
            input_filter=ft.InputFilter(regex_string=r"[0-9/]*"),
            on_change=lambda e: (
                setattr(validade_input, "value",
                        "".join(c for c in validade_input.value if c.isdigit() or c == "/")),
                data.format_date_input(validade_input, page),
            ),
        )
        saida_input = ft.TextField(
            label="Data de Saída (opcional)", expand=True, hint_text="DD/MM/AAAA",
            input_filter=ft.InputFilter(regex_string=r"[0-9/]*"),
            on_change=lambda e: (
                setattr(saida_input, "value",
                        "".join(c for c in saida_input.value if c.isdigit() or c == "/")),
                data.format_date_input(saida_input, page),
            ),
        )
        observacoes_input = ft.TextField(label="Observações", expand=True, multiline=True)

        return ft.Column(
            [
                ft.Text(f"Adicionar {tipo.capitalize()}", size=24, weight="bold"),
                equipamento_input,
                marca_input,
                quantidade_row,
                validade_input,
                observacoes_input,
                saida_input,
                ft.ElevatedButton(
                    "Adicionar", icon=ft.Icons.ADD,
                    on_click=lambda e: (
                        setattr(quantidade_field, "value", quantidade_field.value.strip()),
                        data.process_item(
                            tipo, equipamento_input, marca_input,
                            quantidade_field, validade_input,
                            observacoes_input, saida_input, page
                        )
                    )[1]
                    
                ),
            ],
            spacing=15, expand=True
        )

    # --------------------------------------------------------------
    # 3.3 Atualização da tabela
    # --------------------------------------------------------------
    def update_report_table(tipo):
        report_rows[tipo].clear()
        report_items[tipo] = data.load_items_for_report(tipo)

        def make_number_cell(initial, row_idx):
            txt = ft.TextField(
                value=str(initial), expand=True,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=lambda e: edit_item(tipo, e, row_idx, 4)
            )

            def inc(e):
                txt.value = str(int(txt.value or 0) + 1)
                report_items[tipo][row_idx][4] = txt.value
                set_row_highlight(tipo, row_idx)
                page.update()

            def dec(e):
                txt.value = str(max(0, int(txt.value or 0) - 1))
                report_items[tipo][row_idx][4] = txt.value
                set_row_highlight(tipo, row_idx)
                page.update()

            return ft.Row(
                [ft.IconButton(ft.Icons.REMOVE, on_click=dec),
                 txt,
                 ft.IconButton(ft.Icons.ADD,    on_click=inc)],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )

        for i, item in enumerate(report_items[tipo]):
            item += [""] * (8 - len(item))
            cells = []
            for j in range(1, 8):
                if j == 1:  # Equipamento
                    control = ft.Text(item[j], expand=True)
                elif j == 4:  # Quantidade
                    control = make_number_cell(item[j], i)
                else:
                    control = ft.TextField(
                        value=item[j], expand=True,
                        on_change=lambda e, r=i, c=j: edit_item(tipo, e, r, c)
                    )
                cells.append(ft.DataCell(control))

            # botão Excluir
            def on_delete(e, t=tipo, rid=item[0]):
                data.delete_item(t, rid)
                update_report_table(t)
                page.open(ft.SnackBar(ft.Text(f"Item excluido")))
                page.update()
            cells.append(
                ft.DataCell(ft.IconButton(ft.Icons.DELETE,
                                          icon_color=ft.Colors.RED,
                                          tooltip="Excluir",
                                          on_click=on_delete))
            )

            # cria DataRow e aplica destaque inicial
            dr = ft.DataRow(cells=cells)
            report_rows[tipo].append(dr)
            set_row_highlight(tipo, i)

        page.update()

    # --------------------------------------------------------------
    # 3.4 Salvar alterações
    # --------------------------------------------------------------
    def save_changes(tipo):
        data.save_edited_items(tipo, report_items[tipo])
        page.open(ft.SnackBar(ft.Text(f"Alterações salvas com sucesso!")))
        page.update()

    # --------------------------------------------------------------
    # 3.5 Abas
    # --------------------------------------------------------------
    def build_editable_view_tab(tipo, title):
        update_report_table(tipo)
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c)) 
                    for c in
                ["Data Entrada","Equipamento","Marca","Quantidade",
                 "Validade","Observações","Data Saída","Ações"]],
            rows=report_rows[tipo], 
            expand=True,
        )
        scroll_h = ft.Row([table], scroll=ft.ScrollMode.ALWAYS, expand=True)
        scroll_v = ft.Column([scroll_h], scroll=ft.ScrollMode.AUTO, expand=True)
        return ft.Column(
            [
                ft.Text(title, size=24, weight="bold"),
                ft.Container(scroll_v, expand=True, height=500),
                ft.Row(
                    [ft.ElevatedButton("Salvar Alterações",
                        icon=ft.Icons.SAVE,
                        on_click=lambda e: save_changes(tipo))],
                    spacing=10
                ),
            ],
            spacing=15, expand=True
        )

    def build_report_tab(tipo, title):
        items = data.load_items_for_report(tipo)
        
        def export_word(e):
            path = data.export_to_word(tipo, items)
            page.open(ft.SnackBar(ft.Text(f"WORD exportado")))
            page.update()
            


        def export_excel(e):
            path = data.export_to_excel(tipo, items)
            page.open(ft.SnackBar(ft.Text(f"Excel exportado")))
            page.update()


        def export_pdf(e):
            path = data.export_to_pdf(tipo, items)
            page.open(ft.SnackBar(ft.Text(f"PDF exportado")))
            page.update()
       
        def export_pdf_imprimir(e):
            import webbrowser
            path = data.export_to_pdf(tipo, items)
            page.open(ft.SnackBar(ft.Text(f"PDF exportado")))
            if os.path.isfile(path):
                webbrowser.open(path)
                page.open(ft.SnackBar(ft.Text("PDF exportado e aberto")))
            else:
                page.open(ft.SnackBar(ft.Text("Erro ao exportar o PDF")))
            page.update()
            page.update()

    

        rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(f))) for f in row[1:]])
            for row in items
        ]
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c)) for c in
                ["Data Entrada","Equipamento","Marca","Quantidade",
                 "Validade","Observações","Data Saída"]],
            rows=rows, expand=True
        )
        scroll_h = ft.Row([table], scroll=ft.ScrollMode.ALWAYS, expand=True)
        scroll_v = ft.Column([scroll_h], scroll=ft.ScrollMode.AUTO, expand=True)
        return ft.Column(
            [
                ft.Text(title, size=24, weight="bold"),
                ft.Container(scroll_v, expand=True, height=500),
                ft.Row(
                    [
                        ft.ElevatedButton("Exportar para Excel", icon=ft.Icons.DESCRIPTION,   on_click=export_excel),
                        ft.ElevatedButton("Exportar para PDF",   icon=ft.Icons.PICTURE_AS_PDF, on_click=export_pdf),
                        ft.ElevatedButton("Exportar para Word", icon=ft.Icons.TEXT_SNIPPET, on_click=export_word),
                        ft.ElevatedButton("Imprimir",            icon=ft.Icons.PRINT, on_click=export_pdf_imprimir),
                        
                    ],
                    spacing=10
                ),
            ],
            spacing=15, expand=True
        )
        

    # Abas fixas
    add_equipamento_tab = build_add_form("equipamento")
    add_patrimonio_tab  = build_add_form("patrimonio")

    support_tab = ft.Column(
    [
        ft.Text("Tutorial de Uso do 'InventoryPro'", size=24, weight="bold"),

        # Visão Geral
        ft.Text("Visão Geral", size=20, weight="bold"),
        ft.Text(
            "O InventoryPro é uma aplicação de gestão de itens, projetada para facilitar o registro e o acompanhamento dos equipamentos e patrimônios da brigada."
            " Este guia ajudará você a utilizar as principais funcionalidades do sistema.",
            size=16
        ),
        
        # Adicionando Equipamentos e Patrimônios
        ft.Text("O programa é dividido em 3 abas: 'Cadastro'(responsável por adicionar itens), 'Visualização'(responsável por visualizar e editar itens já adicionados), e 'Relatórios'(responsável pela geração dos relatórios)", size=18),
        ft.Text("Adicionando Equipamentos e Patrimônios", size=20, weight="bold"),
        ft.Text("Passos para Adicionar:", size=18),

        ft.Text("1. Acesse a aba 'Cadastro':", size=16),
        ft.Text(
            "   - No menu lateral, clique em 'Adicionar Equipamento' ou 'Adicionar Patrimônio'. Ambos levam à mesma funcionalidade.",
            size=16
        ),

        ft.Text("2. Preencha as Informações:", size=16),
        ft.Text(
            "   - Equipamento: Insira o nome ou ID do equipamento.\n"
            "   - Marca: Insira a marca ou fabricante.\n"
            "   - Quantidade: Use os botões '+' e '-' para ajustar a quantidade.\n"
            "   - Validade: Insira a data de validade no formato DD/MM/AAAA.\n"
            "   - Observações: Adicione informações adicionais no campo de texto.\n"
            "   - Data de Saída: Opcionalmente, indique a data de saída do estoque.",
            size=16
        ),

        ft.Text("3. Salvar:", size=16),
        ft.Text(
            "   - Após preencher os dados, clique em 'Adicionar' para salvar o registro.",
            size=16
        ),

        # Visualização e Edição de Itens
        ft.Text("Visualização e Edição de Itens", size=20, weight="bold"),
        ft.Text("Alterar e Excluir Itens:", size=18),

        ft.Text("1. Acessar a aba 'Visualização':", size=16),
        ft.Text(
            "   - Selecione 'Equipamentos' ou 'Patrimônios' no menu para visualizar a lista.",
            size=16
        ),

        ft.Text("2. Editar Itens:", size=16),
        ft.Text(
            "   - Clique no item desejado e altere os campos necessários.\n"
            "   - Ajuste a quantidade utilizando os controles disponíveis.",
            size=16
        ),

        ft.Text("3. Excluir Itens:", size=16),
        ft.Text(
            "   - Para remover um item, utilize a opção de exclusão direta ao lado do item.",
            size=16
        ),

        ft.Text("4. Salvar Alterações:", size=16),
        ft.Text(
            "   - Após editar, clique no botão 'Salvar' para aplicar as mudanças.",
            size=16
        ),

        # Relatório Diário
        ft.Text("Aba 'Relatórios'", size=20, weight="bold"),
        ft.Text("Gerando um Relatório Diário:", size=18),

        ft.Text("1. Acessar 'Relatório Diário':", size=16),
        ft.Text(
            "   - Clique em 'Relatório Diário' no menu lateral.",
            size=16
        ),

        ft.Text("2. Capturar Dados:", size=16),
        ft.Text(
            "   - Utilize os botões 'Início equip.' / 'Início Patr.' ao iniciar o expediente, e 'Fim Equip.' / 'Fim Patr.' ao finalizar o expediente para capturar os dados do dia. Isso trava a tabela para garantir a integridade do relatório.",
            size=16
        ),

        ft.Text("3. Exportar Relatório:", size=16),
        ft.Text(
            "   - Após capturar os dados, clique em 'Gerar PDF Diário' para visualizar e exportar o relatório em PDF completo e inalterável.",
            size=16
        ),

        # Relatórios Exportados
        ft.Text("Relatórios Exportados", size=20, weight="bold"),
        ft.Text(
            "   - Selecione 'Relatórios Exportados' no menu para visualizar todos os relatórios diários armazenados.",
            size=16
        ),
          ft.Text(
            "   - Os botões de 'Relatório Equip.' e 'Relatório Patrim.' na barra lateral servem apenas para fazer relatórios pontuais que não são inalteráveis. ",
            size=16
        ),
        # Conclusão
        ft.Text("Conclusão", size=20, weight="bold"),
        ft.Text(
            "O InventoryPro é uma solução eficaz para gerenciar seu inventário de forma intuitiva e organizada. Aproveite todas as funcionalidades para otimizar seu processo de controle de equipamentos e patrimônios.",
            size=16
        ),
    ],
    spacing=15, expand=True, scroll=True  # Adiciona a funcionalidade de rolagem
)
    
    # Conteúdo inicial
    default_tab    = ft.Text(
        "Bem-vindo ao InventoryPro\nSelecione uma aba na barra lateral",
        size=20, weight="bold", text_align="center"
    )
    main_container = ft.Container(default_tab, padding=20, expand=True)

    def build_relatorios_exportados_tab():
        # Pegue a lista de PDFs
        arquivos_pdf = data.listar_pdfs()
        lista = []

        if not arquivos_pdf:
            lista.append(ft.Text("Nenhum PDF exportado encontrado."))
        else:
            for nome in sorted(arquivos_pdf, reverse=True):
                caminho = os.path.join(data.PASTA_RELATORIOS_DIARIO, nome)
                row = ft.Row([
                    ft.Text(nome, expand=True),
                    ft.ElevatedButton(
                        "Abrir",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        on_click=lambda e, c=caminho: data.abrir_pdf(c)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                lista.append(row)

        return ft.Column(
            [
                ft.Text("Relatórios Exportados (PDF)", size=24, weight="bold"),
                ft.Divider(),
                *lista
            ],
            spacing=10, expand=True
        )
    
    def build_daily_view_tab():
        hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
        display_date = hoje.strftime("%d/%m/%Y")
        date_label = ft.Text(f"Data: {display_date}", size=16)

        cols = ["Data Entrada","Equipamento","Marca","Quantidade","Validade","Observações","Data Saída"]
        columns = [ft.DataColumn(ft.Text(c)) for c in cols]

        def make_table():
            return ft.DataTable(columns=columns, rows=[], expand=True)

        equip_inicio_table = make_table()
        equip_fim_table    = make_table()
        patr_inicio_table  = make_table()
        patr_fim_table     = make_table()

        iso_date = hoje.isoformat()

        def populate_snapshot(tipo, typ, table_ref):
            items = data.get_snapshots(tipo, iso_date, typ)
            table_ref.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(col))) for col in item[1:]])
                for item in items
            ]

        populate_snapshot("equipamento", "inicio", equip_inicio_table)
        populate_snapshot("equipamento",  "fim",    equip_fim_table)
        populate_snapshot("patrimonio",  "inicio", patr_inicio_table)
        populate_snapshot("patrimonio",   "fim",    patr_fim_table)

        log = ft.Text("", color=ft.Colors.GREEN)

        flags = {
            "ei": len(data.get_snapshots("equipamento", iso_date, "inicio"))  > 0,
            "ef": len(data.get_snapshots("equipamento", iso_date, "fim"))     > 0,
            "pi": len(data.get_snapshots("patrimonio", iso_date, "inicio"))   > 0,
            "pf": len(data.get_snapshots("patrimonio", iso_date, "fim"))      > 0,
        }

        pdf_button = ft.ElevatedButton(
            "Gerar PDF Diário",
            icon=ft.Icons.PICTURE_AS_PDF,
            disabled=not all(flags.values()),
            on_click=lambda e: data.abrir_pdf(export_relatorio_diario(display_date))
        )

        def update_pdf_button():
            pdf_button.disabled = not all(flags.values())
            page.update()

        def make_snap_button(label, tipo, typ, table_ref, key):
            btn = ft.ElevatedButton(label, disabled=flags[key])
            def handler(e):
                registrar_snapshot(tipo, typ)
                populate_snapshot(tipo, typ, table_ref)
                flags[key] = True            
                btn.disabled = True
                log.value = f"{tipo.capitalize()} snapshot “{typ}” gravado."
                update_pdf_button()        
            btn.on_click = handler
            return btn

        btn_equip_inicio = make_snap_button("Início Equip.", "equipamento", "inicio", equip_inicio_table, "ei")
        btn_equip_fim    = make_snap_button("Fim Equip.",    "equipamento", "fim",    equip_fim_table,    "ef")
        btn_patr_inicio  = make_snap_button("Início Patr.",  "patrimonio",  "inicio", patr_inicio_table,  "pi")
        btn_patr_fim     = make_snap_button("Fim Patr.",     "patrimonio",  "fim",    patr_fim_table,     "pf")

        botoes_row = ft.Row([
            btn_equip_inicio,
            btn_equip_fim,
            btn_patr_inicio,
            btn_patr_fim,
        ], spacing=8)

        return ft.Column(
            [
                ft.Text("Visão Diária", size=24, weight="bold"),
                date_label,
                botoes_row,
                log,
                ft.Divider(),

                ft.Text("Equipamentos - Início do dia", weight="bold"),
                ft.Container(
                    content=ft.Column([equip_inicio_table], scroll=ft.ScrollMode.AUTO, expand=True),
                    height=150, padding=5, #border=ft.Border(1, ft.Colors.GREY)
                ),

                ft.Text("Equipamentos - Fim do dia", weight="bold"),
                ft.Container(
                    content=ft.Column([equip_fim_table], scroll=ft.ScrollMode.AUTO, expand=True),
                    height=150, padding=5, #border=ft.Border(1, ft.Colors.GREY)
                ),

                ft.Text("Patrimônios - Início do dia", weight="bold"),
                ft.Container(
                    content=ft.Column([patr_inicio_table], scroll=ft.ScrollMode.AUTO, expand=True),
                    height=150, padding=5, #border=ft.Border(1, ft.Colors.GREY)
                ),

                ft.Text("Patrimônios - Fim do dia", weight="bold"),
                ft.Container(
                    content=ft.Column([patr_fim_table], scroll=ft.ScrollMode.AUTO, expand=True),
                    height=150, padding=5, #border=ft.Border(1, ft.Colors.GREY)
                ),

                ft.Divider(),
                pdf_button,
            ],
            spacing=15,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )


    # --------------------------------------------------------------
    # 3.6 Troca de abas
    # --------------------------------------------------------------
    def switch_tab(name):
        tabs = {
            "add_equipamento": add_equipamento_tab,
            "add_patrimonio":  add_patrimonio_tab,
            "view_equipamento": lambda: build_editable_view_tab("equipamento","Equipamentos Registrados"),
            "view_patrimonio":  lambda: build_editable_view_tab("patrimonio", "Patrimônios Registrados"),
            "visao_diaria": build_daily_view_tab,
            "relatorio_equipamento": lambda: build_report_tab("equipamento","Relatório de Equipamentos"),
            "relatorio_patrimonio":  lambda: build_report_tab("patrimonio", "Relatório de Patrimônios"),
            "relatorios_exportados": build_relatorios_exportados_tab,
            "support": support_tab,
        }
        main_container.content = tabs[name]() if callable(tabs[name]) else tabs[name]
        page.update()

    # --------------------------------------------------------------
    # 3.7 Sidebar
    # --------------------------------------------------------------
    sidebar = ft.Container(
        width=270, bgcolor=ft.Colors.BLUE_GREY_700, padding=10,
        content=ft.Column([
            ft.Text("InventoryPro", size=24, weight="bold", font_family="Courier New"),
            ft.Divider(),
            ft.Text("Cadastro", weight="bold", color=ft.Colors.WHITE),
            ft.ElevatedButton("Adicionar Equipamento", icon=ft.Icons.ADD,
                                on_click=lambda e: switch_tab("add_equipamento")),
            ft.ElevatedButton("Adicionar Patrimônio",  icon=ft.Icons.ADD,
                                on_click=lambda e: switch_tab("add_patrimonio")),
            ft.Text("Visualização", weight="bold", color=ft.Colors.WHITE),
            ft.ElevatedButton("Equipamentos", icon=ft.Icons.LIST,
                                on_click=lambda e: switch_tab("view_equipamento")),
            ft.ElevatedButton("Patrimônios", icon=ft.Icons.LIST,
                                on_click=lambda e: switch_tab("view_patrimonio")),
            ft.Text("Relatórios", weight="bold", color=ft.Colors.WHITE),
            ft.ElevatedButton("Relatório Diário", icon=ft.Icons.DATE_RANGE,
                                on_click=lambda e: switch_tab("visao_diaria")),
            ft.ElevatedButton("Relatório Equip.", icon=ft.Icons.DESCRIPTION,
                                on_click=lambda e: switch_tab("relatorio_equipamento")),
            ft.ElevatedButton("Relatório Patrim.", icon=ft.Icons.DESCRIPTION,
                                on_click=lambda e: switch_tab("relatorio_patrimonio")),
            ft.ElevatedButton("Relatórios Exportados", icon=ft.Icons.FOLDER,on_click=lambda e: switch_tab("relatorios_exportados")),
            ft.Divider(),
            ft.ElevatedButton("Suporte", icon=ft.Icons.HELP,
                                on_click=lambda e: switch_tab("support")),
        ], spacing=10),
    )

    # ----------------------------------------------------------------
    # 3.8 Estrutura final
    # ----------------------------------------------------------------
    return ft.Row([sidebar, ft.VerticalDivider(width=1), main_container],
                  expand=True)
