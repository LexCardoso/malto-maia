"""Popula o cardapio com os dados reais da Malto Maia.

Idempotente: por padrao SO roda se o banco estiver vazio, pra nunca sobrescrever
as edicoes que o admin fizer pelo painel. Use --force pra apagar e recriar tudo.

    python manage.py seed_cardapio
    python manage.py seed_cardapio --force
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from cardapio.models import Categoria, ConfiguracaoSite, Item

# Espelha assets/menu-data.js do design. preco None = "a definir".
MENU = [
    {
        "slug": "quentes",
        "nome_pt": "Bebidas Quentes", "nome_en": "Hot Drinks",
        "nota_pt": "A alma da casa — extraído na hora.",
        "nota_en": "The heart of the house — freshly pulled.",
        "itens": [
            ("Café Espresso", "70 ml", "70 ml", 6.80, False),
            ("Café Curto", "30 ml", "30 ml", 6.80, False),
            ("Café Ristretto", "15 ml", "15 ml", 6.80, False),
            ("Café Carioca", "50 ml água + 70 ml café", "50 ml water + 70 ml coffee", 6.80, False),
            ("Café Aromatizado", "70 ml · consultar sabores", "70 ml · ask for flavours", 10.80, False),
            ("Café Duplo", "120 ml", "120 ml", 10.80, False),
            ("Macchiato", "70 ml café + 180 ml leite vaporizado", "70 ml coffee + 180 ml steamed milk", 10.80, False),
            ("Café Latte", "70 ml café + 180 ml leite", "70 ml coffee + 180 ml milk", 10.80, False),
            ("Café Bombom", "Espresso, leite condensado, leite vaporizado, chantilly", "Espresso, condensed milk, steamed milk, whipped cream", 10.80, False),
            ("Cappuccino Mineiro", "Leite, café, chocolate e canela · 250 ml", "Milk, coffee, chocolate & cinnamon · 250 ml", 10.80, True),
            ("Chocolate Suíço", "Leite vaporizado + chocolate cremoso · 250 ml", "Steamed milk + creamy chocolate · 250 ml", 12.80, False),
            ("Massala Chai", "Leite vaporizado + chá indiano · 250 ml", "Steamed milk + Indian tea · 250 ml", 12.80, False),
            ("Chá Prensa Francesa", "French press", "French press", 10.80, False),
            ("Moccacino", "Chocolate ou caramelo", "Chocolate or caramel", 14.80, False),
            ("Spirit of Lion", "Amarula, espresso, chantilly", "Amarula, espresso, whipped cream", 22.80, False),
            ("Irish Coffee", "Whisky, espresso, chantilly", "Whisky, espresso, whipped cream", 25.80, False),
            ("Moccinha", "Leite condensado, espresso, conhaque, chantilly", "Condensed milk, espresso, brandy, whipped cream", 20.80, False),
        ],
    },
    {
        "slug": "geladas",
        "nome_pt": "Bebidas Geladas", "nome_en": "Cold Drinks",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Frappuccino", "250 ml", "250 ml", 17.50, False),
            ("Affogato", "Sorvete, espresso, chantilly", "Ice cream, espresso, whipped cream", 16.80, False),
            ("Soda Italiana", "200 ml · consultar sabores", "200 ml · ask for flavours", 12.00, False),
            ("Milk Shake", "350 ml · consultar sabores", "350 ml · ask for flavours", 18.50, False),
            ("Banana Split", "", "", 17.50, False),
            ("Cappuccino Shake", "350 ml", "350 ml", 17.50, False),
            ("Chocolate Shake", "350 ml", "350 ml", 16.00, False),
            ("Jarra de Suco Detox", "400 ml", "400 ml", 12.50, False),
            ("Brownie com Sorvete e Chantilly", "", "", 10.00, False),
            ("Açaí", "Granola e calda a escolher", "Granola and topping of your choice", None, False),
        ],
    },
    {
        "slug": "doces",
        "nome_pt": "Doces", "nome_en": "Sweets",
        "nota_pt": "Feitos em casa, todos os dias.",
        "nota_en": "Homemade, every day.",
        "itens": [
            ("Torta — fatia", "Sabor do dia · destaque a torta de coco", "Flavour of the day · our famous coconut pie", 13.80, True),
            ("Torta Especial", "", "", 15.00, False),
            ("Bolo caseiro — fatia", "Consultar sabores", "Ask for flavours", 6.00, False),
            ("Manjar — pedaço", "", "", 8.00, False),
            ("Crème Brûlée", "", "", 10.80, False),
            ("Doce de festa fondant", "Unidade", "Each", 4.80, False),
            ("Chantilly adicional", "", "", 3.00, False),
            ("Adicionais", "Canela, bule de água, caldas", "Cinnamon, pot of water, syrups", 4.00, False),
            ("Geleias", "", "", None, False),
        ],
    },
    {
        "slug": "salgados",
        "nome_pt": "Salgados", "nome_en": "Savouries",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Empada", "Frango, palmito ou queijo", "Chicken, heart of palm or cheese", 10.00, False),
            ("Empada de Camarão", "", "Shrimp empanada", 12.00, False),
            ("Croquete de Carne", "", "Beef croquette", 15.00, False),
            ("Bolinho de Bacalhau", "", "Codfish ball", 25.00, False),
            ("Quiche", "Alho-poró ou carne seca", "Leek or dried beef", 15.00, False),
            ("Quiche de Bacalhau", "", "Codfish quiche", 17.00, False),
            ("Quiche Lorraine", "", "", 17.00, False),
            ("Pastel de Forno", "", "Baked pastel", 10.00, False),
        ],
    },
    {
        "slug": "sanduiches",
        "nome_pt": "Sanduíches & Especiais", "nome_en": "Sandwiches & Specials",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Sanduíche de Pernil", "", "Pork shoulder sandwich", 19.80, False),
            ("Sanduíche de Carne Seca", "", "Dried beef sandwich", 19.80, False),
            ("Sanduíche de Carne Assada", "", "Roast beef sandwich", 19.80, False),
            ("Misto Quente / Queijo Quente", "", "Ham & cheese / toasted cheese", 12.00, False),
            ("Pão na Chapa", "", "Buttered grilled bread", 5.00, False),
            ("Pão de Queijo", "Cheese bread", "Cheese bread", 8.00, True),
        ],
    },
    {
        "slug": "almoco",
        "nome_pt": "Sugestão de Almoço", "nome_en": "Lunch Suggestions",
        "nota_pt": "Servidos individualmente e montados na hora.",
        "nota_en": "Served individually, plated to order.",
        "itens": [
            ("Lasanha de Berinjela — Bolonhesa", "Com mozarela", "Bolognese with mozzarella", 45.00, False),
            ("Lasanha de Berinjela — Camarão", "Com cottage", "Shrimp with cottage cheese", 48.00, False),
            ("Estrogonoff de Frango", "Batata noisette", "Chicken · noisette potatoes", 38.00, False),
            ("Estrogonoff de Filé Mignon", "", "Filet mignon", 45.00, False),
            ("Estrogonoff de Camarão", "", "Shrimp", 45.00, False),
            ("Estrogonoff Neblina / Gorgonzola", "Batata noisette", "Gorgonzola · noisette potatoes", 54.00, False),
            ("Fricassê de Bacalhau", "Batata palha", "Codfish · shoestring potatoes", 45.00, False),
            ("Costelinha Suína", "Barbecue + batata frita", "BBQ pork ribs + fries", 42.00, False),
            ("Escalopinho de Filé Mignon", "Arroz à montese + noisette", "Filet · montese rice + noisette", 48.00, False),
        ],
    },
    {
        "slug": "caldos",
        "nome_pt": "Caldos, Sopas & Cremes", "nome_en": "Broths, Soups & Creams",
        "nota_pt": "Disponíveis em 500 ml / 350 ml.",
        "nota_en": "Available in 500 ml / 350 ml.",
        "itens": [
            ("Caldo de Mocotó", "500 ml / 350 ml", "500 ml / 350 ml", None, False),
            ("Caldo Verde", "500 ml / 350 ml", "500 ml / 350 ml", None, False),
            ("Creme de Abóbora com Carne Seca", "500 ml / 350 ml", "500 ml / 350 ml", None, False),
            ("Sopa de Legumes", "500 ml / 350 ml", "500 ml / 350 ml", None, False),
        ],
    },
    {
        "slug": "zero-lactose",
        "nome_pt": "Bebidas Zero Lactose", "nome_en": "Lactose-Free Drinks",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Macchiato", "", "", 13.80, False),
            ("Café Latte", "", "", 13.80, False),
            ("Cappuccino Mineiro", "", "", 13.80, False),
            ("Chocolate Suíço", "", "", 13.80, False),
            ("Massala Chai", "", "", 14.80, False),
            ("Mocaccino", "Chocolate ou caramelo", "Chocolate or caramel", 13.80, False),
            ("Milk Shake", "", "", 19.80, False),
        ],
    },
    {
        "slug": "bebidas",
        "nome_pt": "Bebidas", "nome_en": "Drinks",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Refrigerante lata", "", "Canned soda", 6.00, False),
            ("Água mineral sem gás", "", "Still water", 4.00, False),
            ("Água mineral com gás", "", "Sparkling water", 4.00, False),
            ("Mate natural", "", "", 8.00, False),
            ("Suco — Vinícola Aurora", "", "", 8.00, False),
            ("H²O", "", "", 8.00, False),
            ("Suco Del Valle", "Consultar sabores", "Ask for flavours", 8.00, False),
            ("Suco de Laranja Inteiro", "", "Whole orange juice", 8.00, False),
        ],
    },
    {
        "slug": "cervejas",
        "nome_pt": "Cervejas", "nome_en": "Beers",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Heineken Long Neck", "355 ml", "355 ml", 10.00, False),
            ("Petra Long Neck", "355 ml", "355 ml", 10.00, False),
            ("Eisenbahn Pilsen", "355 ml", "355 ml", 10.00, False),
            ("Budweiser Long Neck", "355 ml", "355 ml", 10.00, False),
            ("Demais rótulos", "Therezópolis 600 ml, Eisenbahn Dunkel, Stella Artois 275 ml, Corona Extra, Brahma Zero, Malzbier, Baden Baden Especial 600 ml", "Therezópolis 600 ml, Eisenbahn Dunkel, Stella Artois 275 ml, Corona Extra, Brahma Zero, Malzbier, Baden Baden Especial 600 ml", None, False),
        ],
    },
    {
        "slug": "vinhos",
        "nome_pt": "Vinhos & Espumantes", "nome_en": "Wines & Sparkling",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Cabernet Chileno", "", "Chilean Cabernet", 31.00, False),
            ("Cabernet Português", "", "Portuguese Cabernet", 148.00, False),
            ("Cabernet Argentino", "", "Argentine Cabernet", 148.00, False),
        ],
    },
]


class Command(BaseCommand):
    help = "Popula categorias e itens do cardapio (idempotente; --force recria)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Apaga e recria tudo, mesmo com dados existentes.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if Categoria.objects.exists() and not opts["force"]:
            self.stdout.write(
                "Cardapio ja populado — pulando (use --force para recriar)."
            )
            ConfiguracaoSite.get()
            return

        if opts["force"]:
            Item.objects.all().delete()
            Categoria.objects.all().delete()

        for ci, cat in enumerate(MENU):
            categoria = Categoria.objects.create(
                slug=cat["slug"],
                nome_pt=cat["nome_pt"], nome_en=cat["nome_en"],
                nota_pt=cat["nota_pt"], nota_en=cat["nota_en"],
                ordem=ci,
            )
            for ii, (nome, dpt, den, preco, destaque) in enumerate(cat["itens"]):
                Item.objects.create(
                    categoria=categoria, nome=nome,
                    desc_pt=dpt, desc_en=den, preco=preco,
                    destaque=destaque, ordem=ii,
                )

        ConfiguracaoSite.get()
        self.stdout.write(
            self.style.SUCCESS(
                f"Cardapio populado: {Categoria.objects.count()} categorias, "
                f"{Item.objects.count()} itens."
            )
        )
