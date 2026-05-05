from flask import Flask, jsonify
import threading
import time
import random
import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import requests
import psycopg2
import psycopg2.extras

# ============================================================
# CONFIG
# ============================================================
APP_TZ = ZoneInfo("America/Sao_Paulo")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
EVOLUTION_URL = os.getenv("EVOLUTION_URL", "https://evolution-api-2iwv.onrender.com").strip().rstrip("/")
EVOLUTION_KEY = os.getenv("EVOLUTION_KEY", "rainhagames_F5C542_corvo_2026").strip()
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "rainha").strip()

SCHEDULER_SLEEP = 10
LOCK_TIMEOUT = 60

ROOMS = {
    "slots": {
        "jid": os.getenv("SLOTS_JID", "120363425781519648@g.us"),
        "windows": [("00:00", "23:59")],
        "min_interval": 3,
        "max_interval": 5,
    },
    "aviator": {
        "jid": os.getenv("AVIATOR_JID", "120363407874498135@g.us"),
        "windows": [("10:00", "12:00"), ("15:00", "17:00"), ("20:00", "23:59")],
        "min_interval": 12,
        "max_interval": 18,
    },
    "bacbo": {
        "jid": os.getenv("BACBO_JID", "120363423860148086@g.us"),
        "windows": [("10:00", "12:00"), ("14:00", "17:00"), ("20:00", "23:59")],
        "min_interval": 8,
        "max_interval": 12,
    },
    "sports": {
        "jid": os.getenv("SPORTS_JID", "120363428850704241@g.us"),
        "windows": [("09:00", "09:25"), ("14:00", "14:25"), ("19:00", "19:25"), ("21:00", "21:25")],
        "min_interval": 20,
        "max_interval": 25,
    },
    "mines": {
        "jid": os.getenv("MINES_JID", "120363425225665418@g.us"),
        "windows": [("10:00", "12:00"), ("14:00", "17:00"), ("19:00", "23:59")],
        "min_interval": 8,
        "max_interval": 14,
    },
    "roleta": {
        "jid": os.getenv("ROLETA_JID", "120363427358245251@g.us"),
        "windows": [("14:00", "17:00"), ("19:00", "23:59")],
        "min_interval": 10,
        "max_interval": 15,
    },
}

# ============================================================
# CATÁLOGO DE JOGOS — SLOTS
# ============================================================
PROVIDER_GAMES = {
    "PG Soft": [
        ("Fortune Tiger", "96.81%", "🐯"),
        ("Fortune Ox", "96.75%", "🐂"),
        ("Fortune Rabbit", "96.75%", "🐰"),
        ("Fortune Mouse", "96.72%", "🐭"),
        ("Fortune Dragon", "96.83%", "🐉"),
        ("Fortune Snake", "96.70%", "🐍"),
        ("Fortune Gods", "96.74%", "💰"),
        ("Fortune Horse", "96.72%", "🐎"),
        ("Mahjong Ways", "96.92%", "🀄"),
        ("Mahjong Ways 2", "96.95%", "🀄"),
        ("Wild Bandito", "97.00%", "🤠"),
        ("Ganesha Gold", "96.49%", "🐘"),
        ("Ganesha Fortune", "96.71%", "🐘"),
        ("Caishen Wins", "96.92%", "💰"),
        ("Dragon Hatch", "96.83%", "🐉"),
        ("Dragon Hatch 2", "96.83%", "🐉"),
        ("Dragon Legend", "96.50%", "🐉"),
        ("Lucky Neko", "96.73%", "🐱"),
        ("Lucky Piggy", "96.44%", "🐷"),
        ("Leprechaun Riches", "97.35%", "🍀"),
        ("Shark Bounty", "96.71%", "🦈"),
        ("Muay Thai Champion", "96.86%", "🥊"),
        ("Ninja vs Samurai", "97.44%", "⚔️"),
        ("Galactic Gems", "98.13%", "💎"),
        ("Wild Bounty Showdown", "96.50%", "🤠"),
        ("Werewolf's Hunt", "96.50%", "🐺"),
        ("Medusa", "96.58%", "🐍"),
        ("Medusa II", "96.58%", "🐍"),
        ("Rave Party Fever", "96.32%", "🎧"),
        ("Speed Winner", "96.53%", "🏎️"),
        ("Totem Wonders", "96.71%", "🗿"),
        ("Opera Dynasty", "96.52%", "🎭"),
        ("Wings of Iguazu", "96.29%", "🦜"),
        ("Yakuza Honor", "96.11%", "🕴️"),
        ("Zombie Outbreak", "96.20%", "🧟"),
        ("Hip Hop Panda", "96.50%", "🐼"),
        ("Legend of Hou Yi", "96.95%", "🏹"),
        ("Legend of Perseus", "96.31%", "🛡️"),
        ("Mafia Mayhem", "96.50%", "🕵️"),
        ("Dragon Tiger Luck", "96.50%", "🐉"),
        ("Candy Burst", "96.50%", "🍬"),
        ("Mystic Potion", "96.50%", "🧪"),
        ("Emperor's Favour", "96.50%", "👑"),
        ("Prosperity Lion", "96.50%", "🦁"),
        ("Sushi Oishi", "96.50%", "🍣"),
        ("Vampire's Charm", "96.50%", "🧛"),
        ("Double Fortune", "96.50%", "🍀"),
        ("Jungle Delight", "96.50%", "🌿"),
        ("Cash Mania", "96.50%", "💵"),
        ("Inferno Mayhem", "96.50%", "🔥"),
        ("Honey Trap of Diao Chan", "96.50%", "👸"),
        ("Tree of Fortune", "96.50%", "🌳"),
        ("Three Monkeys", "96.50%", "🐒"),
        ("Tomb of Treasure", "96.50%", "🏺"),
        ("Three Crazy Pigs", "96.50%", "🐷"),
        ("Cowboys", "96.50%", "🤠"),
        ("Elves Town", "96.50%", "🧝"),
        ("Bank Robbers", "96.50%", "🏦"),
        ("Big Wild Buffalo", "96.50%", "🦬"),
        ("Electro Fiesta", "96.50%", "⚡"),
        ("Halloween Meow", "96.50%", "🎃"),
        ("Safari Wilds", "96.31%", "🦁"),
        ("Jurassic Kingdom", "96.18%", "🦖"),
        ("Rise of Apollo", "96.20%", "⚡"),
        ("Galaxy Miner", "96.32%", "🚀"),
        ("Crypto Gold", "96.12%", "₿"),
        ("Graffiti Rush", "96.50%", "🎨"),
        ("Diner Delights", "96.50%", "🍔"),
        ("Cash Mania", "96.50%", "💵"),
    ],
    "Pragmatic Play": [
        ("Big Bass Bonanza", "96.71%", "🎣"),
        ("Big Bass Bonanza Megaways", "96.70%", "🎣"),
        ("Big Bass Splash", "96.71%", "🎣"),
        ("Big Bass Halloween", "96.50%", "🎃"),
        ("Big Bass Halloween 2", "96.50%", "🎃"),
        ("Big Bass Christmas Bash", "96.50%", "🎄"),
        ("Buffalo King", "96.06%", "🦬"),
        ("Buffalo King Megaways", "96.78%", "🦬"),
        ("Gates of Olympus", "96.50%", "⚡"),
        ("Gates of Olympus 1000", "96.50%", "⚡"),
        ("Sweet Bonanza", "96.51%", "🍭"),
        ("Sweet Bonanza Xmas", "96.51%", "🎄"),
        ("The Dog House", "96.51%", "🐕"),
        ("The Dog House Megaways", "96.55%", "🐕"),
        ("Starlight Princess", "96.50%", "⭐"),
        ("Starlight Princess 1000", "96.50%", "⭐"),
        ("Wild West Gold", "96.51%", "🤠"),
        ("Wild West Gold Megaways", "96.50%", "🤠"),
        ("Wolf Gold", "96.01%", "🐺"),
        ("Chilli Heat", "96.50%", "🌶️"),
        ("Chilli Heat Megaways", "96.50%", "🌶️"),
        ("Book of the Fallen", "96.50%", "📖"),
        ("Book of Vikings", "96.50%", "📖"),
        ("Fire Strike", "96.52%", "🔥"),
        ("Fire Strike 2", "96.50%", "🔥"),
        ("Fruit Party", "96.50%", "🍓"),
        ("Fruit Party 2", "96.50%", "🍓"),
        ("Aztec Gems", "96.50%", "🏺"),
        ("Aztec Bonanza", "96.50%", "🏺"),
        ("Joker's Jewels", "96.50%", "💎"),
        ("Diamond Strike", "96.50%", "💎"),
        ("5 Lions Gold", "96.50%", "🦁"),
        ("5 Lions Megaways", "96.50%", "🦁"),
        ("Money Mouse", "96.52%", "🐭"),
        ("Cash Elevator", "96.50%", "🛗"),
        ("Candy Blitz", "96.50%", "🍬"),
        ("Drill That Gold", "96.50%", "⛏️"),
        ("Hand of Midas", "96.50%", "✋"),
        ("Madame Destiny Megaways", "96.51%", "🔮"),
        ("Gorilla Mayhem", "96.50%", "🦍"),
        ("Eye of Cleopatra", "96.50%", "👁️"),
        ("Bomb Bonanza", "96.50%", "💣"),
        ("Cash Bonanza", "96.50%", "💵"),
        ("Cleopatra's Riches", "96.50%", "👑"),
        ("Colossal Cash Zone", "96.50%", "💰"),
        ("Congo Cash", "96.50%", "🦍"),
        ("Crown of Fire", "96.50%", "👑"),
        ("Da Vinci's Treasure", "96.50%", "🎨"),
        ("Dino Drop", "96.50%", "🦖"),
        ("Dragon King Hot Pots", "96.50%", "🐉"),
    ],
    "Hacksaw Gaming": [
        ("Chaos Crew", "96.32%", "🎪"),
        ("Chaos Crew 2", "96.29%", "🎪"),
        ("Stick Em", "96.50%", "🏏"),
        ("Wanted Dead or a Wild", "96.38%", "🤠"),
        ("Bonus Bonanza", "96.50%", "💰"),
        ("Sea Of Riches", "96.50%", "🌊"),
        ("Mental", "96.50%", "🤯"),
        ("Extra Juicy Megaways", "96.50%", "🍊"),
        ("Dynamite Riches Megaways", "96.50%", "💥"),
        ("Harlequin Carnival", "96.50%", "🎭"),
    ],
    "Nolimit City": [
        ("xWays Hoarder xSplit", "96.23%", "👾"),
        ("Fire In The Hole", "96.01%", "💣"),
        ("San Quentin xWays", "96.24%", "⛓️"),
        ("Barbarian Fury", "96.06%", "⚔️"),
        ("Deadwood", "96.01%", "🪦"),
        ("Tombstone RIP", "96.24%", "🪦"),
        ("Poison Eve", "96.05%", "☠️"),
        ("Book of Shadows", "96.00%", "📖"),
        ("Punk Rocker", "96.07%", "🎸"),
        ("Infectious 5 xWays", "96.03%", "🦠"),
    ],
    "Spribe": [
        ("Mines", "97.00%", "💣"),
        ("Plinko", "97.00%", "🎯"),
        ("HiLo", "97.00%", "🃏"),
        ("Dice", "97.00%", "🎲"),
        ("Goal", "97.00%", "⚽"),
        ("Keno", "97.00%", "🎱"),
        ("Mini Roulette", "97.00%", "🎡"),
        ("Limbo", "97.00%", "📈"),
        ("Tower", "97.00%", "🏗️"),
    ],
    "Evolution": [
        ("Lightning Roulette", "97.30%", "⚡"),
        ("Crazy Time", "96.08%", "🎡"),
        ("Monopoly Live", "96.23%", "🎩"),
        ("Dream Catcher", "96.58%", "🌀"),
        ("Lightning Blackjack", "99.00%", "♠️"),
        ("Speed Baccarat", "98.76%", "🃏"),
        ("Immersive Roulette", "97.30%", "🎡"),
        ("Football Studio", "96.27%", "⚽"),
    ],
}

