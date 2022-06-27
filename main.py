import random
import telebot
from telebot import types
import personalSettings as ps

class NotifyEvent(object):
    lines = list()
    countRooms = int(0)
    countKills = int(0)
    countDrunkPotion = int(0)
    countTakeDamage = int(0)
    countGiveDamage = int(0)
    countRegenPoints = int(0)

    def addMessage(self, m):
        self.lines.append(m)

    def __repr__(self):
        txt = ""
        for i in self.lines:
            txt += (i) + "\n"
        return txt+"\n"

    def clearLines(self):
        self.lines.clear()

    def clearStatictic(self):
        self.countRooms = int(0)
        self.countKills = int(0)
        self.countDrunkPotion = int(0)
        self.countTakeDamage = int(0)
        self.countGiveDamage = int(0)
        self.countRegenPoints = int(0)

    def statistic(self):
        return "\n" \
               "count reserch rooms: {0}\n" \
               "count kills: {1}\n" \
               "count use HP potion: {2}\n" \
               "count damage which player take: {3}\n" \
               "count damage which player give: {4}\n" \
               "count regen hp points: {5}\n".format(self.countRooms, self.countKills, self.countDrunkPotion,
                                                   self.countTakeDamage, self.countGiveDamage, self.countRegenPoints)

class Enemy(object):
    def __init__(self, d, h):
        self.damage = d
        self.hp = h

    def deadCheck(self):
        if self.hp < 1:
            return True
        else:
            return False

    def atak(self, player):
        if not self.deadCheck():
            player.curHp -= self.damage
            notifyEvent.countTakeDamage += self.damage
            notifyEvent.addMessage("you TAKE {0} damage".format(self.damage))

    def __repr__(self):
        if self.deadCheck():
            print("1")
            return "enemy dead"
        else:
            return "enemy hp: {0}\n" \
                   "enemy damage: {1}".format(self.hp,self.damage)

class Player(object):
    def __init__(self, mh, ch, c, d, hp, df=1, r=2):
        self.maxHp = mh
        self.curHp = ch
        self.coins = c
        self.damage = d
        self.hpPotion = hp
        self.damageFactor = df
        self.regenPower = r

    def avgHp(self):
        return int((self.maxHp+self.curHp)/2)

    def __repr__(self):
        return "HP: {0}/{1}\n" \
               "DAMAGE: {2}\n" \
               "COINS: {3}\n" \
               "HP POTION: {4}\n" \
               "POTION REGEN: {5}\n\n".format(self.curHp, self.maxHp, self.damage, self.coins, self.hpPotion,self.regenPower)

    def atak(self, enemy):
        enemy.hp -= self.damage * self.damageFactor
        notifyEvent.countGiveDamage += self.damage * self.damageFactor
        notifyEvent.addMessage("you GIVE {0} damage".format(self.damage * self.damageFactor))
        self.damageFactor = 1

    def deadCheck(self):
        return self.curHp < 1

    def dodge(self, enemy):
        if random.randint(1, 2) == 1:
            self.damageFactor = 2
            notifyEvent.addMessage("you dodge, you can hit in bag, use potion or escape from enemy")
        else:
            notifyEvent.addMessage("you not dodge, loser")
            enemy.atak(self)

    def useHpPotion(self):
        notifyEvent.addMessage("you regen {0} health points".format(self.regenPower))
        self.hpPotion -= 1
        notifyEvent.countRegenPoints+=self.regenPower
        self.curHp += self.regenPower
        self.curHp = self.maxHp if self.curHp > self.maxHp else self.curHp


bot = telebot.TeleBot(ps.token)
notifyEvent = NotifyEvent()
pl = Player(10, 10, 0, 2, 3)
en = Enemy(5, 10)


def createEnemy(player):
    playerPower=(int(player.curHp+player.damage)/2)-2
    enemyDamage=int(1)
    enemyHp=int(1)
    while playerPower>0:
        if random.randint(0,1)==0:
            enemyDamage+=1
        else:
            enemyHp+=1
        playerPower-=1
    return Enemy(enemyDamage,enemyHp)

