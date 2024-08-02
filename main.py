from javascript import require, On, Once, AsyncTask, once, off
import settings as st

# модуль для быстрого создания вектора - v(x,y,z)
v = require('vec3')

# подгрузка mineflayer и его компонентов 
mineflayer = require('mineflayer')
inventoryViewer = require('mineflayer-web-inventory')
pathfinder = require('mineflayer-pathfinder').pathfinder
Movements = require('mineflayer-pathfinder').Movements

# создание бота, его заход на сервер, настройки в settings.py
bot = mineflayer.createBot(st.options_for_bot)
bot.loadPlugin(pathfinder)

# подгрузка модуля для работы с блоками, тыкнул сюда, т.к. нужно сразу к боту подкючить (мб можно и раньше в коде сделать, хз, в апи такой пример)
Block = require('prismarine-block')(bot.registry)

# пример для создания блока
block_diam = Block.fromString("diamond_block", 14)

# функция, которая проверяет в радиусе maxDistance наличие блоков, id которых заданно в options_for_digging['matching'] и вскапывает их
# debug для записи в консоль инфы, можно убрать
def check_and_dig(marker=0):
    place_leg_block = False
    options = {'matching': st.options_for_digging['matching'], 
               'point': bot.entity.position,
               'count': st.options_for_digging['count'], 
               'maxDistance': st.options_for_digging['maxDistance']}
    
    # функция findBlock на выходе дает массив координат
    treasure = bot.findBlocks(options)
    # поэтому превращаем массив координат в массив блоков
    to_dig = []
    for item in treasure:
        if bot.entity.position.y > item.y:
            if marker == 1:
                continue
            place_leg_block = True
            print(item)
            bot.chat('found!')
        elif bot.entity.position.z < item.z:
            continue
        print(item)
        to_dig.append(bot.blockAt(item))
    # затем вскапываем
    for block in to_dig:
        bot.dig(block)
    if place_leg_block == True:
        bot.equip(27, 'hand')
        bot.look(st.yaw_radians, st.simple_bridge_pitch)
        block_hole = bot.blockAtCursor()
        bot.placeBlock(block_hole, v(0,0,-1))
        bot.equip(841, 'hand')
        

# приветствие
def greetings():
    bot.chat('Привет, меня зовут Шахтерин, я был создан ради добычи полезных ископаемых!')
    bot.chat('Чем могу помочь?')

# ходьба через состояния...
def go_forw_one_block():
    bot.setControlState('forward', True)
    bot.waitForTicks(10)
    bot.clearControlStates()

def dig_upper_block():
    bot.look(st.yaw_radians, 0)
    block_forw = bot.blockAtCursor()
    bot.dig(block_forw)
    check_and_dig(marker=1)

def dig_lower_block():
    bot.look(st.yaw_radians, st.pitch_radians)
    block_forw = bot.blockAtCursor()
    bot.dig(block_forw)
    check_and_dig(marker=0)

# алгоритм копания
def mine():
    dig_upper_block()
    dig_lower_block()
    go_forw_one_block()
    

    
# что происходит, когда бот спавнится
@On(bot, 'spawn')
def handle(*args):
    greetings()

    # обработка сообщений в чате
    @On(bot, 'chat')
    def handleMsg(this, sender, message, *args):
        if sender != st.BOT_USERNAME and message == 'dig':
            print('Got message to dig from', sender)
            bot.equip(841, 'hand')  
            temp = 0
            # back_to = bot.entity.position - забацать позицию, чтоб к ней вернутся (СДЕЛАТЬ ПОЗЖЕ)
            while True:
                mine()
                temp += 1
                if temp == st.num_of_blocks:
                    break    
        # web inventory viewer 
        elif sender != st.BOT_USERNAME and message == 'open pocket':
            inventoryViewer(bot)
        elif sender != st.BOT_USERNAME and message == 'close pocket':
            bot.webInventory.stop()
        
        
            
# для проверки в случае ошибок
# @On(bot, "end")
# def handle_end(*args):
#     print("Bot ended!", args)

# @On(bot, "error")
# def handle_error(*args):
#     print("Bot errored!", args)