# ============================================================
# INTRO / CLOSING / ESTRATÉGIAS — SLOTS
# ============================================================
INTRO_VARIANTS = [
    "🎰 Entrada confirmada",
    "🎰 Oportunidade do momento",
    "🎰 Fiquem de olho nessa entrada",
    "🎰 Entrada em observação",
    "🎰 Jogo liberado para análise",
    "🎰 Possível janela interessante",
    "🎰 Movimento favorável agora",
]

CLOSING_VARIANTS = [
    "⚠️ Operação informativa. Use gestão e responsabilidade.",
    "⚠️ Controle a banca e não force entradas.",
    "⚠️ Jogue com responsabilidade e respeite seu limite.",
    "⚠️ Gestão primeiro. Operação sempre com controle.",
]

STRATEGY_VARIANTS = {
    "slots_leve": [
        "💎 Estilo Premium Leve:\n• 3 giros em bet baixa no normal\n• 5 giros no turbo mantendo a bet\n• Se não responder, faça mais 15 giros no automático\n• Sem insistir além disso",
        "💎 Estilo Premium Leve:\n• Comece com 3 giros em bet baixa\n• Depois faça 5 giros no turbo\n• Finalize com 15 giros no automático\n• Se não encaixar, aguarde a próxima",
    ],
    "slots_media": [
        "💎 Estilo Premium Média:\n• 3 giros em bet baixa no normal\n• 5 giros no turbo\n• Sem resposta? suba 1 nível de bet\n• Faça +15 giros no automático",
        "💎 Estilo Premium Média:\n• Inicie com 3 giros em bet baixa\n• Vá para 5 giros no turbo\n• Suba 1 nível com controle\n• Feche com 15 giros no automático",
    ],
    "slots_agressiva": [
        "💎 Estilo Premium Agressiva:\n• 3 giros em bet baixa no normal\n• 5 giros no turbo\n• Sem resposta? subir a bet com controle\n• Fazer +15 giros no automático\n• Limite máximo: 6% da banca",
        "💎 Estilo Premium Agressiva:\n• Comece leve com 3 giros no normal\n• Faça 5 giros no turbo\n• Suba a bet de forma controlada\n• Finalize com 15 giros no automático\n• Nunca ultrapasse 6% da banca",
    ],
    "crash": [
        "💎 Estilo Premium Crash:\n• Entrar com 3% da banca\n• Buscar saída entre 1.5x e 2x\n• Não perseguir multiplicador alto\n• Se perder 3 seguidas, pausar 5 minutos",
        "💎 Estilo Premium Crash:\n• Entrada pequena e fixa\n• Saída antecipada sem hesitar\n• No máximo 5 rodadas por sessão\n• Stop loss: 15% da banca",
    ],
    "mines": [
        "💎 Estilo Premium Mines:\n• Configurar 5 minas\n• Abrir no máximo 4 campos\n• Sair na 3ª ou 4ª abertura\n• Pare ao perder 3 rodadas seguidas",
        "💎 Estilo Premium Mines:\n• Gestão leve no início\n• Não forçar quinta abertura\n• Sessão curta\n• Controle total da banca",
    ],
    "dice": [
        "💎 Estilo Premium Dice:\n• Entrada pequena e fixa\n• Não aumentar agressivamente após perda\n• Trabalhar sessões curtas\n• Meta curta e pausa",
        "💎 Estilo Premium Dice:\n• Buscar constância, não emoção\n• Stop loss curto\n• Stop win rápido\n• Evite maratonar",
    ],
    "hilo": [
        "💎 Estilo Premium HiLo:\n• Bet fixa e pequena por rodada\n• Máximo 8 rodadas por sessão\n• Não dobre após perda\n• Stop loss: 5 erros seguidos = encerra",
        "💎 Estilo Premium HiLo:\n• Escolha sempre a mesma direção por sessão\n• Gestão rigorosa da banca\n• Sessão curta com meta definida\n• Pare ao atingir o stop win",
    ],
    "limbo": [
        "💎 Estilo Premium Limbo:\n• Entre com aposta fixa e pequena\n• Defina o multiplicador alvo antes de jogar\n• Não altere o alvo no meio da sessão\n• Stop loss: 15% da banca",
        "💎 Estilo Premium Limbo:\n• Multiplicador alvo entre 1.5x e 3x\n• Bet fixa sem progressão\n• Máximo 10 rodadas por sessão\n• Encerre ao atingir o objetivo",
    ],
    "plinko": [
        "💎 Estilo Premium Plinko:\n• Use risco baixo ou médio\n• Bet fixa por lançamento\n• Máximo 15 lançamentos por sessão\n• Não aumente a bet após sequência negativa",
        "💎 Estilo Premium Plinko:\n• Prefira as colunas centrais\n• Sessão curta com stop definido\n• Bet constante sem variação\n• Stop loss: 20% da banca",
    ],
    "roulette": [
        "💎 Estilo Premium Roleta:\n• Aposte nas cores (vermelho ou preto) com bet fixa\n• Não use progressão após perda\n• Máximo 10 rodadas por sessão\n• Stop loss: 25% da banca",
        "💎 Estilo Premium Roleta:\n• Foque nas apostas de maior frequência\n• Bet pequena e constante\n• Sessão curta e disciplinada\n• Stop win: dobrou = encerra",
    ],
    "baccarat": [
        "💎 Estilo Premium Baccarat:\n• Aposte sempre no Banker (menor vantagem da casa)\n• Bet fixa sem progressão\n• Máximo 10 mãos por sessão\n• Stop loss: 20% da banca",
        "💎 Estilo Premium Baccarat:\n• Mantenha a aposta no Banker por toda a sessão\n• Gestão disciplinada sem martingale\n• Sessão curta e objetiva\n• Stop win: 30% de lucro = encerra",
    ],
    "blackjack": [
        "💎 Estilo Premium Blackjack:\n• Siga sempre a estratégia básica\n• Bet fixa sem dobrar no tilt\n• Máximo 10 mãos por sessão\n• Stop loss: 20% da banca",
        "💎 Estilo Premium Blackjack:\n• Disciplina total na estratégia básica\n• Gestão fixa sem progressão agressiva\n• Sessão curta com meta definida\n• Stop win: dobrou = encerra",
    ],
    "keno": [
        "💎 Estilo Premium Keno:\n• Escolha entre 4 e 6 números por rodada\n• Mantenha os mesmos números por toda a sessão\n• Bet fixa sem progressão após perda\n• Máximo 10 rodadas por sessão",
        "💎 Estilo Premium Keno:\n• Não troque os números no meio da sessão\n• Gestão disciplinada e bet constante\n• Sessão curta com meta definida\n• Stop win: triplicou = encerra",
    ],
    "scratch": [
        "💎 Estilo Premium Scratch:\n• Jogue em bet baixa e fixa\n• Máximo 5 raspadinhas por sessão\n• Não aumente a bet após perda\n• Se ganhar, pare — não reinvista tudo",
        "💎 Estilo Premium Scratch:\n• Sessão curta e controlada\n• Bet mínima para mais volume de jogadas\n• Stop win: dobrou a banca = encerra\n• Stop loss: 5 tentativas sem retorno",
    ],
    "coin_flip": [
        "💎 Estilo Premium Heads Tails:\n• Escolha sempre o mesmo lado por sessão\n• Bet fixa sem dobrar após perda\n• Máximo 8 rodadas por sessão\n• Stop loss: 5 derrotas seguidas = encerra",
        "💎 Estilo Premium Heads Tails:\n• Não troque de lado no meio da sessão\n• Gestão fixa sem martingale\n• Sessão disciplinada e curta\n• Lucro pequeno e consistente",
    ],
    "wheel": [
        "💎 Estilo Premium Wheel:\n• Aposte nos campos de menor multiplicador\n• Bet fixa e pequena\n• Máximo 10 giros por sessão\n• Não persiga o multiplicador máximo",
        "💎 Estilo Premium Wheel:\n• Foque nos campos com maior frequência\n• Bet constante sem variação\n• Sessão curta com meta definida\n• Stop loss: 30% da banca",
    ],
    "penalty": [
        "💎 Estilo Premium Penalty:\n• Escolha sempre o mesmo canto por sessão\n• Bet fixa sem progressão\n• Máximo 8 cobranças por sessão\n• Stop loss: 4 erros seguidos = pausa",
        "💎 Estilo Premium Penalty:\n• Não mude o canto no meio da sessão\n• Gestão disciplinada da banca\n• Sessão curta e objetiva\n• Encerre ao atingir a meta",
    ],
    "tower": [
        "💎 Estilo Premium Tower:\n• Suba no máximo 4 andares por rodada\n• Retire antes do 5º andar\n• Bet fixa e pequena\n• Pare ao perder 3 rodadas seguidas",
        "💎 Estilo Premium Tower:\n• Não force andares altos\n• Saída disciplinada no 3º ou 4º andar\n• Sessão curta com stop definido\n• Stop loss: 20% da banca",
    ],
    "grid_slot": [
        "💎 Estilo Premium Grid:\n• Jogue em bet baixa — a volatilidade é alta\n• Aguarde as cascatas acontecerem naturalmente\n• Não aumente a bet em sequência negativa\n• Stop loss: 20% da banca por sessão",
        "💎 Estilo Premium Grid:\n• Alta volatilidade — prepare a banca\n• Bet fixa e disciplinada durante toda a sessão\n• Sessão curta com meta definida\n• Stop win: dobrou = encerra",
    ],
    "racing": [
        "💎 Estilo Premium Racing:\n• Escolha sempre o mesmo competidor por sessão\n• Bet fixa sem progressão\n• Máximo 8 apostas por sessão\n• Stop loss: 4 derrotas seguidas = pausa",
        "💎 Estilo Premium Racing:\n• Analise o histórico antes de apostar\n• Bet pequena e constante\n• Sessão curta e disciplinada\n• Stop win: dobrou = encerra",
    ],
    "bingo": [
        "💎 Estilo Premium Bingo:\n• Jogue com bet fixa e pequena\n• Máximo 10 cartelas por sessão\n• Não aumente a bet após sequência negativa\n• Stop loss: 20% da banca",
        "💎 Estilo Premium Bingo:\n• Controle o número de cartelas por rodada\n• Gestão disciplinada sem impulsividade\n• Sessão curta com meta definida\n• Stop win: dobrou = encerra",
    ],
    "darts": [
        "💎 Estilo Premium Darts:\n• Escolha sempre a mesma região alvo por sessão\n• Bet fixa sem progressão\n• Máximo 10 arremessos por sessão\n• Stop loss: 5 erros seguidos = pausa",
        "💎 Estilo Premium Darts:\n• Bet pequena e constante\n• Disciplina na escolha do alvo\n• Sessão curta com meta definida\n• Stop win: dobrou = encerra",
    ],
    "runner": [
        "💎 Estilo Premium Runner:\n• Comece com bet baixa até pegar o ritmo\n• Não aumente a bet em sequência negativa\n• Máximo 10 partidas por sessão\n• Stop loss: 20% da banca",
        "💎 Estilo Premium Runner:\n• Bet fixa e pequena por partida\n• Sessão curta com meta definida\n• Stop win: dobrou = encerra\n• Pare ao perder 4 seguidas",
    ],
}

