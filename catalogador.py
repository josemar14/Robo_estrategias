from iqoptionapi.constants import ACTIVES  # Importa a classe ACTIVES da biblioteca iqoptionapi
from configobj import ConfigObj  # Importa a classe ConfigObj da biblioteca configobj
from datetime import datetime, timedelta  # Importa a classe datetime do módulo datetime
import time, sys  # Importa os módulos 'time', 'sys' para funcionalidades do sistema

def catag(API):
    config = ConfigObj('config.txt') 

    pares_abertos = []

    all_asset = API.get_all_open_time()

    for par in all_asset['digital']:
        if par in ACTIVES:
            if all_asset['digital'][par]['open']:
                pares_abertos.append(par)

    for par in all_asset['turbo']:
        if par in ACTIVES:
            if all_asset['turbo'][par]['open']:
                if par not in pares_abertos:
                    pares_abertos.append(par)
            

    timeframe = 300
    qnt_velas_m5  = 146

    global resultado
    resultado = []
    
    def gabam5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 15 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-3]['open'] < velas[i-3]['close'] else 'Vermelha' if velas[i-3]['open'] > velas[i-3]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela3 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'
                        
                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2,vela3

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Vermelha'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Verde'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['GABA'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
    def tripli():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 10 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'

                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['TRIPLICAÇÃO M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])

    def naotripli():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 10 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'

                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Vermelha'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Verde'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['NÃO TRIPLICAÇÃO M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
    def d21():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 30 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-6]['open'] < velas[i-6]['close'] else 'Vermelha' if velas[i-6]['open'] > velas[i-6]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-4]['open'] < velas[i-4]['close'] else 'Vermelha' if velas[i-4]['open'] > velas[i-4]['close'] else 'Doji'
                            vela3 = 'Verde' if velas[i-3]['open'] < velas[i-3]['close'] else 'Vermelha' if velas[i-3]['open'] > velas[i-3]['close'] else 'Doji'
                        
                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2,vela3

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Vermelha'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Verde'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['D21 M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])

    def garra():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 10 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            
                            vela1 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'

                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['GARRA M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
    def vizinhosm5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 20 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'


                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['TRÊS VIZINHOS M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])

    def mosqueteirosm5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 10 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'


                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['TRÊS MOSQUETEIROS M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
    def torresm5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 25 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-5]['open'] < velas[i-5]['close'] else 'Vermelha' if velas[i-5]['open'] > velas[i-5]['close'] else 'Doji'


                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['TORRES GÊMEAS M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
    def milhaom5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 30 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:
                            vela1 = 'Verde' if velas[i-6]['open'] < velas[i-6]['close'] else 'Vermelha' if velas[i-6]['open'] > velas[i-6]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-5]['open'] < velas[i-5]['close'] else 'Vermelha' if velas[i-5]['open'] > velas[i-5]['close'] else 'Doji'
                            vela3 = 'Verde' if velas[i-4]['open'] < velas[i-4]['close'] else 'Vermelha' if velas[i-4]['open'] > velas[i-4]['close'] else 'Doji'
                            vela4 = 'Verde' if velas[i-3]['open'] < velas[i-3]['close'] else 'Vermelha' if velas[i-3]['open'] > velas[i-3]['close'] else 'Doji'
                            vela5 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela6 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'

                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2,vela3,vela4,vela5,vela6

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Vermelha'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Verde'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['MILHÃO MINORIA M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
    def milhaoM5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 30 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:
                            vela1 = 'Verde' if velas[i-6]['open'] < velas[i-6]['close'] else 'Vermelha' if velas[i-6]['open'] > velas[i-6]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-5]['open'] < velas[i-5]['close'] else 'Vermelha' if velas[i-5]['open'] > velas[i-5]['close'] else 'Doji'
                            vela3 = 'Verde' if velas[i-4]['open'] < velas[i-4]['close'] else 'Vermelha' if velas[i-4]['open'] > velas[i-4]['close'] else 'Doji'
                            vela4 = 'Verde' if velas[i-3]['open'] < velas[i-3]['close'] else 'Vermelha' if velas[i-3]['open'] > velas[i-3]['close'] else 'Doji'
                            vela5 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela6 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'

                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2,vela3,vela4,vela5,vela6

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['MILHÃO MAIORIA M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])

    def mhiM5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 30 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-3]['open'] < velas[i-3]['close'] else 'Vermelha' if velas[i-3]['open'] > velas[i-3]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela3 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'

                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2,vela3

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Verde'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Vermelha'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['MHI1 MAIORIA M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])        
    
    def mhim5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 30 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-3]['open'] < velas[i-3]['close'] else 'Vermelha' if velas[i-3]['open'] > velas[i-3]['close'] else 'Doji'
                            vela2 = 'Verde' if velas[i-2]['open'] < velas[i-2]['close'] else 'Vermelha' if velas[i-2]['open'] > velas[i-2]['close'] else 'Doji'
                            vela3 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'

                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1,vela2,vela3

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Vermelha'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Verde'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['MHI1 MINORIA M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
    def fivem5():
        global resultado
        for par in pares_abertos:
            velas = API.get_candles(par, timeframe,qnt_velas_m5, time.time())
            doji = 0
            win = 0
            loss = 0
            gale1 = 0
            gale2 = 0
            gale3 = 0
            gale4 = 0
            gale5 = 0

            for i in range(len(velas)):
                minutos = float(datetime.fromtimestamp(velas[i]['from']).strftime('%M'))

                if minutos == 25 or minutos== 00:
                    try:
                        if i <2:
                            pass
                        else:

                            vela1 = 'Verde' if velas[i-1]['open'] < velas[i-1]['close'] else 'Vermelha' if velas[i-1]['open'] > velas[i-1]['close'] else 'Doji'


                            entrada1 = 'Verde' if velas[i]['open'] < velas[i]['close'] else 'Vermelha' if velas[i]['open'] > velas[i]['close'] else 'Doji'
                            entrada2 = 'Verde' if velas[i+1]['open'] < velas[i+1]['close'] else 'Vermelha' if velas[i+1]['open'] > velas[i+1]['close'] else 'Doji'
                            entrada3 ='Verde' if velas[i+2]['open'] < velas[i+2]['close'] else 'Vermelha' if velas[i+2]['open'] > velas[i+2]['close'] else 'Doji'
                            entrada4 ='Verde' if velas[i+3]['open'] < velas[i+3]['close'] else 'Vermelha' if velas[i+3]['open'] > velas[i+3]['close'] else 'Doji'
                            entrada5 ='Verde' if velas[i+4]['open'] < velas[i+4]['close'] else 'Vermelha' if velas[i+4]['open'] > velas[i+4]['close'] else 'Doji'
                            entrada6 ='Verde' if velas[i+5]['open'] < velas[i+5]['close'] else 'Vermelha' if velas[i+5]['open'] > velas[i+5]['close'] else 'Doji'

                            cores = vela1

                            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0 : dir = 'Vermelha'
                        
                            if cores.count('Vermelha') > cores.count('Verde') and cores.count('Doji') == 0 : dir = 'Verde'

                            if cores.count('Doji') >0:
                                doji += 1
                            else:
                                if entrada1 == dir:
                                    win +=1
                                else:
                                    if entrada2 == dir:
                                        gale1 +=1
                                    else:
                                        if entrada3 == dir:
                                            gale2 +=1
                                        else: 
                                            if entrada4 == dir:
                                                gale3 +=1
                                            else:
                                                if entrada5 == dir:
                                                    gale4 +=1
                                                else: 
                                                    if entrada6 == dir:
                                                        gale5 +=1
                                                    
                                                    else:
                                                        loss +=1
                    except:
                        pass
            
            

            total_entrada = win + gale1 + gale2 + gale3 + gale4 + gale5 + loss    
            qnt_win = win
            qnt_gale1 = win + gale1
            qnt_gale2 = win + gale1 + gale2
            qnt_gale3 = win + gale1 + gale2 + gale3
            qnt_gale4 = win + gale1 + gale2 + gale3 + gale4
            qnt_gale5 = win + gale1 + gale2 + gale3 + gale4 + gale5

            win = round(qnt_win/(total_entrada)*100,2)
            gale1 = round(qnt_gale1/(total_entrada)*100,2)
            gale2 = round(qnt_gale2/(total_entrada)*100,2)
            gale3 = round(qnt_gale3/(total_entrada)*100,2)
            gale4 = round(qnt_gale4/(total_entrada)*100,2)
            gale5 = round(qnt_gale5/(total_entrada)*100,2)
            assertividade = round(win/(total_entrada)*100,2)
            resultado.append(['FIVE FLIP M5'] + [par]+ [win]+ [gale1]+ [gale2]+ [gale3]+ [gale4]+ [gale5]+ [doji]+ [loss]+ [assertividade])
    
   
    ### Chamada de Estratégias

    gabam5()
    tripli()
    naotripli()
    d21()
    garra()
    vizinhosm5()
    mosqueteirosm5()
    torresm5()
    milhaom5()
    milhaoM5()
    mhiM5()
    mhim5()
    fivem5()

    ### Configuração de Entrada do Martingale:

    if config['MARTINGALE']['usar_martingale'] == 'S':
        if int(config['MARTINGALE']['niveis_martingale']) == 0:
            linha = 2
        if int(config['MARTINGALE']['niveis_martingale']) == 1:
            linha = 3
        if int(config['MARTINGALE']['niveis_martingale']) >= 2:
            linha = 4
        if int(config['MARTINGALE']['niveis_martingale']) == 3:
            linha = 5
        if int(config['MARTINGALE']['niveis_martingale']) == 4:
            linha = 6
        if int(config['MARTINGALE']['niveis_martingale']) >= 5:
            linha = 7
    else:
        linha = 2

    lista_catalog = sorted(resultado, key = lambda x: x[linha], reverse = True)

    return lista_catalog, linha   