def gameEnd(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    itembtn1 = types.InlineKeyboardButton('restart', callback_data='rest')
    markup.add(itembtn1)
    messageFromBot = str(notifyEvent) + str(pl) + str(en) + notifyEvent.statistic()
    notifyEvent.clearLines()
    # bot.send_message(message.chat.id, messageFromBot, reply_markup=markup)
    bot.edit_message_text(text=messageFromBot, chat_id=message.chat.id, message_id=message.message_id,reply_markup=markup)

def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton('next room', callback_data='nr')
    itembtn2 = types.InlineKeyboardButton('quit', callback_data='q')
    itembtn3 = types.InlineKeyboardButton('use hp Potion', callback_data='uhpe')
    markup.add(itembtn1, itembtn2, itembtn3)

    messageFromBot = str(notifyEvent) + str(pl)
    notifyEvent.clearLines()
    bot.send_message(message.chat.id, messageFromBot, reply_markup=markup)

def emptyPlace(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton('next room', callback_data='nr')
    itembtn2 = types.InlineKeyboardButton('quit', callback_data='q')
    itembtn3 = types.InlineKeyboardButton('use hp Potion', callback_data='uhpe')
    markup.add(itembtn1, itembtn2, itembtn3)

    messageFromBot = str(notifyEvent) + str(pl)
    notifyEvent.clearLines()
    bot.edit_message_text(text=messageFromBot,chat_id=message.chat.id,message_id=message.message_id,reply_markup=markup)

def fightPlace(message):
    if en.deadCheck():
        notifyEvent.addMessage(str(en))
        pl.coins += 1
        notifyEvent.countKills += 1
        emptyPlace(message)
        return
    if pl.deadCheck():
        gameEnd(message)
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton('atack', callback_data='a')
    itembtn2 = types.InlineKeyboardButton('dodge', callback_data='d')
    itembtn3 = types.InlineKeyboardButton('use hp Potion', callback_data='uhpf')
    markup.add(itembtn1, itembtn2, itembtn3)
    messageFromBot = str(notifyEvent) + str(pl) + str(en)
    notifyEvent.clearLines()
    bot.edit_message_text(text=messageFromBot, chat_id=message.chat.id, message_id=message.message_id,reply_markup=markup)
    # bot.send_message(message.chat.id, messageFromBot, reply_markup=markup)

def playerCanDodge(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton('atack', callback_data='da')
    itembtn2 = types.InlineKeyboardButton('escape', callback_data='de')
    itembtn3 = types.InlineKeyboardButton('use hp Potion', callback_data='uhpd')
    markup.add(itembtn1, itembtn2, itembtn3)
    messageFromBot = str(notifyEvent) + str(pl) + str(en)
    notifyEvent.clearLines()
    bot.edit_message_text(text=messageFromBot, chat_id=message.chat.id, message_id=message.message_id,reply_markup=markup)
    # bot.send_message(message.chat.id, messageFromBot, reply_markup=markup)

def lifeAltarPlace(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton('potion power', callback_data='pu')
    itembtn2 = types.InlineKeyboardButton('max hp', callback_data='hu')
    markup.add(itembtn1, itembtn2)
    messageFromBot = "you find life altar.\nWhat do you want to improve?"
    notifyEvent.clearLines()
    bot.edit_message_text(text=messageFromBot, chat_id=message.chat.id, message_id=message.message_id,reply_markup=markup)
    # bot.send_message(message.chat.id, messageFromBot, reply_markup=markup)

@bot.message_handler(commands=['start','s'])
def send_welcome(message):
    welcome(message)

def chestPlace(message):
    messageFromBot = "you find chest.\n"
    choose=random.randint(0,2)
    if choose == 0:
        messageFromBot+="you found new weapon in chest"
        pl.damage+=1
    elif choose == 1:
        messageFromBot += "you found coins in chest"
        pl.coins+=1
    else:
        countPotion=random.randint(1,2)
        messageFromBot+= "you found {0} hp potion in chest".format(countPotion)
        pl.hpPotion+=countPotion
    notifyEvent.addMessage(messageFromBot)
    # bot.send_message(message.chat.id, messageFromBot)
    emptyPlace(message)

def roomsGenerator(message):
    fortuna=random.randint(1,4)
    global en
    if fortuna >= 3:
        en = createEnemy(pl)
        notifyEvent.addMessage("you find enemy in room")
        fightPlace(message)
    elif fortuna == 2:
        chestPlace(message)
    elif fortuna == 1:
        lifeAltarPlace(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global pl
    global en
    global notifyEvent
    if call.data == 'nr':
        notifyEvent.countRooms += 1
        roomsGenerator(call.message)
    elif call.data == 'q':
        gameEnd(call.message)
    elif call.data.startswith('uhp'):
        if pl.hpPotion!=0:
            pl.useHpPotion()
            notifyEvent.countDrunkPotion += 1
            if call.data[-1]=='e':
                emptyPlace(call.message)
            elif call.data[-1]=='f':
                en.atak(pl)
                fightPlace(call.message)
            elif call.data[-1]=='d':
                fightPlace(call.message)
    elif call.data == 'a':
        if not en.deadCheck():
            pl.atak(en)
            en.atak(pl)
            fightPlace(call.message)
        else:
            emptyPlace(call.message)
    elif call.data == 'd':
        if not en.deadCheck():
            pl.dodge(en)
            if pl.damageFactor == 2:
                playerCanDodge(call.message)
            else:
                fightPlace(call.message)
        else:
            emptyPlace(call.message)
    elif call.data == 'da':
        if not en.deadCheck():
            pl.atak(en)
            fightPlace(call.message)
        else:
            emptyPlace(call.message)
    elif call.data == 'de':
        notifyEvent.addMessage('you escape from enemy')
        emptyPlace(call.message)
        pl.damageFactor = 1
    elif call.data == 'rest':
        pl = Player(10, 10, 0, 2, 3)
        notifyEvent.clearLines()
        notifyEvent.clearStatictic()
        emptyPlace(call.message)
    elif call.data == 'pu':
        pl.regenPower+=1
        notifyEvent.addMessage("you level up regen potion power")
        emptyPlace(call.message)
    elif call.data == 'hu':
        pl.maxHp+=1
        pl.curHp=pl.maxHp
        notifyEvent.addMessage("you level up max Hp")
        emptyPlace(call.message)
    elif call.data == 'du':
        pl.maxHp+=1
        pl.curHp=pl.maxHp
        notifyEvent.addMessage("you level up max Hp")
        emptyPlace(call.message)
    elif call.data == 'tc':
        pl.maxHp+=1
        pl.curHp=pl.maxHp
        notifyEvent.addMessage("you level up max Hp")
        emptyPlace(call.message)

bot.infinity_polling()