CRASH_PROVIDERS = {"Spribe", "Original", "Betby", "Easybet"}

# ============================================================
# AVIATOR — VARIANTES DE SINAL
# ============================================================
AVIATOR_SIGNALS = [
    {
        "strategy": "Safe Flight ✈️",
        "body": "🎯 Cashout → *1.5x*\n⏳ Válido: 4 rodadas",
    },
    {
        "strategy": "Safe Flight ✈️",
        "body": "🎯 Cashout → *1.8x*\n⏳ Válido: 3 rodadas",
    },
    {
        "strategy": "Safe Flight ✈️",
        "body": "🎯 Cashout → *1.6x*\n⏳ Válido: 4 rodadas",
    },
    {
        "strategy": "Cashout Duplo 🔀",
        "body": "🔹 1ª saída → *1.5x* (50% do valor)\n🔹 2ª saída → *2.5x* (restante)\n⏳ Válido: 3 rodadas",
    },
    {
        "strategy": "Cashout Duplo 🔀",
        "body": "🔹 1ª saída → *1.5x* (50% do valor)\n🔹 2ª saída → *2.8x* (restante)\n⏳ Válido: 3 rodadas",
    },
    {
        "strategy": "Cashout Duplo 🔀",
        "body": "🔹 1ª saída → *1.8x* (50% do valor)\n🔹 2ª saída → *3.2x* (restante)\n⏳ Válido: 2 rodadas",
    },
    {
        "strategy": "Cashout Duplo 🔀",
        "body": "🔹 1ª saída → *2.0x* (50% do valor)\n🔹 2ª saída → *3.5x* (restante)\n⏳ Válido: 2 rodadas",
    },
    {
        "strategy": "Entrada Agressiva 🔥",
        "body": "🔹 1ª saída → *2.0x* (50% do valor)\n🔹 2ª saída → *4.0x* (restante)\n⏳ Válido: 2 rodadas",
    },
    {
        "strategy": "Entrada Agressiva 🔥",
        "body": "🔹 1ª saída → *2.5x* (60% do valor)\n🔹 2ª saída → *5.0x* (restante)\n⏳ Válido: 2 rodadas",
    },
    {
        "strategy": "Martingale Controlado ♟️",
        "body": "💵 Entrada 1: aposta normal → cashout *2.0x*\nSe red → 💵 Entrada 2: dobra → cashout *2.0x*\nSe red → 💵 Entrada 3: dobra → cashout *2.0x*\n⚡ Máximo 3 entradas. Nunca faça a 4ª.",
    },
]

