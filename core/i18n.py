"""Strings de interface PT/EN — porte de assets/i18n.js do design.

Uso: {% t "hero.title" %} no template (ver core/templatetags/maltomaia.py),
ou t("hero.title", lang) no Python. Conteudo de cardapio NAO vive aqui — vem
dos campos *_pt / *_en dos modelos.
"""

STRINGS = {
    # Nav
    "nav.home": {"pt": "Início", "en": "Home"},
    "nav.menu": {"pt": "Cardápio", "en": "Menu"},
    "nav.order": {"pt": "Encomendas", "en": "Order"},
    "nav.about": {"pt": "Sobre", "en": "About"},
    "nav.visit": {"pt": "Visite", "en": "Visit"},
    "nav.admin": {"pt": "Painel", "en": "Admin"},

    # Common
    "cta.menu": {"pt": "Ver cardápio", "en": "View menu"},
    "cta.order": {"pt": "Fazer encomenda", "en": "Place an order"},
    "cta.directions": {"pt": "Como chegar", "en": "Get directions"},
    "cta.whatsapp": {"pt": "Pedir no WhatsApp", "en": "Order on WhatsApp"},
    "cta.backHome": {"pt": "Voltar ao início", "en": "Back to home"},
    "common.unavailable": {"pt": "Indisponível", "en": "Unavailable"},
    "common.askPrice": {"pt": "a definir", "en": "ask us"},
    "common.signature": {"pt": "Carro-chefe", "en": "House favourite"},
    "common.updated": {"pt": "Atualizado em", "en": "Updated on"},

    # Hero
    "hero.eyebrow": {"pt": "Praia Seca · Araruama – RJ", "en": "Praia Seca · Araruama – RJ"},
    "hero.title": {"pt": "Café de raiz mineira,\nà beira-mar.", "en": "Coffee with Minas roots,\nby the sea."},
    "hero.sub": {"pt": "Numa casa colonial amarela, o espresso é levado a sério e a torta de coco sai quentinha do forno. Sente-se, respire e fique um tempo.", "en": "In a yellow colonial house, the espresso is taken seriously and the coconut pie comes warm from the oven. Sit down, breathe, and stay a while."},
    "hero.badge": {"pt": "Nº 15 de 91 em Araruama · TripAdvisor", "en": "No. 15 of 91 in Araruama · TripAdvisor"},

    # About
    "about.eyebrow": {"pt": "Nossa casa", "en": "Our house"},
    "about.title": {"pt": "A alma mineira que veio morar na praia", "en": "A Minas Gerais soul that came to live by the beach"},
    "about.p1": {"pt": "A Malto Maia nasceu do desejo de juntar duas coisas boas: o aconchego das cozinhas de Minas e a brisa de Praia Seca. Funcionamos numa casa colonial de telha de barro, com jardim, móveis de madeira patinada e pratos de cerâmica nas paredes.", "en": "Malto Maia was born from the wish to bring together two good things: the warmth of Minas kitchens and the breeze of Praia Seca. We live in a colonial house with clay-tile roofs, a garden, patinated wooden furniture and ceramic plates on the walls."},
    "about.p2": {"pt": "Aqui o café é coado com calma — da prensa francesa ao espresso bem extraído. É um lugar para conversar sem pressa, com a lousa anunciando o doce do dia.", "en": "Here coffee is brewed unhurried — from the French press to a well-pulled espresso. A place for slow conversation, with the chalkboard announcing the sweet of the day."},
    "about.stat1": {"pt": "Anos à beira-mar", "en": "Years by the sea"},
    "about.stat2": {"pt": "Feito em casa", "en": "Homemade"},
    "about.stat3": {"pt": "Avaliação média", "en": "Average rating"},

    # Highlights
    "high.eyebrow": {"pt": "Carros-chefe", "en": "House favourites"},
    "high.title": {"pt": "O que as pessoas voltam para comer", "en": "What people come back for"},
    "high.sub": {"pt": "Os queridinhos das avaliações — direto da lousa.", "en": "The reviewers’ darlings — straight from the chalkboard."},

    # Gallery
    "gal.eyebrow": {"pt": "O ambiente", "en": "The space"},
    "gal.title": {"pt": "Um cantinho cuidado, do jardim à xícara", "en": "A cared-for corner, from garden to cup"},

    # Order strip
    "order.eyebrow": {"pt": "Encomendas", "en": "Orders"},
    "order.title": {"pt": "Leve a Malto Maia para a sua mesa", "en": "Take Malto Maia to your table"},
    "order.sub": {"pt": "Tortas inteiras, salgados e quitutes por encomenda. Monte seu pedido e finalize pelo WhatsApp.", "en": "Whole pies, savouries and treats to order. Build your order and finish on WhatsApp."},

    # Reviews
    "rev.eyebrow": {"pt": "Quem visita, conta", "en": "In their words"},
    "rev.title": {"pt": "4,4 de 5 — e contando", "en": "4.4 out of 5 — and counting"},
    "rev.r1": {"pt": "O melhor espresso da região, num ambiente que dá vontade de não ir embora. A torta de coco é obrigatória.", "en": "The best espresso in the region, in a place you won’t want to leave. The coconut pie is a must."},
    "rev.r1a": {"pt": "Marina R. · Google", "en": "Marina R. · Google"},
    "rev.r2": {"pt": "Casinha charmosa, atendimento caprichado e cappuccino mineiro maravilhoso. Voltarei sempre.", "en": "Charming little house, attentive service and a wonderful Minas cappuccino. I’ll always come back."},
    "rev.r2a": {"pt": "Paulo C. · TripAdvisor", "en": "Paulo C. · TripAdvisor"},
    "rev.r3": {"pt": "Lugar de bom gosto, perfeito para um café tranquilo. O pão de queijo derrete na boca.", "en": "A tasteful place, perfect for a quiet coffee. The cheese bread melts in your mouth."},
    "rev.r3a": {"pt": "Helena M. · Google", "en": "Helena M. · Google"},

    # Instagram
    "ig.eyebrow": {"pt": "No nosso feed", "en": "On our feed"},
    "ig.title": {"pt": "Acompanhe o dia a dia", "en": "Follow our everyday"},
    "ig.follow": {"pt": "Seguir @maltomaia", "en": "Follow @maltomaia"},

    # Visit
    "visit.eyebrow": {"pt": "Onde estamos", "en": "Find us"},
    "visit.title": {"pt": "Venha nos visitar", "en": "Come and visit us"},
    "visit.addr": {"pt": "Estrada de Praia Seca, Araruama – RJ", "en": "Estrada de Praia Seca, Araruama – RJ"},
    "visit.hoursLabel": {"pt": "Horário", "en": "Hours"},
    "visit.hours": {"pt": "Todos os dias · 9h às 18h", "en": "Every day · 9am to 6pm"},
    "visit.phoneLabel": {"pt": "WhatsApp", "en": "WhatsApp"},

    # Concept
    "concept.eyebrow": {"pt": "Nosso conceito", "en": "Our concept"},
    "concept.title": {"pt": "Um lugar para apreciar com calma", "en": "A place to savour, slowly"},
    "concept.body": {"pt": "A Malto Maia é um respiro do corre-corre. Cuidamos do ambiente como quem recebe em casa: música baixa, mesas postas com carinho e tempo para um bom café. Pedimos só uma gentileza — venha como quem visita a sala de um amigo, com aquele capricho no traje. Assim, a casa segue sendo esse cantinho especial para todos.", "en": "Malto Maia is a breather from the rush. We care for the space the way you’d welcome guests at home: soft music, lovingly set tables and time for a good coffee. We ask only one kindness — come as you would to a friend’s living room, dressed with a little care. That way the house stays this special corner for everyone."},

    # Footer
    "foot.tagline": {"pt": "Doceria & Cafeteria · desde sempre, à beira-mar", "en": "Doceria & Cafeteria · always, by the sea"},
    "foot.explore": {"pt": "Navegar", "en": "Explore"},
    "foot.contact": {"pt": "Contato", "en": "Contact"},
    "foot.hours": {"pt": "Funcionamento", "en": "Opening hours"},
    "foot.rights": {"pt": "Feito com café e carinho.", "en": "Made with coffee and care."},

    # Menu page
    "menu.title": {"pt": "Cardápio", "en": "Menu"},
    "menu.sub": {"pt": "Café de verdade, comida de casa. Preços em reais (R$).", "en": "Real coffee, home cooking. Prices in Brazilian reais (R$)."},
    "menu.exportPdf": {"pt": "Exportar PDF", "en": "Export PDF"},
    "menu.qr": {"pt": "QR do cardápio", "en": "Menu QR code"},
    "menu.qrTitle": {"pt": "Cardápio online", "en": "Online menu"},
    "menu.qrHint": {"pt": "Aponte a câmera para abrir o cardápio no celular.", "en": "Point your camera to open the menu on your phone."},
    "menu.jump": {"pt": "Ir para", "en": "Jump to"},
    "menu.close": {"pt": "Fechar", "en": "Close"},

    # Order page
    "ord.title": {"pt": "Fazer encomenda", "en": "Place an order"},
    "ord.sub": {"pt": "Escolha os itens, ajuste as quantidades e finalize pelo WhatsApp.", "en": "Pick your items, adjust quantities and finish on WhatsApp."},
    "ord.pick": {"pt": "Escolha os itens", "en": "Choose items"},
    "ord.add": {"pt": "Adicionar", "en": "Add"},
    "ord.summary": {"pt": "Resumo do pedido", "en": "Order summary"},
    "ord.empty": {"pt": "Seu pedido está vazio. Toque em “Adicionar” nos itens ao lado.", "en": "Your order is empty. Tap “Add” on the items beside."},
    "ord.notes": {"pt": "Observações", "en": "Notes"},
    "ord.notesPh": {"pt": "Ex.: torta de coco inteira para sábado, retirar 15h…", "en": "e.g. whole coconut pie for Saturday, pickup at 3pm…"},
    "ord.name": {"pt": "Seu nome", "en": "Your name"},
    "ord.namePh": {"pt": "Como podemos te chamar?", "en": "What may we call you?"},
    "ord.total": {"pt": "Total estimado", "en": "Estimated total"},
    "ord.totalNote": {"pt": "Itens “a definir” serão confirmados na conversa.", "en": "Items marked “ask us” are confirmed in chat."},
    "ord.send": {"pt": "Enviar pedido no WhatsApp", "en": "Send order on WhatsApp"},
    "ord.clear": {"pt": "Limpar", "en": "Clear"},
    "ord.search": {"pt": "Buscar item…", "en": "Search item…"},
    "ord.waHeader": {"pt": "Olá! Gostaria de fazer uma encomenda na Malto Maia:", "en": "Hello! I’d like to place an order at Malto Maia:"},

    # Admin (painel)
    "adm.title": {"pt": "Painel do Cardápio", "en": "Menu Dashboard"},
    "adm.sub": {"pt": "Gerencie itens, preços e disponibilidade.", "en": "Manage items, prices and availability."},
    "adm.search": {"pt": "Buscar item ou categoria…", "en": "Search item or category…"},
    "adm.add": {"pt": "Novo item", "en": "New item"},
    "adm.itemsCount": {"pt": "itens no cardápio", "en": "items on the menu"},
    "adm.available": {"pt": "Disponível", "en": "Available"},
    "adm.lastUpdate": {"pt": "Última atualização", "en": "Last updated"},
    "adm.markToday": {"pt": "Marcar hoje", "en": "Mark today"},
    "adm.exportPdf": {"pt": "Exportar PDF", "en": "Export PDF"},
    "adm.qr": {"pt": "Gerar QR Code", "en": "Generate QR"},
    "adm.col.item": {"pt": "Item", "en": "Item"},
    "adm.col.cat": {"pt": "Categoria", "en": "Category"},
    "adm.col.price": {"pt": "Preço", "en": "Price"},
    "adm.col.status": {"pt": "Status", "en": "Status"},
    "adm.col.actions": {"pt": "Ações", "en": "Actions"},
    "adm.edit": {"pt": "Editar", "en": "Edit"},
    "adm.save": {"pt": "Salvar", "en": "Save"},
    "adm.cancel": {"pt": "Cancelar", "en": "Cancel"},
    "adm.name": {"pt": "Nome", "en": "Name"},
    "adm.desc": {"pt": "Descrição", "en": "Description"},
    "adm.priceField": {"pt": "Preço (R$)", "en": "Price (R$)"},
    "adm.priceTbd": {"pt": "A definir", "en": "To be defined"},
    "adm.newItem": {"pt": "Adicionar item", "en": "Add item"},
}

LANGS = ("pt", "en")
LANG_DEFAULT = "pt"


def t(key, lang="pt"):
    """Devolve a string no idioma pedido, com fallback pt -> key."""
    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("pt") or key
