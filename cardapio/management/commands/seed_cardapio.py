"""Popula o cardapio com os dados REAIS da Malto Maia (transcrito das fotos do cardapio).

Idempotente: por padrao SO roda se o banco estiver vazio, pra nunca sobrescrever
as edicoes que o admin fizer pelo painel. Use --force pra apagar e recriar tudo.

    python manage.py seed_cardapio
    python manage.py seed_cardapio --force

Obs.: nomes de item nao traduzem (so a descricao). preco None = "a definir".
Alguns precos do cardapio fisico sao manuscritos/com reflexo; o dono ajusta no painel.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from cardapio.models import Categoria, ConfiguracaoSite, Item

# Contato / endereco / mapa reais (entram no singleton ConfiguracaoSite no seed).
CONTATO = {
    "whatsapp": "5522988280158",          # +55 22 98828-0158
    "instagram": "doceria_maltomaia",
    "tripadvisor_url": (
        "https://www.tripadvisor.com.br/Restaurant_Review-g1598513-d13238200-"
        "Reviews-Doceria_Malto_Maia-Araruama_State_of_Rio_de_Janeiro.html"
    ),
    "latitude": Decimal("-22.9236137"),
    "longitude": Decimal("-42.3080728"),
}

# (nome, desc_pt, desc_en, preco, destaque). preco None = "a definir".
MENU = [
    {
        "slug": "quentes",
        "nome_pt": "Bebidas Quentes", "nome_en": "Hot Drinks",
        "nota_pt": "Cappuccino e chocolate: receita própria da casa, sem glúten nem espessante.",
        "nota_en": "Cappuccino & chocolate: our own recipe, gluten- and thickener-free.",
        "itens": [
            ("Café Espresso", "70 ml", "70 ml", 10.90, True),
            ("Café Curto", "30 ml", "30 ml", 10.90, False),
            ("Café Ristretto", "15 ml", "15 ml", 10.90, False),
            ("Café Carioca", "50 ml de água + 70 ml de café", "50 ml water + 70 ml coffee", 10.90, False),
            ("Café Aromatizado", "70 ml · Monin, consultar sabores", "70 ml · Monin, ask for flavours", 14.00, False),
            ("Café Duplo", "120 ml", "120 ml", 16.30, False),
            ("Café Coado", "Coado na hora", "Freshly brewed filter coffee", 17.40, False),
            ("Macchiato", "70 ml de café + 180 ml de leite vaporizado", "70 ml coffee + 180 ml steamed milk", 16.30, False),
            ("Café Latte", "70 ml de café + 180 ml de leite", "70 ml coffee + 180 ml milk", 16.30, False),
            ("Café Bombom", "Café, leite condensado, leite vaporizado e chantilly", "Coffee, condensed milk, steamed milk & whipped cream", 26.20, False),
            ("Cappuccino Mineiro", "Leite, café e chocolate · 250 ml", "Milk, coffee & chocolate · 250 ml", 18.30, True),
            ("Chocolate Suíço", "250 ml", "250 ml", 18.50, False),
            ("Massala Chai", "Leite vaporizado + chá indiano · 250 ml", "Steamed milk + Indian tea · 250 ml", 19.50, False),
            ("Chá na Prensa Francesa", "", "French press tea", 17.40, False),
            ("Mocaccino", "Chocolate ou caramelo, leite vaporizado, café e calda a escolher", "Chocolate or caramel, steamed milk, coffee & syrup of choice", 24.00, False),
            ("Spirit of Lion", "Amarula, café, leite vaporizado e chantilly", "Amarula, coffee, steamed milk & whipped cream", 38.30, False),
            ("Moccinha", "Leite condensado, café, conhaque e chantilly", "Condensed milk, coffee, brandy & whipped cream", 38.30, False),
        ],
    },
    {
        "slug": "descafeinados",
        "nome_pt": "Descafeinados", "nome_en": "Decaf",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Café Espresso", "Descafeinado", "Decaffeinated", 14.10, False),
            ("Café Coado", "Descafeinado", "Decaffeinated filter coffee", 20.70, False),
            ("Café com Latte", "Descafeinado", "Decaffeinated, with milk", 20.70, False),
        ],
    },
    {
        "slug": "zero-lactose",
        "nome_pt": "Bebidas Zero Lactose", "nome_en": "Lactose-Free Drinks",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Macchiato", "70 ml de café + 180 ml de leite vaporizado", "70 ml coffee + 180 ml steamed milk", 19.70, False),
            ("Café Latte", "70 ml de café + 180 ml de leite", "70 ml coffee + 180 ml milk", 19.70, False),
            ("Cappuccino Mineiro", "Leite, café e chocolate", "Milk, coffee & chocolate", 19.70, False),
            ("Chocolate Suíço", "Leite vaporizado + chocolate cremoso", "Steamed milk + creamy chocolate", 19.70, False),
            ("Massala Chai", "Leite vaporizado + chá indiano", "Steamed milk + Indian tea", 23.90, False),
        ],
    },
    {
        "slug": "geladas",
        "nome_pt": "Bebidas Geladas", "nome_en": "Cold Drinks",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Frappuccino", "Frappê de café e chocolate, sorvete e chantilly · 250 ml", "Coffee & chocolate frappé, ice cream & whipped cream · 250 ml", 26.90, False),
            ("Affogato", "Sorvete, café espresso e chantilly", "Ice cream, espresso & whipped cream", 26.90, False),
            ("Soda Italiana", "200 ml de água gasosa, gelo e Monin · consultar sabores", "200 ml sparkling water, ice & Monin · ask for flavours", 19.90, False),
            ("Milk Shake", "Morango ou chocolate", "Strawberry or chocolate", 28.90, False),
            ("Cappuccino Shake", "350 ml de cappuccino gelado, gelo e chantilly", "350 ml iced cappuccino, ice & whipped cream", 28.90, False),
            ("Chocolate Shake", "350 ml de chocolate gelado, gelo e chantilly", "350 ml iced chocolate, ice & whipped cream", 28.90, False),
        ],
    },
    {
        "slug": "bebidas",
        "nome_pt": "Bebidas", "nome_en": "Drinks",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Refrigerante (lata)", "", "Canned soda", 8.90, False),
            ("Água Mineral", "", "Mineral water", 5.90, False),
            ("Mate (Leão)", "", "Iced mate tea", 8.90, False),
            ("Cerveja Long Neck", "355 ml", "355 ml", 15.90, False),
            ("Suco Del Valle", "", "Del Valle juice", 11.90, False),
            ("Suco de Polpa", "Abacaxi, goiaba, manga, graviola, cajú, acerola ou cajá", "Pineapple, guava, mango, soursop, cashew, acerola or cajá", 11.90, False),
            ("Suco (Vinícola Aurora)", "", "Aurora grape juice", 11.90, False),
            ("H²O", "", "", 11.90, False),
        ],
    },
    {
        "slug": "salgados",
        "nome_pt": "Salgados", "nome_en": "Savouries",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Empada", "Frango, palmito ou queijo", "Chicken, heart of palm or cheese", 18.50, False),
            ("Empada de Camarão", "", "Shrimp empada", 21.80, False),
            ("Quiche", "Alho-poró; bacalhau com espinafre; lorraine; carne seca; palmito com tomate seco", "Leek; codfish & spinach; lorraine; dried beef; heart of palm & sun-dried tomato", 21.80, False),
            ("Pastel de Forno", "Frango, pernil ou presunto com requeijão", "Chicken, pork or ham with cream cheese", 18.50, False),
        ],
    },
    {
        "slug": "sanduiches",
        "nome_pt": "Sanduíches & Especiais", "nome_en": "Sandwiches & Specials",
        "nota_pt": "", "nota_en": "",
        "itens": [
            ("Sanduíche Especial", "Pernil, carne seca ou carne assada · pão francês, carne desfiada e queijo", "Pork, dried beef or roast beef · French bread, shredded meat & cheese", 32.80, False),
            ("Misto Quente", "Pão francês ou de forma", "Ham & cheese · French or sliced bread", 19.80, False),
            ("Queijo Quente", "Pão francês ou de forma", "Toasted cheese · French or sliced bread", 19.80, False),
            ("Pão na Chapa", "", "Buttered grilled bread", 7.50, False),
            ("Pão de Queijo", "Com queijo", "With cheese", 8.60, True),
            ("Pão com Ovo", "Pão francês com dois ovos", "French bread with two eggs", 18.50, False),
            ("Ovo Mexido", "Dois ovos mexidos", "Two scrambled eggs", 9.70, False),
            ("Queijo Adicional", "50 g de queijo muçarela", "50 g mozzarella", 7.90, False),
        ],
    },
    {
        "slug": "almoco",
        "nome_pt": "Sugestão de Almoço", "nome_en": "Lunch Suggestions",
        "nota_pt": "Servidos individualmente e empratados.",
        "nota_en": "Served individually, plated to order.",
        "itens": [
            ("Lasanha de Berinjela — Bolonhesa", "", "Bolognese", 66.00, False),
            ("Lasanha de Berinjela — Camarão", "", "Shrimp", 70.00, False),
            ("Lasanha de Berinjela — Palmito", "", "Heart of palm", 66.00, False),
            ("Lasanha de Berinjela — Frango", "", "Chicken", 58.00, False),
            ("Estrogonofe de Frango", "Com arroz e batata noisette", "With rice & noisette potatoes", 52.00, False),
            ("Estrogonofe de Filé Mignon", "Com arroz e batata noisette", "With rice & noisette potatoes", 60.00, False),
            ("Estrogonofe de Camarão", "Com arroz e batata noisette", "With rice & noisette potatoes", 70.00, False),
            ("Medalhão", "Filé mignon ao molho gorgonzola, batata noisette e arroz branco", "Filet mignon in gorgonzola sauce, noisette potatoes & white rice", None, False),
            ("Fricassê de Bacalhau", "Com arroz e batata palha", "With rice & shoestring potatoes", 60.00, False),
            ("Fricassê de Frango", "Com arroz e batata palha", "With rice & shoestring potatoes", 50.00, False),
            ("Fricassê de Pernil", "Com arroz e batata palha", "With rice & shoestring potatoes", 50.00, False),
            ("Costelinha Suína", "Molho barbecue, arroz e batata noisette", "BBQ sauce, rice & noisette potatoes", 52.00, False),
            ("Nhoque de Batata — Molho de Carne", "", "Meat sauce", 66.00, False),
            ("Nhoque de Batata — Molho de Camarão", "", "Shrimp sauce", 70.00, False),
            ("Nhoque de Batata — Molho de Palmito", "", "Heart of palm sauce", 66.00, False),
            ("Nhoque de Batata — Molho Parisiense", "", "Parisienne sauce", 66.00, False),
            ("Pernil com Arroz de Forno", "Salpicão e farofa", "Baked rice, salpicão & farofa", 66.00, False),
            ("Escalopinho de Mignon", "Arroz piamontese e batata noisette", "Piedmontese rice & noisette potatoes", 62.00, False),
        ],
    },
    {
        "slug": "doces",
        "nome_pt": "Doces", "nome_en": "Sweets",
        "nota_pt": "Feitos em casa.",
        "nota_en": "Homemade.",
        "itens": [
            ("Torta — fatia", "Consultar sabores · a famosa torta de coco", "Ask for flavours · our famous coconut pie", 19.90, True),
            ("Torta Especial — fatia", "Consultar sabores", "Ask for flavours", 22.90, False),
            ("Bolo Caseiro", "Consultar sabores", "Ask for flavours", 8.90, False),
            ("Bolo Caseiro Especial", "Consultar sabores", "Ask for flavours", 10.90, False),
            ("Creme Inglês", "Geleia de abacaxi ou de morango com amora", "Pineapple or strawberry-blackberry jam", 21.80, False),
            ("Açaí (taça)", "", "Bowl", 17.50, False),
            ("Sorvete (taça)", "", "Ice cream bowl", 17.50, False),
            ("Banana Split", "Banana, 3 sorvetes e chantilly na barca", "Banana, 3 ice creams & whipped cream", 45.90, False),
            ("Brownie com Sorvete", "Sorvete de creme, chantilly e calda de chocolate", "Vanilla ice cream, whipped cream & chocolate sauce", 26.90, False),
            ("Rabanada com Sorvete", "Sorvete de pistache, chantilly e calda de menta", "Pistachio ice cream, whipped cream & mint sauce", 28.90, False),
            ("Rabanada (2 un)", "", "2 pieces", 8.90, False),
            ("Creme Brûlée", "Creme de baunilha com crosta de açúcar", "Vanilla custard with caramelised sugar crust", 21.80, False),
            ("Doce de Festa", "Consultar sabores", "Party sweet · ask for flavours", 5.50, False),
            ("Chantilly (adicional)", "", "Extra whipped cream", 7.90, False),
            ("Adicionais", "Canela, bule de água, caldas, etc.", "Cinnamon, pot of water, syrups, etc.", 3.00, False),
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

        # Contato/endereco/mapa reais no singleton (so no seed inicial / --force).
        config = ConfiguracaoSite.get()
        config.whatsapp = CONTATO["whatsapp"]
        config.instagram = CONTATO["instagram"]
        config.tripadvisor_url = CONTATO["tripadvisor_url"]
        config.latitude = CONTATO["latitude"]
        config.longitude = CONTATO["longitude"]
        config.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Cardapio populado: {Categoria.objects.count()} categorias, "
                f"{Item.objects.count()} itens + contato/mapa."
            )
        )