AVIATOR_CLOSING = [
    "⚠️ Controle a banca e não force entradas.",
    "⚠️ Jogue com responsabilidade e respeite seu limite.",
    "⚠️ Gestão primeiro. Operação sempre com controle.",
    "⚠️ Operação informativa. Use gestão e responsabilidade.",
]

# ============================================================
# BACBO — VARIANTES DE SINAL
# ============================================================
BACBO_SIDES = [
    ("BANKER 🔵", "ALTA 🟢"),
    ("BANKER 🔵", "ALTA 🟢"),
    ("BANKER 🔵", "MÉDIA 🟡"),
    ("PLAYER 🔴", "ALTA 🟢"),
    ("PLAYER 🔴", "ALTA 🟢"),
    ("PLAYER 🔴", "MÉDIA 🟡"),
    ("TIE ⚪", "ESPECIAL 💎"),
]

BACBO_PATTERNS = [
    "Player venceu 4x seguidas — correção identificada",
    "Player venceu 5x seguidas — reversão esperada",
    "Banker venceu 4x seguidas — correção identificada",
    "Banker venceu 5x seguidas — reversão esperada",
    "Sequência de alternância Player/Banker — tendência de continuidade",
    "Dados equilibrados nas últimas rodadas — padrão estável",
    "Banker dominando com margens baixas — virada próxima",
    "Player dominando com margens baixas — virada próxima",
    "Dados do Banker caindo (soma baixa) — Player aquecendo",
    "Dados do Player caindo (soma baixa) — Banker aquecendo",
    "15+ rodadas sem Tie — probabilidade aumentando",
    "Padrão de corrida — Banker em sequência longa",
    "Padrão de corrida — Player em sequência longa",
    "Virada identificada após sequência dominante",
    "Padrão de dados próximos — tensão acumulada",
]

BACBO_ROUNDS = [2, 2, 2, 3, 3]

BACBO_CLOSING = [
    "⚠️ Controle a banca e não force entradas.",
    "⚠️ Jogue com responsabilidade e respeite seu limite.",
    "⚠️ Gestão primeiro. Operação sempre com controle.",
    "⚠️ Operação informativa. Use gestão e responsabilidade.",
]

# ============================================================
# ESPORTES — LIGAS PRIORITÁRIAS
# ============================================================
PRIORITY_LEAGUES = [
    "FIFA World Cup",
    "UEFA Champions League",
    "UEFA Europa League",
    "UEFA Europa Conference League",
    "Copa Libertadores",
    "Copa do Brasil",
    "Brazilian Serie A",
    "Brazilian Serie B",
    "English Premier League",
    "La Liga",
    "Bundesliga",
    "Serie A",
    "Ligue 1",
    "Copa America",
    "CONMEBOL",
]

SPORTS_MARKETS = [
    ("Resultado Final", "casa"),
    ("Resultado Final", "fora"),
    ("Resultado Final", "casa"),
    ("Dupla Chance", "casa_empate"),
    ("Ambas Marcam", "sim"),
    ("Ambas Marcam", "nao"),
    ("Mais/Menos Gols", "mais"),
    ("Mais/Menos Gols", "menos"),
    ("Placar Exato", "favorito"),
    ("Placar Exato", "zebra"),
]

PLACARES_FAVORITO = ["1x0", "2x0", "2x1", "3x1", "3x0"]
PLACARES_ZEBRA    = ["0x1", "1x2", "0x2", "1x3", "0x0"]

SPORTS_CLOSING = [
    "⚠️ Analise antes de apostar. Gestão é o que separa o lucro do prejuízo.",
    "⚠️ Jogue com responsabilidade. Aposte só o que pode perder.",
    "⚠️ Odd é referência. Verifique na sua casa de apostas.",
    "⚠️ Gestão primeiro. Nunca ultrapasse 5% da banca por entrada.",
]

COPA_2026_TIPS = [
    (
        "🏆 *Copa do Mundo 2026 — Preparação*\n\n"
        "📅 Data: 11 junho – 19 julho de 2026\n"
        "🌎 Sede: EUA, México e Canadá\n"
        "⚽ 48 seleções pela primeira vez na história\n\n"
        "📌 *Mercado mais lucrativo na Copa:*\n"
        "Resultado ao Vivo (In-Play) — as odds mudam em tempo real.\n"
        "Quem lê o jogo e entra na hora certa lucra mais.\n\n"
        "💡 Dica: Acompanhe aqui os jogos do dia para treinar o olho antes da Copa."
    ),
    (
        "🇧🇷 *Brasil na Copa 2026*\n\n"
        "A Seleção chega como uma das favoritas ao título.\n"
        "Odd atual para o Brasil vencer a Copa: entre 5.00 e 7.00.\n\n"
        "📌 *Como apostar na seleção com segurança:*\n"
        "• Aposte no Brasil em mercados de fase de grupos (menor risco)\n"
        "• Evite apostar no placar exato — volatilidade alta\n"
        "• Mercado Dupla Chance (Brasil ou Empate) paga menos mas protege\n\n"
        "💡 Vamos acompanhar os jogos preparatórios da Seleção aqui."
    ),
    (
        "📊 *Gestão de Banca para Copa 2026*\n\n"
        "A Copa tem 64 jogos ao longo de 39 dias.\n"
        "É uma maratona, não uma corrida.\n\n"
        "📌 *Regras de ouro para a Copa:*\n"
        "• Defina uma banca exclusiva para a Copa\n"
        "• Máximo 3% por entrada nos grupos\n"
        "• Máximo 5% a partir das quartas\n"
        "• Stop loss diário: -15% da banca\n"
        "• Stop win diário: +25% — pare quando atingir\n\n"
        "💡 Quem respeita a banca chega às finais com saldo positivo."
    ),
    (
        "🎯 *Mercados para dominar antes da Copa*\n\n"
        "Os 5 mercados mais populares e rentáveis:\n\n"
        "1️⃣ *Resultado Final (1X2)* — mais simples\n"
        "2️⃣ *Dupla Chance* — cobre 2 dos 3 resultados\n"
        "3️⃣ *Ambas Marcam (BTTS)* — independe de quem vence\n"
        "4️⃣ *Total de Gols* — acima ou abaixo de 2.5\n"
        "5️⃣ *Handicap Asiático* — equilibra jogos desiguais\n\n"
        "💡 Treino começa agora. Acompanha os sinais diários aqui."
    ),
    (
        "⚡ *Favoritos para a Copa 2026*\n\n"
        "🥇 França — elenco mais completo do mundo\n"
        "🥈 Inglaterra — geração Bellingham/Kane no auge\n"
        "🥉 Brasil — Vini Jr e companhia com sede de título\n"
        "4️⃣ Argentina — campeã atual, Messi pode se despedir\n"
        "5️⃣ Espanha — jovens talentos em ascensão\n\n"
        "📌 Odd média para esses 5 vencerem a Copa: 3.50 a 8.00\n\n"
        "💡 Atenção às seleções zebra: Portugal, Alemanha e Uruguai."
    ),
    (
        "🔍 *Como ler uma odd antes de apostar*\n\n"
        "Odd 1.85 no Brasil → para cada R$100 apostados, recebe R$185\n"
        "Lucro real: R$85\n\n"
        "📌 *Fórmula da probabilidade implícita:*\n"
        "1 ÷ odd = probabilidade\n"
        "Odd 2.00 → 50% de chance\n"
        "Odd 3.00 → 33% de chance\n"
        "Odd 1.50 → 67% de chance\n\n"
        "💡 Se você acha que o Brasil tem 70% de chance e a odd é 1.85 (54%), "
        "existe valor nessa aposta."
    ),
]

# ============================================================
# MINES — VARIANTES DE SINAL
# ============================================================
MINES_CONFIGS = [
    {"mines": 3,  "fields": 4, "exit": "4ª abertura"},
    {"mines": 3,  "fields": 3, "exit": "3ª abertura"},
    {"mines": 5,  "fields": 3, "exit": "3ª abertura"},
    {"mines": 5,  "fields": 2, "exit": "2ª abertura"},
    {"mines": 7,  "fields": 2, "exit": "2ª abertura"},
    {"mines": 7,  "fields": 3, "exit": "3ª abertura"},
    {"mines": 10, "fields": 2, "exit": "2ª abertura"},
    {"mines": 3,  "fields": 5, "exit": "5ª abertura"},
    {"mines": 5,  "fields": 4, "exit": "4ª abertura"},
    {"mines": 12, "fields": 2, "exit": "2ª abertura"},
]

MINES_INTRO = [
    "💣 Campo minado — entre com cuidado",
    "💣 Janela identificada no Mines",
    "💣 Configuração validada para entrar",
    "💣 Movimento favorável no Mines agora",
    "💣 Entrada liberada — siga a config",
]

MINES_CLOSING = [
    "⚠️ Gestão primeiro. Operação sempre com controle.",
    "⚠️ Nunca force campo além do indicado. Disciplina é lucro.",
    "⚠️ Jogue com responsabilidade e respeite seu limite.",
    "⚠️ Operação informativa. Use gestão e responsabilidade.",
]

# ============================================================
# ROLETA — VARIANTES DE SINAL
# ============================================================
ROLETA_SIGNALS = [
    {"entrada": "VERMELHO 🔴", "tipo": "Cor"},
    {"entrada": "PRETO ⚫", "tipo": "Cor"},
    {"entrada": "VERMELHO 🔴", "tipo": "Cor"},
    {"entrada": "PRETO ⚫", "tipo": "Cor"},
    {"entrada": "VERMELHO 🔴", "tipo": "Cor"},
    {"entrada": "PRETO ⚫", "tipo": "Cor"},
    {"entrada": "1ª DÚZIA (1–12) 🔢", "tipo": "Dúzia"},
    {"entrada": "2ª DÚZIA (13–24) 🔢", "tipo": "Dúzia"},
    {"entrada": "3ª DÚZIA (25–36) 🔢", "tipo": "Dúzia"},
    {"entrada": "1ª COLUNA 📊", "tipo": "Coluna"},
    {"entrada": "2ª COLUNA 📊", "tipo": "Coluna"},
    {"entrada": "3ª COLUNA 📊", "tipo": "Coluna"},
    {"entrada": "PAR (Even) 🔵", "tipo": "Par/Ímpar"},
    {"entrada": "ÍMPAR (Odd) 🟠", "tipo": "Par/Ímpar"},
    {"entrada": "BAIXO (1–18) ⬇️", "tipo": "Alto/Baixo"},
    {"entrada": "ALTO (19–36) ⬆️", "tipo": "Alto/Baixo"},
]

ROLETA_STRATEGIES = [
    "Bet fixa sem progressão",
    "Flat bet — consistência acima de tudo",
    "Bet conservadora — máx 2% da banca",
    "Bet fixa — não dobrar após perda",
]

ROLETA_CLOSING = [
    "⚠️ Nunca use Martingale na roleta. Bet fixa protege sua banca.",
    "⚠️ Jogue com responsabilidade e respeite seu limite.",
    "⚠️ Gestão primeiro. Sessões curtas = mais consistência.",
    "⚠️ Operação informativa. Use gestão e responsabilidade.",
]

def build_mines_message(plan_date, position):
    seed = f"{plan_date}|mines|{position}"
    config = choose_variant(MINES_CONFIGS, seed + "|config")
    intro = choose_variant(MINES_INTRO, seed + "|intro")
    closing = choose_variant(MINES_CLOSING, seed + "|closing")
    rounds = choose_variant([2, 2, 3, 3, 3], seed + "|rounds")
    hora = now_br().strftime("%H:%M")

    return (
        f"{intro}\n\n"
        f"🕐 {hora}\n"
        f"⚙️ Minas: *{config['mines']}*\n"
        f"📍 Abrir: *{config['fields']} campos*\n"
        f"🚪 Saída: na *{config['exit']}*\n"
        f"⏳ Válido: {rounds} rodadas\n\n"
        f"💰 Gestão: máx 5% da banca por entrada\n\n"
        f"{closing}"
    )

def build_roleta_message(plan_date, position):
    seed = f"{plan_date}|roleta|{position}"
    signal = choose_variant(ROLETA_SIGNALS, seed + "|signal")
    strategy = choose_variant(ROLETA_STRATEGIES, seed + "|strategy")
    closing = choose_variant(ROLETA_CLOSING, seed + "|closing")
    rounds = choose_variant([2, 3, 3, 4], seed + "|rounds")
    hora = now_br().strftime("%H:%M")

    return (
        f"🎡 *Sinal Roleta ao Vivo*\n\n"
        f"🕐 {hora}\n"
        f"🎯 Entrada: *{signal['entrada']}*\n"
        f"📌 Tipo: {signal['tipo']}\n"
        f"📊 Estratégia: {strategy}\n"
        f"⏳ Válido: {rounds} rodadas\n\n"
        f"💰 Gestão: 3% da banca por entrada\n\n"
        f"{closing}"
    )

def fetch_todays_matches():
    today = today_str()
    url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s=Soccer"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get("events") or []
    except Exception:
        return []

def pick_best_match(events):
    if not events:
        return None
    for league_priority in PRIORITY_LEAGUES:
        for event in events:
            league = event.get("strLeague", "")
            if league_priority.lower() in league.lower():
                return event
    return events[0] if events else None

def generate_odds(home_team, away_team, plan_date, position):
    seed = f"{home_team}|{away_team}|{plan_date}|{position}"
    n = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    home_odds = round(1.50 + (n % 130) / 100, 2)
    away_odds = round(1.70 + ((n >> 4) % 160) / 100, 2)
    draw_odds = round(2.80 + ((n >> 8) % 70) / 100, 2)
    return home_odds, draw_odds, away_odds

def build_sports_message(plan_date, position):
    seed = f"{plan_date}|sports|{position}"
    closing = choose_variant(SPORTS_CLOSING, seed + "|closing")
    hora = now_br().strftime("%H:%M")

    events = fetch_todays_matches()
    match = pick_best_match(events)

    if match:
        home = match.get("strHomeTeam", "Casa")
        away = match.get("strAwayTeam", "Visitante")
        league = match.get("strLeague", "Futebol Internacional")
        time_utc = match.get("strTime", "")

        if time_utc:
            try:
                h, m = time_utc.replace(".", ":").split(":")[:2]
                br_h = (int(h) - 3) % 24
                match_time = f"{br_h:02d}:{m}"
            except Exception:
                match_time = hora
        else:
            match_time = hora

        home_odds, draw_odds, away_odds = generate_odds(home, away, plan_date, position)

        market_idx = int(hashlib.sha256((seed + "|market").encode()).hexdigest(), 16) % len(SPORTS_MARKETS)
        market, side = SPORTS_MARKETS[market_idx]

        aviso_risco = ""
        if market == "Resultado Final":
            if side == "casa":
                entry = f"{home} vence"
                odd = f"{home_odds:.2f}"
            else:
                entry = f"{away} vence"
                odd = f"{away_odds:.2f}"
        elif market == "Dupla Chance":
            entry = f"{home} ou Empate"
            odd = f"{round(home_odds * 0.65, 2):.2f}"
        elif market == "Ambas Marcam":
            entry = "Sim" if side == "sim" else "Não"
            odd = f"{round(1.60 + (int(seed[:4], 16) % 40) / 100, 2):.2f}"
        elif market == "Mais/Menos Gols":
            if side == "mais":
                entry = "Mais de 2.5 gols"
                odd = f"{round(1.70 + (int(seed[:4], 16) % 50) / 100, 2):.2f}"
            else:
                entry = "Menos de 2.5 gols"
                odd = f"{round(1.55 + (int(seed[:4], 16) % 40) / 100, 2):.2f}"
        else:
            placar = choose_variant(PLACARES_FAVORITO if side == "favorito" else PLACARES_ZEBRA, seed + "|placar")
            if side == "favorito":
                entry = f"{home} {placar}"
                odd = f"{round(4.50 + (int(seed[:4], 16) % 300) / 100, 2):.2f}"
            else:
                entry = f"{away} {placar.split('x')[1]}x{placar.split('x')[0]}"
                odd = f"{round(7.00 + (int(seed[:4], 16) % 500) / 100, 2):.2f}"
            aviso_risco = "\n⚡ Placar exato — odd alta, risco alto. Use no máx 1% da banca."

        return (
            f"⚽ *Sinal Esportes*\n\n"
            f"🏆 {league}\n"
            f"🆚 *{home}* x *{away}*\n"
            f"🕐 {match_time} (horário de Brasília)\n\n"
            f"📌 Mercado: {market}\n"
            f"🎯 Entrada: {entry}\n"
            f"📊 Odd de referência: *{odd}*\n"
            f"💰 Gestão: 3% da banca{aviso_risco}\n\n"
            f"{closing}"
        )
    else:
        tip = choose_variant(COPA_2026_TIPS, seed + "|copa")
        return tip + f"\n\n{closing}"

# ============================================================
# UTILITÁRIOS
# ============================================================
def now_br():
    return datetime.now(APP_TZ)

def today_str():
    return now_br().strftime("%Y-%m-%d")

def parse_hhmm(hhmm):
    h, m = hhmm.split(":")
    return int(h), int(m)

def choose_variant(items, seed_key):
    idx = int(hashlib.sha256(seed_key.encode("utf-8")).hexdigest(), 16) % len(items)
    return items[idx]

def infer_game_type(provider, name):
    n = name.lower()
    p = provider.lower()
    if "mines" in n: return "mines"
    if "aviator" in n: return "aviator"
    if "hi-lo" in n or "hilo" in n or "hi lo" in n: return "hilo"
    if "limbo" in n: return "limbo"
    if "plinko" in n: return "plinko"
    if "scratch" in n: return "scratch"
    if "heads tails" in n or "heads & tails" in n: return "coin_flip"
    if "lucky wheel" in n or n == "wheel": return "wheel"
    if "penalty" in n: return "penalty"
    if "tower" in n: return "tower"
    if "roulette" in n: return "roulette"
    if "bingo" in n: return "bingo"
    if "blackjack" in n: return "blackjack"
    if "baccarat" in n or "bac bo" in n: return "baccarat"
    if "darts" in n: return "darts"
    if "racing" in n or "horse racing" in n: return "racing"
    if "keno" in n: return "keno"
    if "runner" in n or "uncrossable" in n: return "runner"
    if "dice" in n or "crash" in n or "rocket" in n: return "crash"
    if p in {x.lower() for x in CRASH_PROVIDERS}: return "crash"
    return "slot"

def choose_strategy_key(game_type, position):
    mapping = {
        "mines": "mines", "crash": "crash", "aviator": "crash",
        "hilo": "hilo", "limbo": "limbo", "plinko": "plinko",
        "scratch": "scratch", "coin_flip": "coin_flip", "wheel": "wheel",
        "penalty": "penalty", "tower": "tower", "dice": "dice",
        "grid_slot": "grid_slot", "keno": "keno", "roulette": "roulette",
        "runner": "runner", "baccarat": "baccarat", "blackjack": "blackjack",
        "racing": "racing", "bingo": "bingo", "darts": "darts",
    }
    if game_type in mapping:
        return mapping[game_type]
    return ["slots_leve", "slots_media", "slots_agressiva"][position % 3]

# ============================================================
# BANCO DE DADOS
# ============================================================
def db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()

    # Tabela de jogos compartilhada com o bot Telegram (mesmos dados)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,
            rtp TEXT DEFAULT '',
            emoji TEXT DEFAULT '🎰',
            game_type TEXT DEFAULT 'slot',
            UNIQUE(name, provider)
        )
    """)

    # Tabela exclusiva do bot WhatsApp (prefixo wa_ evita conflito)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wa_daily_plan (
            id SERIAL PRIMARY KEY,
            room TEXT NOT NULL,
            plan_date TEXT NOT NULL,
            position INTEGER NOT NULL,
            game_id INTEGER,
            send_at TEXT NOT NULL,
            sent INTEGER DEFAULT 0,
            sent_at TEXT DEFAULT '',
            wa_status TEXT DEFAULT '',
            locked_at TEXT DEFAULT '',
            UNIQUE(room, plan_date, position)
        )
    """)

    conn.commit()

    for provider, items in PROVIDER_GAMES.items():
        for name, rtp, emoji in items:
            game_type = infer_game_type(provider, name)
            try:
                cur.execute("""
                    INSERT INTO games (name, provider, rtp, emoji, game_type)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT(name, provider) DO NOTHING
                """, (name, provider, rtp, emoji, game_type))
            except Exception:
                pass

    conn.commit()
    cur.close()
    conn.close()

# ============================================================
# PLANEJAMENTO DIÁRIO
# ============================================================
def build_send_slots_for_room(room_name, day_str):
    room = ROOMS[room_name]
    day_obj = datetime.strptime(day_str, "%Y-%m-%d").date()
    seed_int = int(hashlib.sha256(f"{day_str}_{room_name}_times".encode()).hexdigest(), 16)
    rng = random.Random(seed_int)

    all_slots = []
    for (start_hhmm, end_hhmm) in room["windows"]:
        sh, sm = parse_hhmm(start_hhmm)
        eh, em = parse_hhmm(end_hhmm)
        start_dt = datetime(day_obj.year, day_obj.month, day_obj.day, sh, sm, 0, tzinfo=APP_TZ)
        end_dt = datetime(day_obj.year, day_obj.month, day_obj.day, eh, em, 0, tzinfo=APP_TZ)
        current = start_dt
        while current <= end_dt:
            all_slots.append(current)
            minutes = rng.randint(room["min_interval"], room["max_interval"])
            seconds = rng.randint(0, 59)
            current += timedelta(minutes=minutes, seconds=seconds)

    all_slots.sort()
    return all_slots

def ensure_daily_plan(room_name, day_str):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) AS total FROM wa_daily_plan WHERE room = %s AND plan_date = %s",
        (room_name, day_str)
    )
    if cur.fetchone()["total"] > 0:
        cur.close()
        conn.close()
        return

    slots = build_send_slots_for_room(room_name, day_str)
    if not slots:
        cur.close()
        conn.close()
        return

    if room_name == "slots":
        cur.execute(
            "SELECT id FROM games WHERE name NOT IN ('Aviator', 'Bac Bo') ORDER BY provider, name"
        )
        games = list(cur.fetchall())
        if not games:
            cur.close()
            conn.close()
            return
        seed_int = int(hashlib.sha256(f"{day_str}_slots_games".encode()).hexdigest(), 16)
        rng = random.Random(seed_int)
        rng.shuffle(games)
        needed = len(slots)
        selected = []
        while len(selected) < needed:
            tmp = list(games)
            rng.shuffle(tmp)
            selected.extend(tmp)
        selected = selected[:needed]

        for position, game_row in enumerate(selected, start=1):
            send_at = slots[position - 1].strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO wa_daily_plan (room, plan_date, position, game_id, send_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(room, plan_date, position) DO NOTHING
            """, (room_name, day_str, position, game_row["id"], send_at))
    else:
        for position, slot_dt in enumerate(slots, start=1):
            send_at = slot_dt.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO wa_daily_plan (room, plan_date, position, game_id, send_at)
                VALUES (%s, %s, %s, NULL, %s)
                ON CONFLICT(room, plan_date, position) DO NOTHING
            """, (room_name, day_str, position, send_at))

    conn.commit()
    cur.close()
    conn.close()

def get_due_items(room_name, limit=1):
    day_str = today_str()
    ensure_daily_plan(room_name, day_str)

    now_dt = now_br()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    cutoff = (now_dt - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    lock_cutoff = (now_dt - timedelta(seconds=LOCK_TIMEOUT)).strftime("%Y-%m-%d %H:%M:%S")

    conn = db()
    cur = conn.cursor()

    if room_name == "slots":
        cur.execute("""
            SELECT dp.id, dp.room, dp.plan_date, dp.position, dp.send_at,
                   g.id AS game_id, g.name AS game_name, g.provider,
                   g.rtp, g.emoji, g.game_type
            FROM wa_daily_plan dp
            JOIN games g ON g.id = dp.game_id
            WHERE dp.room = %s AND dp.plan_date = %s
              AND dp.sent = 0
              AND dp.send_at <= %s AND dp.send_at >= %s
              AND (dp.locked_at = '' OR dp.locked_at <= %s)
            ORDER BY dp.position ASC LIMIT %s
        """, (room_name, day_str, now_str, cutoff, lock_cutoff, limit))
    else:
        cur.execute("""
            SELECT id, room, plan_date, position, send_at
            FROM wa_daily_plan
            WHERE room = %s AND plan_date = %s
              AND sent = 0
              AND send_at <= %s AND send_at >= %s
              AND (locked_at = '' OR locked_at <= %s)
            ORDER BY position ASC LIMIT %s
        """, (room_name, day_str, now_str, cutoff, lock_cutoff, limit))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def try_lock(item_id):
    now_str = now_br().strftime("%Y-%m-%d %H:%M:%S")
    lock_cutoff = (now_br() - timedelta(seconds=LOCK_TIMEOUT)).strftime("%Y-%m-%d %H:%M:%S")
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE wa_daily_plan SET locked_at = %s
            WHERE id = %s AND sent = 0 AND (locked_at = '' OR locked_at <= %s)
        """, (now_str, item_id, lock_cutoff))
        conn.commit()
        ok = cur.rowcount == 1
    except Exception:
        conn.rollback()
        ok = False
    cur.close()
    conn.close()
    return ok

def mark_sent(item_id, status):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE wa_daily_plan SET sent = 1, sent_at = %s, wa_status = %s, locked_at = ''
        WHERE id = %s
    """, (now_br().strftime("%Y-%m-%d %H:%M:%S"), status, item_id))
    conn.commit()
    cur.close()
    conn.close()

# ============================================================
# GERAÇÃO DE MENSAGENS
# ============================================================
def build_slots_message(plan_date, position, game_row):
    game_id = game_row["game_id"]
    seed = f"{plan_date}|{game_id}"
    intro = choose_variant(INTRO_VARIANTS, seed + "|intro")
    closing = choose_variant(CLOSING_VARIANTS, seed + "|closing")
    strategy_key = choose_strategy_key(game_row["game_type"], position)
    strategy_text = choose_variant(STRATEGY_VARIANTS[strategy_key], seed + "|strategy")

    provider_line = f"🏢 Provedora: {game_row['provider']}\n" if game_row["provider"] else ""
    rtp_line = f"📊 RTP: {game_row['rtp']}\n" if game_row["rtp"] else "📊 RTP: Verificado ✅\n"
    megaways_line = "⚡ Mecânica: MEGAWAYS — rolos expansíveis, alta volatilidade!\n" if "megaways" in game_row["game_name"].lower() else ""

    return (
        f"{intro}\n\n"
        f"🎮 Jogo: {game_row['game_name']} {game_row['emoji']}\n"
        f"{provider_line}"
        f"{rtp_line}"
        f"{megaways_line}\n"
        f"{strategy_text}\n\n"
        f"{closing}"
    )

def build_aviator_message(plan_date, position):
    seed = f"{plan_date}|aviator|{position}"
    signal = choose_variant(AVIATOR_SIGNALS, seed + "|signal")
    closing = choose_variant(AVIATOR_CLOSING, seed + "|closing")
    hora = now_br().strftime("%H:%M")

    return (
        f"✈️ *Sinal Aviator*\n\n"
        f"🕐 {hora}\n"
        f"📌 {signal['strategy']}\n"
        f"{signal['body']}\n\n"
        f"{closing}"
    )

def build_bacbo_message(plan_date, position):
    seed = f"{plan_date}|bacbo|{position}"
    side, confidence = choose_variant(BACBO_SIDES, seed + "|side")
    pattern = choose_variant(BACBO_PATTERNS, seed + "|pattern")
    closing = choose_variant(BACBO_CLOSING, seed + "|closing")
    rounds = choose_variant(BACBO_ROUNDS, seed + "|rounds")
    hora = now_br().strftime("%H:%M")

    return (
        f"🎲 *Sinal BacBo*\n\n"
        f"🕐 {hora}\n"
        f"🎯 Entrada: *{side}*\n"
        f"📊 Confiança: {confidence}\n"
        f"💡 {pattern}\n"
        f"⏳ Válido: {rounds} rodadas\n\n"
        f"{closing}"
    )

# ============================================================
# EVOLUTION API
# ============================================================
def evolution_send(jid, text):
    url = f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    payload = {"number": jid, "text": text}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        ok = resp.status_code in (200, 201)
        return ok, str(resp.status_code)
    except Exception as e:
        return False, str(e)[:200]

# ============================================================
# SCHEDULER
# ============================================================
def scheduler_loop():
    time.sleep(8)
    try:
        init_db()
    except Exception as e:
        print(f"[DB INIT ERROR] {e}")

    while True:
        try:
            tomorrow = (now_br().date() + timedelta(days=1)).strftime("%Y-%m-%d")
            for room_name in ROOMS:
                try:
                    ensure_daily_plan(room_name, tomorrow)
                except Exception:
                    pass

            for room_name, room_cfg in ROOMS.items():
                try:
                    due = get_due_items(room_name, limit=1)
                    for item in due:
                        if not try_lock(item["id"]):
                            continue

                        if room_name == "slots":
                            msg = build_slots_message(item["plan_date"], item["position"], item)
                        elif room_name == "aviator":
                            msg = build_aviator_message(item["plan_date"], item["position"])
                        elif room_name == "bacbo":
                            msg = build_bacbo_message(item["plan_date"], item["position"])
                        elif room_name == "sports":
                            msg = build_sports_message(item["plan_date"], item["position"])
                        elif room_name == "mines":
                            msg = build_mines_message(item["plan_date"], item["position"])
                        else:
                            msg = build_roleta_message(item["plan_date"], item["position"])

                        ok, status = evolution_send(room_cfg["jid"], msg)
                        mark_sent(item["id"], "ok" if ok else "erro")
                        print(f"[{room_name.upper()}] pos={item['position']} status={status}")
                except Exception as e:
                    print(f"[ROOM ERROR] {room_name}: {e}")

        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")

        time.sleep(SCHEDULER_SLEEP)

# ============================================================
# FLASK
# ============================================================
app = Flask(__name__)

ROOM_META = {
    "slots":   {"emoji": "🎰", "label": "Slots",    "janela": "00h – 23h59"},
    "aviator": {"emoji": "✈️", "label": "Aviator",  "janela": "10h / 15h / 20h"},
    "bacbo":   {"emoji": "🎲", "label": "BacBo",    "janela": "10h / 14h / 20h"},
    "sports":  {"emoji": "⚽", "label": "Esportes", "janela": "9h / 14h / 19h"},
    "mines":   {"emoji": "💣", "label": "Mines",    "janela": "10h / 14h / 19h"},
    "roleta":  {"emoji": "🎡", "label": "Roleta",   "janela": "14h / 19h"},
}

@app.route("/")
def health():
    return "Bot WhatsApp Sinais — Rainha Games OK", 200

@app.route("/rebuild/<room>")
def rebuild_room(room):
    if room not in ROOMS:
        return jsonify({"error": "sala inválida"}), 400
    try:
        day = today_str()
        room_cfg = ROOMS[room]
        conn = db()
        cur = conn.cursor()

        # Deletar plano do dia e recriar
        cur.execute("DELETE FROM wa_daily_plan WHERE room = %s AND plan_date = %s", (room, day))
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()

        ensure_daily_plan(room, day)

        # Reagendar itens com send_at no passado para começar agora
        conn = db()
        cur = conn.cursor()
        now_dt = now_br()
        cur.execute("""
            SELECT id FROM wa_daily_plan
            WHERE room = %s AND plan_date = %s AND sent = 0
              AND send_at <= %s
            ORDER BY send_at ASC
        """, (room, day, now_dt.strftime("%Y-%m-%d %H:%M:%S")))
        past = cur.fetchall()

        min_i = room_cfg["min_interval"]
        for i, item in enumerate(past):
            new_time = (now_dt + timedelta(minutes=min_i * (i + 1))).strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE wa_daily_plan SET send_at = %s WHERE id = %s", (new_time, item["id"]))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "ok": True, "room": room,
            "removidos": deleted,
            "reagendados": len(past),
            "msg": f"Plano recriado — {len(past)} sinais reagendados a partir de agora"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status")
def status():
    try:
        conn = db()
        cur = conn.cursor()
        cur.execute("""
            SELECT room,
                   COUNT(*) AS total,
                   SUM(sent) AS enviados,
                   SUM(CASE WHEN wa_status = 'erro' THEN 1 ELSE 0 END) AS erros
            FROM wa_daily_plan
            WHERE plan_date = %s
            GROUP BY room
        """, (today_str(),))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        data = {r["room"]: {"total": r["total"], "enviados": int(r["enviados"] or 0), "erros": int(r["erros"] or 0)} for r in rows}

        now_str = now_br().strftime("%d/%m/%Y %H:%M")

        cards = ""
        for room, meta in ROOM_META.items():
            d = data.get(room, {"total": 0, "enviados": 0, "erros": 0})
            total = d["total"]
            enviados = d["enviados"]
            erros = d["erros"]
            pct = round((enviados / total * 100) if total > 0 else 0)
            status_color = "#22c55e" if erros == 0 else "#ef4444"
            status_text = "Online" if erros == 0 else f"{erros} erro(s)"
            cards += f"""
            <div class="card">
                <div class="card-header">
                    <span class="emoji">{meta['emoji']}</span>
                    <div>
                        <div class="room-name">{meta['label']}</div>
                        <div class="janela">{meta['janela']}</div>
                    </div>
                    <span class="badge" style="background:{status_color}">{status_text}</span>
                </div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-val">{enviados}</div>
                        <div class="stat-lbl">Enviados</div>
                    </div>
                    <div class="stat">
                        <div class="stat-val">{total}</div>
                        <div class="stat-lbl">Planejados</div>
                    </div>
                    <div class="stat">
                        <div class="stat-val">{pct}%</div>
                        <div class="stat-lbl">Progresso</div>
                    </div>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width:{pct}%"></div>
                </div>
            </div>"""

        total_enviados = sum(d.get("enviados", 0) for d in data.values())
        total_planejados = sum(d.get("total", 0) for d in data.values())
        total_erros = sum(d.get("erros", 0) for d in data.values())

        html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rainha Games — Monitor de Sinais</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0B0B0F; color:#fff; font-family:'Segoe UI',sans-serif; min-height:100vh; padding:24px 16px; }}
  .header {{ text-align:center; margin-bottom:32px; }}
  .crown {{ font-size:48px; }}
  h1 {{ font-size:24px; color:#D4AF37; font-weight:700; margin:8px 0 4px; }}
  .subtitle {{ color:#888; font-size:13px; }}
  .summary {{ display:flex; gap:12px; justify-content:center; margin-bottom:28px; flex-wrap:wrap; }}
  .sum-box {{ background:#1a1a24; border:1px solid #2a2a3a; border-radius:12px; padding:14px 24px; text-align:center; min-width:120px; }}
  .sum-val {{ font-size:28px; font-weight:700; color:#D4AF37; }}
  .sum-lbl {{ font-size:12px; color:#888; margin-top:2px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; max-width:1000px; margin:0 auto; }}
  .card {{ background:#1a1a24; border:1px solid #2a2a3a; border-radius:16px; padding:20px; }}
  .card-header {{ display:flex; align-items:center; gap:12px; margin-bottom:16px; }}
  .emoji {{ font-size:32px; }}
  .room-name {{ font-size:16px; font-weight:700; color:#fff; }}
  .janela {{ font-size:11px; color:#888; margin-top:2px; }}
  .badge {{ margin-left:auto; font-size:11px; font-weight:600; padding:4px 10px; border-radius:20px; color:#fff; white-space:nowrap; }}
  .stats {{ display:flex; gap:8px; margin-bottom:12px; }}
  .stat {{ flex:1; background:#0B0B0F; border-radius:10px; padding:10px; text-align:center; }}
  .stat-val {{ font-size:20px; font-weight:700; color:#D4AF37; }}
  .stat-lbl {{ font-size:10px; color:#888; margin-top:2px; }}
  .bar-bg {{ background:#0B0B0F; border-radius:999px; height:6px; overflow:hidden; }}
  .bar-fill {{ background:linear-gradient(90deg,#B3001B,#D4AF37); height:100%; border-radius:999px; transition:width .5s; }}
  .footer {{ text-align:center; margin-top:32px; color:#555; font-size:12px; }}
  .dot {{ display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%; margin-right:6px; animation:pulse 2s infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.4}} }}
</style>
</head>
<body>
<div class="header">
  <div class="crown">👑</div>
  <h1>RAINHA GAMES</h1>
  <div class="subtitle"><span class="dot"></span>Monitor de Sinais — {now_str}</div>
</div>
<div class="summary">
  <div class="sum-box"><div class="sum-val">{total_enviados}</div><div class="sum-lbl">Sinais enviados hoje</div></div>
  <div class="sum-box"><div class="sum-val">{total_planejados}</div><div class="sum-lbl">Planejados hoje</div></div>
  <div class="sum-box"><div class="sum-val" style="color:{'#22c55e' if total_erros==0 else '#ef4444'}">{total_erros}</div><div class="sum-lbl">Erros</div></div>
  <div class="sum-box"><div class="sum-val">{len(ROOM_META)}</div><div class="sum-lbl">Salas ativas</div></div>
</div>
<div class="grid">{cards}</div>
<div class="footer">Atualiza automaticamente — recarregue a página para ver o status mais recente</div>
<script>setTimeout(()=>location.reload(), 60000)</script>
</body>
</html>"""
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return f"<h1 style='color:red'>Erro: {e}</h1>", 500

_started = False

@app.before_request
def start_once():
    global _started
    if not _started:
        _started = True
        t = threading.Thread(target=scheduler_loop, daemon=True)
        t.start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
