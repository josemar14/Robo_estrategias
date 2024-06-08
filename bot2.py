from iqoptionapi.stable_api import IQ_Option  # Importa a classe IQ_Option da biblioteca iqoptionapi
from iqoptionapi.constants import ACTIVES  # Importa a classe ACTIVES da biblioteca iqoptionapi
from configobj import ConfigObj  # Importa a classe ConfigObj da biblioteca configobj
from datetime import datetime, timedelta  # Importa a classe datetime do módulo datetime
from catalogador import catag  # Importa a função catag do módulo catalogador
from tabulate import tabulate  # Importa a classe tabulate da biblioteca tabulate
import json, os ,sys  # Importa os módulos 'sys', 'os', 'sys' para funcionalidades do sistema
import time  # Importa o módulo time para manipulação de tempo

### CRIANDO ARQUIVO DE CONFIGURAÇÃO ####
config = ConfigObj('config.txt')  # NOME ARQUIVO: [TXT] DE CONFIGURAÇÃO
email = config['LOGIN']['email']  # Obtém o email de login
senha = config['LOGIN']['senha']  # Obtém a senha de login
tipo = config['AJUSTES']['tipo']  # Obtém o tipo de moeda
valor_entrada = float(config['AJUSTES']['valor_entrada'])  # Obtém o valor da entrada como um número decimal
stop_win = float(config['AJUSTES']['stop_win'])  # Obtém o stop win como um número decimal
stop_loss = float(config['AJUSTES']['stop_loss'])  # Obtém o stop loss como um número decimal
payout_min = int(config["AJUSTES"]["payout_min"]) # Obtém o pagamento mínimo como um inteiro

# Configurações de martingale
if config['MARTINGALE']['usar_martingale'].upper() == 'S':  # Verifica se o martingale está ativado
    martingale = int(config['MARTINGALE']['niveis_martingale'])  # Obtém o número de níveis de martingale como um inteiro
else:
    martingale = 0  # Define o martingale como zero se não estiver ativado
fator_mg = float(config['MARTINGALE']['fator_martingale'])  # Obtém o fator de martingale como um número decimal

# Configurações de soros
if config['SOROS']['usar_soros'].upper() == 'S':  # Verifica se o soros está ativado
    soros = True  # Define soros como True se estiver ativado
    niveis_soros = int(config['SOROS']['niveis_soros'])  # Obtém o número de níveis de soros como um inteiro
    nivel_soros = 0  # Inicializa o nível de soros como zero
else:
    soros = False  # Define soros como False se não estiver ativado
    niveis_soros = 0  # Define o número de níveis de soros como zero
    nivel_soros = 0  # Inicializa o nível de soros como zero
porcentagem_soros = float(config["SOROS"]["porcentagem_soros"])  # Obtém a porcentagem de soros como um número decimal
valor_soros = 0  # Inicializa o valor de soros como zero
lucro_op_atual = 0  # Inicializa o lucro da operação atual como zero

# Configurações de indicadores
analise_medias = config['INDICADORES']['analise_medias']  # Obtém a análise de médias
velas_medias = int(config['INDICADORES']['velas_medias'])  # Obtém o número de velas para a média como um inteiro

#### Inicialização de variáveis  ####
lucro_total = 0  # Inicializa o lucro total como zero
stop = True  # Inicializa a variável stop como True
total_trades = 0  # Inicializa o total trades como zero
total_trades_win = 0  # Inicializa o total trades WIN(Vitorias) como zero
total_trades_loss = 0  # Inicializa o total trades LOSS(Derrotas) como zero

#########---> Avisos iniciais  <---#########
print('\n#####################################################################')
print(' Iniciando Conexão com a IQOption')

# Funcao para reconectar a API
def reconnect(API):
    max_attempts = 3  # Numero maximo de tentativas de reconexao
    attempts = 0
    while attempts < max_attempts:
        try:
            API.connect()  # Tentativa de reconexão
            print(" Reconexão estabelecida novamente com a corretora.")
            return True
        except ConnectionError as ce:
            print(f" Falha de tentativa de reconexão: {ce}")
            attempts += 1
            time.sleep(5)  # Aguarda um pouco antes de tentar novamente
        except Exception as e:
            print(f" Falha ao tentar se reconectar: {e}")
            attempts += 1
            time.sleep(5)  # Aguarda um pouco antes de tentar novamente
    print(" Falha ao tentar se reconectar após várias tentativas. ENCERRANDO!")
    sys.exit()  # Sai do programa se a reconexão falhar

# Função para fazer a conexão com a conta IQ_Option
def connect_account(email, senha):
    global tipo_conta, API  # Permite acesso às variáveis tipo_conta e API fora da função
    
    API = IQ_Option(email,senha)  # Instancia um objeto IQ_Option com o email e senha fornecidos
    conectado = False  # Inicializa a variável conectado como False
    check, reason = API.connect()  # Tenta conectar à IQ_Option
    if check:  # Se a conexão for bem-sucedida
        print('\n Conectado com sucesso!')
    else:  # Se a conexão falhar
        if reason == '{"code":"invalid_credentials","message":"You entered the wrong credentials. Please ensure that your login/password is correct."}':
            print('\n Email ou Senha salvos da corretora podem estar incorretos. Verifique! \n')
            sys.exit()  # Sai do programa se as credenciais estiverem incorretas
        else:
            print('\n Houve um problema na conexão com a IQ_Option!')
            print(reason)  # Se for outro erro, de conexao alem de email e senha... Mostra aqui!
            reconnect(API)  # Tenta reconectar em caso de falha inicial de conexão

    # Função para selecionar entre conta demo ou real
    while True:
        escolha = input("\n Qual o tipo de conta deseja conectar?" +
                        "\n 1- DEMO" +
                        "\n 2- REAL" +
                        "\n --> ")
        if escolha == '1':
            tipo_conta = 'PRACTICE'
            conectado = True
            print('\n Conta DEMO selecionada!')
            break
        if escolha == '2':
            tipo_conta = 'REAL'
            conectado = True
            print('\n Conta REAL selecionada!' +
                  '\n TENHA RESPONSABILIDADE.')
            break
        else:
            print(' Escolha incorreta: Selecione uma das opções abaixo.')
    API.change_balance(tipo_conta)  # Altera o saldo da conta (demo ou real)
    return API, conectado  # Retorna o objeto API e o status de conexão

API, conectado = connect_account(email,senha)  # Chama a função connect_account e obtém o objeto API e o status de conexão

# Função obtendo informações do perfil
def Info_AccountIQ(client):
    perfil = json.loads(json.dumps(client.get_profile_ansyc()))  # Obtém informações do perfil do usuário
    nome = str(perfil["name"])  # Obtém o nome do usuário
    cifrao = str(perfil["currency_char"])  # Obtém o símbolo da moeda
    valorconta = float(client.get_balance())  # Obtém o saldo da conta

    return perfil, nome, cifrao, valorconta

perfil, nome, cifrao, valorconta = Info_AccountIQ(API) # Chama a função InformAccountIQ e obtém os dados do perfil da API

### Função para checar stop win e loss
def check_stop():
    global stop,lucro_total  # Permite acesso às variáveis stop e lucro_total fora da função
    if lucro_total <= float('-'+str(abs(stop_loss))):  # Verifica se o lucro total atingiu o stop loss
        stop = False  # Define stop como False
        print('\n #########################')
        print(' STOP LOSS BATIDO ',str(cifrao),str(lucro_total))
        print(' #########################')
        sys.exit()  # Sai do programa
        
    if lucro_total >= float(abs(stop_win)):  # Verifica se o lucro total atingiu o stop win
        stop = False  # Define stop como False
        print('\n #########################')
        print(' STOP WIN BATIDO ',str(cifrao),str(lucro_total))
        print(' #########################')
        sys.exit()  # Sai do programa

# Função para coletar o pagamento(Payout)
def payout(par):
    pares_abertos = []
    pares_fechados_excluir = []
    profit = API.get_all_profit()  # Obtém os (Payout)[lucros/retorno] de todas todos PARES abertos no momento
    try:
        all_asset = API.get_all_open_time()  # Obtém lista com todos PARES abertos no momento
    except Exception as e:
        print(f" => Erro ao obter ativos e tabelas de candles: {e}")
        reconnect(API)
    # Puxar o pagamento de pares abertos binários
    try:
        if all_asset['binary'][par]['open']:
            if par in ACTIVES:
                if profit[par]['binary']> 0:
                    binary = round(profit[par]['binary'],2) * 100  # Calcula o pagamento binário
                    if binary >= payout_min:
                        if par not in pares_abertos:
                            pares_abertos.append(par)
                    else:
                        pares_fechados_excluir.append(par)
        else:
            binary  = 0
    except:
        binary = 0
    # Puxar o pagamento de pares abertos turbo
    try:
        if all_asset['turbo'][par]['open']:
            if par in ACTIVES:
                if profit[par]['turbo']> 0:
                    turbo = round(profit[par]['turbo'],2) * 100  # Calcula o pagamento turbo
                    if turbo >= payout_min:
                        if par not in pares_abertos:
                            pares_abertos.append(par)
                    else:
                        pares_fechados_excluir.append(par)
        else:
            turbo  = 0
    except:
        turbo = 0
    # Puxar o pagamento de pares abertos digital
    try:
        if all_asset['digital'][par]['open']:
            if par in ACTIVES:
                digital = API.get_digital_payout(par)
                if digital >= payout_min:
                    if par not in pares_abertos:
                        pares_abertos.append(par)
                else:
                        pares_fechados_excluir.append(par)
        else:
            digital  = 0
    except:
        digital = 0

    return binary, turbo, digital  # Retorna os pagamentos binário, turbo e digital

### Função abrir ordem e checar resultado ###
def compra(ativo,valor_entrada,direcao,exp,tipo):
    global stop,lucro_total, nivel_soros, niveis_soros, valor_soros, lucro_op_atual, total_trades_win, total_trades_loss, total_trades

    if soros:
        if nivel_soros == 0:  # Se o nível de soros for 0
            entrada = valor_entrada  # Define a entrada como o valor de entrada
        if nivel_soros >=1 and valor_soros > 0 and nivel_soros <= niveis_soros:  # Se o nível de soros for maior ou igual a 1, o valor de soros for maior que 0 e o nível de soros for menor ou igual ao número de níveis de soros
            entrada = valor_entrada + ((valor_soros * porcentagem_soros) / 100)  # Define a entrada como o valor de entrada mais a porcentagem de soros
        if nivel_soros > niveis_soros:  # Se o nível de soros for maior que o número de níveis de soros
            lucro_op_atual = 0  # Define o lucro da operação atual como 0
            valor_soros = 0  # Define o valor de soros como 0
            entrada = valor_entrada  # Define a entrada como o valor de entrada
            nivel_soros = 0  # Define o nível de soros como 0
    else:
        entrada = valor_entrada  # Define a entrada como o valor de entrada

    for i in range(martingale + 1):  # Loop para o martingale
        if stop == True:  # Verifica stop
            if tipo == 'digital':  # Se o tipo for digital
                check, id = API.buy_digital_spot_v2(ativo,entrada,direcao,exp)  # Compra digital
            else:
                check, id = API.buy(entrada,ativo,direcao,exp)  # Compra binária[m10,m15] ou turbo[m1,m2,m3,m4,m5]

            if check:  # Se a compra for bem-sucedida
                if i == 0:  # Se for a primeira compra
                    print('\n>> Ordem aberta \n>> Par:',ativo,'\n>> Timeframe:',exp,'\n>> Entrada de:',cifrao,entrada)
                if i >= 1:  # Se for a segunda compra sera um gale
                    print('\n>> Ordem aberta para gale',str(i),'\n>> Par:',ativo,'\n>> Timeframe:',exp,'\n>> Entrada de:',cifrao,entrada)

                while True:
                    time.sleep(0.1)
                    status , resultado = API.check_win_digital_v2(id) if tipo == 'digital' else API.check_win_v4(id)

                    if status:  # Se o status(SITUAÇAO) for verdadeiro (win-GANHOU)
                        lucro_total += round(resultado,2)  # Adiciona o lucro total
                        valor_soros += round(resultado, 2)  # Adiciona o valor de soros
                        lucro_op_atual += round(resultado, 2)  # Adiciona o lucro da operação atual

                        if resultado > 0:  # Se o resultado(LUCRO) for positivo(win)
                            if i == 0:  # Se for a primeira compra
                                total_trades +=1
                                total_trades_win += 1
                                print('\n>> Resultado: WIN \n>> Lucro:', round(resultado,2), '\n>> Par:', ativo, '\n>> Lucro total: ', round(lucro_total,2))
                                print("\n=========================","\n>> Total WINS:", total_trades_win, "\n>> Total LOSS:", total_trades_loss,"\n=========================")
                            if i >= 1:  # Se for a segunda compra sera um gale
                                total_trades_win += 1
                                total_trades +=1
                                print('\n>> Resultado: WIN no gale',str(i),'\n>> Lucro:', round(resultado,2), '\n>> Par:', ativo, '\n>> Lucro total: ', round(lucro_total,2))
                                print("\n=========================","\n>> Total WINS:", total_trades_win, "\n>> Total LOSS:", total_trades_loss,"\n=========================")

                        elif resultado == 0:  # Se o resultado(LUCRO) for igual a 0(empate)
                            if i == 0:  # Se for a primeira compra
                                if (martingale == 0): 
                                    total_trades +=1 
                                else: 
                                    pass
                                print('\n>> Resultado: EMPATE \n>> Lucro:', round(resultado,2), '\n>> Par:', ativo, '\n>> Lucro total: ', round(lucro_total,2))
                                print("\n=========================","\n>> Total WINS:", total_trades_win, "\n>> Total LOSS:", total_trades_loss,"\n=========================")
                            if i >= 1:  # Se for a segunda compra sera um gale
                                if (martingale == 1):
                                    total_trades +=1 
                                if (martingale == 2):
                                    total_trades +=1 
                                else: 
                                    pass
                                print('\n>> Resultado: EMPATE no gale',str(i),'\n>> Lucro:', round(resultado,2), '\n>> Par:', ativo, '\n>> Lucro total: ', round(lucro_total,2))
                                print("\n=========================","\n>> Total WINS:", total_trades_win, "\n>> Total LOSS:", total_trades_loss,"\n=========================")
                            
                            if i+1 <= martingale:  # Se for possível realizar mais um gale
                                gale = float(entrada)                   
                                entrada = round(abs(gale), 2)  # Calcula a entrada do próximo gale    

                        else:  # Se o resultado(LUCRO) for negativo(loss)
                            if i == 0:  # Se for a primeira compra
                                if (martingale == 0): 
                                    total_trades_loss += 1
                                    total_trades +=1 
                                else: 
                                    pass
                                print('\n>> Resultado: LOSS \n>> Lucro:', round(resultado,2), '\n>> Par:', ativo, '\n>> Lucro total: ', round(lucro_total,2))
                                if (martingale == 0): 
                                    print("\n=========================","\n>> Total WINS:", total_trades_win, "\n>> Total LOSS:", total_trades_loss,"\n=========================")
                            if i >= 1:  # Se for a segunda compra sera um gale
                                if (martingale == 1):
                                    total_trades_loss += 1
                                    total_trades +=1 
                                if (martingale == 2):
                                    total_trades_loss += 1
                                    total_trades +=1 
                                else: 
                                    pass
                                print('\n>> Resultado: LOSS no gale',str(i), '\n>> Lucro:', round(resultado,2), '\n>> Par:', ativo, '\n>> Lucro total: ', round(lucro_total,2))
                                print("\n=========================","\n>> Total WINS:", total_trades_win, "\n>> Total LOSS:", total_trades_loss,"\n=========================")
                                
                            if i+1 <= martingale:  # Se for possível realizar mais um gale
                                gale = float(entrada) * float(fator_mg)                           
                                entrada = round(abs(gale), 2)  # Calcula a entrada do próximo gale

                        check_stop()  # Verifica os stops
                        break  # Sai do loop  
                if resultado > 0:  # Se o resultado(LUCRO) for positivo(win)
                    break  # Sai do loop(STOP) -- #  status(SITUAÇAO) for falso #
            else:  # Se a compra não for enviada
                print('erro na abertura da ordem,', id,ativo)
    if soros:
        if lucro_op_atual > 0:
            nivel_soros += 1
            lucro_op_atual = 0
        else:
            valor_soros = 0
            nivel_soros = 0
            lucro_op_atual = 0

### Fução que busca hora da corretora ###
def horario():
    x = API.get_server_timestamp()
    now = datetime.fromtimestamp(API.get_server_timestamp())
    return now

# Função para calcular as médias móveis
def medias(velas):
    """
    Calcula a média móvel e determina a tendência do mercado.
    Args:
        velas (list): Uma lista de velas contendo dados de fechamento.
    Returns:
        str: A tendência do mercado ('put' para queda, 'call' para alta).
    """
    soma = 0  # Inicializa a soma
    for i in velas:  # Loop sobre as velas
        soma += i['close']  # Adiciona o valor de fechamento da vela à soma
    media = soma / velas_medias  # Calcula a média

    if media > velas[-1]['close']:  # Se a média for maior que o último valor de fechamento
        tendencia = 'put'  # Tendência é de queda
    else:  # Se não
        tendencia = 'call'  # Tendência é de alta
    return tendencia  # Retorna a tendência

################################################################################
# Função para catalogar estrategias
def catalogar():
    global lista_catalog, estrateg, ativo,  assertividade

    print('>> Iniciando nova catalogação')
    lista_catalog , linha = catag(API)
    
    estrateg = lista_catalog[0][0]
    ativo = lista_catalog[0][1]
    assertividade = lista_catalog[0][linha]
    
    #print(tabulate(lista_catalog, headers=['ESTRATEGIAS','PAR','WIN','GALE1','GALE2'], tablefmt="mixed_grid"))
    print('\n>> Melhor par:', ativo, ' | Estrategia:', estrateg, ' | Assertividade:', assertividade)
    while True:
         ### chamada da estrategia ###
        if estrateg == 'Gaba M5':
            estrategia_gaba()
            break
        if estrateg == 'Triplicação M5':
            estrategia_triplicacao()
            break
        if estrateg == 'Não Triplicação M5':
            estrategia_naotriplicacao()
            break
        if estrateg == 'D21 M5':
            estrategia_d21()
            break
        if estrateg == 'Garra M5':
            estrategia_garram5()
            break
        if estrateg == 'Três Vizinhos M5':
            estrategia_tresvizinhosm5()
            break
        if estrateg == 'Três Mosqueteiros M5':
            estrategia_tresmosqueteirosm5()
            break
        if estrateg == 'Torres Gêmeas M5':
            estrategia_torresgemeasm5()
            break
        if estrateg == 'Milhão Minoria M5':
            estrategia_milhaominoriam5()
            break
        if estrateg == 'Milhão Maioria M5':
            estrategia_milhaomaioriam5()
            break
        if estrateg == 'MHI1 Maioria M5':
            estrategia_mhi1maioriam5() 
            break
        if estrateg == 'MHI1 Minoria M5':
            estrategia_mhi1minoriam5()
            break
        if estrateg == 'Five Flip M5':
            estrategia_fiveflipm5()
            break
        
        else:
            print(' NAO ENCONTRADO ESTRATEGIA! ')
            sys.exit()
################################################################################

#####################----- FUNCAO DAS ESTRATEGIAS -----#########################
### Função de análise MHI menor [1m] 
def estrategia_gaba():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 13.58 and minutos <= 14.00) or minutos >= 28.58 else False 
        else:
            print_catag = False
            auto_catag = False



        entrar = True if (minutos >= 14.58 and minutos <= 15.00) or minutos >= 29.58 else False 
        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]GABA[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 3


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'
            velas[-3] = 'Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji'

            cores = velas[-3],velas[-2],velas[-1]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('[cyan]Velas[/]: ',velas[-3], velas[-2], velas[-1], ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Velas[/]: ',velas[-3], velas[-2], velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Velas[/]: ',velas[-3], velas[-2], velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

### A entrada se dá no mesmo quadrante de 3 velas, a terceira vela deverá ter a mesma cor das duas velas anteriores.

def estrategia_triplicacao():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 8.58 and minutos <= 9.00) or (minutos >= 23.58 and minutos <= 24.00) else False
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 9.58 and minutos <= 10.00) or (minutos >= 24.58 and minutos <= 25.00) else False 
        
        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]TRIPLICAÇÃO[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 2


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'

            cores = velas[-2],velas[-1]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('[cyan]Velas[/]: ',velas[-2], velas[-1] , ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Velas[/]: ',velas[-2], velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Velas[/]: ',velas[-2], velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Velas com[/] [green]cores[/] [red]diferentes[/].')

                time.sleep(2)

### A entrada se dá no mesmo quadrante de 3 velas, a terceira vela deverá ter a cor oposta de uma ou das duas velas anteriores.

def estrategia_naotriplicacao():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 8.58 and minutos <= 9.00) or (minutos >= 23.58 and minutos <= 24.00) else False 
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 9.58 and minutos <= 10.00) or (minutos >= 24.58 and minutos <= 25.00) else False 
        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]NÃO TRIPLICAÇÃO[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 2


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'

            cores = velas[-2],velas[-1]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('[cyan]Velas[/]: ',velas[-2], velas[-1] , ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Velas[/]: ',velas[-2], velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Velas[/]: ',velas[-2], velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Velas com[/] [green]cores[/] [red]diferentes[/].')

                time.sleep(2)

# No quadrante de 6 velas, observa-se as velas 1, 3, e 4. A primeira vela do quadrante seguinte deverá ser da cor da minoria.

def estrategia_d21():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 28.58 and minutos <= 29.00) or minutos >= 28.58 else False 
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 29.58 and minutos <= 30.00) or minutos >= 29.58 else False 
        
        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]D21[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 6


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-3] = 'Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji'
            velas[-4] = 'Verde' if velas[-4]['open'] < velas[-4]['close'] else 'Vermelha' if velas[-4]['open'] > velas[-4]['close'] else 'Doji'
            velas[-6] = 'Verde' if velas[-6]['open'] < velas[-6]['close'] else 'Vermelha' if velas[-6]['open'] > velas[-6]['close'] else 'Doji'

            cores = velas[-6],velas[-4],velas[-3]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('[cyan]Velas[/]: ',velas[-6], velas[-4], velas[-3], ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Velas[/]: ',velas[-6], velas[-4], velas[-3])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Velas[/]: ',velas[-6], velas[-4], velas[-3])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

def estrategia_garram5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 8.58 and minutos <= 9.00) or (minutos >= 23.58 and minutos <= 24.00) else False 
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 9.58 and minutos <= 10.00) or (minutos >= 24.58 and minutos <= 25.00) else False 
        
        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]GARRA M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 2


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'

            cores = velas[-2],velas[-1]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('Velas: ',velas[-2],velas[-1] , ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Velas[/]: ',velas[-2],velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Velas[/]: ',velas[-2],velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um[/] [magenta]doji[/] [yellow]na análise[/].')

                time.sleep(2)

### A operação é aberta no mesmo quadrante e a cor da 4ª vela é levada em consideração para abrir a operação na 5ª vela com a mesma cor.

def estrategia_tresvizinhosm5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 18.58 and minutos <= 19.00) or minutos >= 28.58 else False
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 19.58 and minutos <= 20.00) or minutos >= 29.58 else False

        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]TRÊS VIZINHOS M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 7


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'


            cores = velas[-1]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('[cyan]Vela[/]: ',velas[-1], ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Vela[/]: ',velas[-1])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Vela[/]: ',velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

def estrategia_tresmosqueteirosm5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 8.58 and minutos <= 9.00) or minutos >= 18.58 else False
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 9.58 and minutos <= 10.00) or minutos >= 19.58 else False

        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]TRÊS MOSQUETEIROS M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 2


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-2] = 'Verde' if velas[-1]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'

            cores = velas[-2]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('[cyan]Vela[/]: ',velas[-2], ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Vela[/]: ',velas[-2])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Vela[/]: ',velas[-2] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

def estrategia_torresgemeasm5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 23.58 and minutos <= 24.00) or minutos >= 28.58 else False
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 24.58 and minutos <= 25.00) or minutos >= 29.58 else False

        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [cyan]TORRES GÊMEAS M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 5


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-5] = 'Verde' if velas[-5]['open'] < velas[-5]['close'] else 'Vermelha' if velas[-5]['open'] > velas[-5]['close'] else 'Doji'


            cores = velas[-4]

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('[cyan]Vela[/]: ',velas[-5], ' - [green]Entrada[/] [yellow]para[/] ', direcao)


                compra(ativo,valor_entrada,direcao,5,tipo)

                   
                print('\n')

            else:
                if direcao == 'abortar':
                    print('[cyan]Vela[/]: ',velas[-5])
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('[cyan]Vela[/]: ',velas[-5] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

def estrategia_milhaominoriam5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 28.58 and minutos <= 29.00) or minutos >= 28.58 else False
        else:
            print_catag = False
            auto_catag = False 
        entrar = True if (minutos >= 29.58 and minutos <= 30.00) or minutos >= 29.58 else False


        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass
                    
        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [red]MILHÃO[/] [green]MINORIA M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 6


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())


            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'
            velas[-3] = 'Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji'
            velas[-4] = 'Verde' if velas[-4]['open'] < velas[-4]['close'] else 'Vermelha' if velas[-4]['open'] > velas[-4]['close'] else 'Doji'
            velas[-5] = 'Verde' if velas[-5]['open'] < velas[-5]['close'] else 'Vermelha' if velas[-5]['open'] > velas[-5]['close'] else 'Doji'
            velas[-6] = 'Verde' if velas[-6]['open'] < velas[-6]['close'] else 'Vermelha' if velas[-6]['open'] > velas[-6]['close'] else 'Doji'

            cores = velas[-6], velas[-5], velas[-4], velas[-3] ,velas[-2] ,velas[-1] 

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('>> [cyan]Velas[/]: ',velas[-6] ,velas[-5] ,velas[-4] ,velas[-3] ,velas[-2] ,velas[-1] , ' - [green]Entrada[/] [yellow]para[/]: ', direcao)

                compra(ativo,valor_entrada,direcao,5,tipo)
                print('\n')

            else:
                if direcao == 'abortar':
                    print('>> [cyan]Velas[/]: ',velas[-6] ,velas[-5] ,velas[-4] ,velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('>> [cyan]Velas[/]: ',velas[-6] ,velas[-5] ,velas[-4] ,velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

def estrategia_milhaomaioriam5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 28.58 and minutos <= 29.00) or minutos >= 28.58 else False
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 29.58 and minutos <= 30.00) or minutos >= 29.58 else False


        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass
                    
        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [red]MILHÃO[/] [green]MAIORIA M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 6


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())


            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'
            velas[-3] = 'Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji'
            velas[-4] = 'Verde' if velas[-4]['open'] < velas[-4]['close'] else 'Vermelha' if velas[-4]['open'] > velas[-4]['close'] else 'Doji'
            velas[-5] = 'Verde' if velas[-5]['open'] < velas[-5]['close'] else 'Vermelha' if velas[-5]['open'] > velas[-5]['close'] else 'Doji'
            velas[-6] = 'Verde' if velas[-6]['open'] < velas[-6]['close'] else 'Vermelha' if velas[-6]['open'] > velas[-6]['close'] else 'Doji'

            cores = velas[-6], velas[-5], velas[-4], velas[-3] ,velas[-2] ,velas[-1] 

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('>> [cyan]Velas[/]: ',velas[-6] ,velas[-5] ,velas[-4] ,velas[-3] ,velas[-2] ,velas[-1] , ' - [green]Entrada[/] [yellow]para[/]: ', direcao)

                compra(ativo,valor_entrada,direcao,5,tipo)
                print('\n')

            else:
                if direcao == 'abortar':
                    print('>> [cyan]Velas[/]: ',velas[-6] ,velas[-5] ,velas[-4] ,velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('>> [cyan]Velas[/]: ',velas[-6] ,velas[-5] ,velas[-4] ,velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

def estrategia_mhi1maioriam5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 28.58 and minutos <= 29.00) or minutos >= 28.58 else False
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 29.58 and minutos <= 30.00) or minutos >= 29.58 else False

        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass
                    
        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [red]M[/][green]H[/][red]I[/][green]1[/] [red]MAIORIA M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 3


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())


            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'
            velas[-3] = 'Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji'


            cores = velas[-3] ,velas[-2] ,velas[-1] 

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('>> [cyan]Velas[/]: ',velas[-3] ,velas[-2] ,velas[-1] , ' - [green]Entrada[/] [yellow]para[/]: ', direcao)

                compra(ativo,valor_entrada,direcao,5,tipo)
                print('\n')

            else:
                if direcao == 'abortar':
                    print('>> [cyan]Velas[/]: ',velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('>> [cyan]Velas[/]: ',velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)                

def estrategia_mhi1minoriam5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        print(binary, turbo, digital )
        if digital > turbo:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas digitais[/]')
            tipo = 'digital'
        elif turbo > digital:
            print( '>> [cyan]Suas entradas[/] [yellow]serão realizadas[/] [green]nas binárias[/]')
            tipo = 'binary'
        else:
            print('>> [red]Par fechado[/], [green]escolha outro[/]')
            sys.exit()


    
    while True:
        time.sleep(0.1)

        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])

        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 28.58 and minutos <= 29.00) or minutos >= 28.58 else False
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 29.58 and minutos <= 30.00) or minutos >= 29.58 else False

        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')

        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass
                    
        if entrar:
            print('\n>> [green]Iniciando[/] [magenta]análise[/] [yellow]da estratégia[/] [red]M[/][green]H[/][red]I[/][green]1[/] [red]MINORIA M5[/]')

            direcao = False

            timeframe = 300
            qnt_velas = 3


            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)

            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())


            velas[-1] = 'Verde' if velas[-1]['open'] < velas[-1]['close'] else 'Vermelha' if velas[-1]['open'] > velas[-1]['close'] else 'Doji'
            velas[-2] = 'Verde' if velas[-2]['open'] < velas[-2]['close'] else 'Vermelha' if velas[-2]['open'] > velas[-2]['close'] else 'Doji'
            velas[-3] = 'Verde' if velas[-3]['open'] < velas[-3]['close'] else 'Vermelha' if velas[-3]['open'] > velas[-3]['close'] else 'Doji'


            cores = velas[-3] ,velas[-2] ,velas[-1] 

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'



            if direcao == 'put' or direcao == 'call':
                print('>> [cyan]Velas[/]: ',velas[-3] ,velas[-2] ,velas[-1] , ' - [green]Entrada[/] [yellow]para[/]: ', direcao)

                compra(ativo,valor_entrada,direcao,5,tipo)
                print('\n')

            else:
                if direcao == 'abortar':
                    print('>> [cyan]Velas[/]: ',velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Contra Tendência[/].')

                else:
                    print('>> [cyan]Velas[/]: ',velas[-3] ,velas[-2] ,velas[-1] )
                    print(ativo + ' - >> [red]Entrada abortada[/] - [yellow]Foi encontrado um doji na análise[/].')

                time.sleep(2)

def estrategia_fiveflipm5():
    global tipo, total_trades

    if tipo == 'automatico':
        binary, turbo, digital = payout(ativo)
        #print(binary, turbo, digital )
        if digital > turbo:
            print( 'Suas entradas serão realizadas nas digitais')
            tipo = 'digital'
        elif turbo > digital:
            print( 'Suas entradas serão realizadas nas binárias')
            tipo = 'binary'
        else:
            print(' Par fechado, escolha outro')
            sys.exit()

    print("\n >> Iniciando TORRES GEMEAS [5m]")  # Imprime informações
    while True:
        time.sleep(0.1)
        ### Horario do computador ###
        #minutos = float(datetime.now().strftime('%M.%S')[1:])
        ### horario da iqoption ###
        minutos = float(datetime.fromtimestamp(API.get_server_timestamp()).strftime('%M.%S'))
        if total_trades > 0:
            print_catag = True
            print('Aguardando Horário para nova catalogação: ' ,minutos, end='\r')
            auto_catag = True if (minutos >= 23.58 and minutos <= 23.58) or (minutos >= 53.58 and minutos <= 53.58) else False
        else:
            print_catag = False
            auto_catag = False
        entrar = True if (minutos >= 24.58 and minutos <= 24.58) or (minutos >= 54.58 and minutos <= 54.58) else False
        if print_catag == False:
            print('Aguardando Horário de entrada ' ,minutos, end='\r')
    
        if auto_catag:
            if estrategia == 14:
                catalogar()
            else:
                pass

        if entrar:
            print('\n>> Iniciando análise da estratégia TORRES GEMEAS M5')
            direcao = False
            timeframe = 300
            qnt_velas = 4

            if analise_medias == 'S':
                velas = API.get_candles(ativo, timeframe, velas_medias, time.time())
                tendencia = medias(velas)
            else:
                velas = API.get_candles(ativo, timeframe, qnt_velas, time.time())

            velas[-4] = 'Verde' if velas[-4]['open'] < velas[-4]['close'] else 'Vermelha' if velas[-4]['open'] > velas[-4]['close'] else 'Doji'
            cores = velas[-4] 

            if cores.count('Verde') > cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'call'
            if cores.count('Verde') < cores.count('Vermelha') and cores.count('Doji') == 0: direcao = 'put'

            if analise_medias =='S':
                if direcao == tendencia:
                    pass
                else:
                    direcao = 'abortar'

            if direcao == 'put' or direcao == 'call':
                print('Velas: ',velas[-4] , ' - Entrada para ', direcao)
                compra(ativo,valor_entrada,direcao,5,tipo)
            else:
                if direcao == 'abortar':
                    print('Velas: ',velas[-4] )
                    print('Entrada abortada - Contra Tendência.')
                else:
                    print('Velas: ',velas[-4] )
                    print('Entrada abortada - Foi encontrado um doji na análise.')

                time.sleep(2)

            print('\n######################################################################\n')

################################################################################

# Imprimindo informações iniciais do bot
print('\n######################################################################\n')  # Imprime uma linha de separação
print(' Olá, ',nome, '. Seja bem vindo ao Robô do Canal do Lucas.')  # Imprime uma mensagem de boas-vindas com o nome do usuário
print(' Seu Saldo na conta ',tipo_conta, 'é de', cifrao,valorconta)  # Imprime o saldo da conta
print(' Seu valor de entrada é de ',cifrao,valor_entrada)  # Imprime o valor de entrada
print(' Stop win:',cifrao,stop_win)  # Imprime o stop win definido
print(' Stop loss:',cifrao,'-',stop_loss)  # Imprime o stop loss definido
print('\n######################################################################\n')  # Imprime uma linha de separação

print('>> Iniciando catalogação')
lista_catalog , linha = catag(API)

estrateg = lista_catalog[0][0]
ativo = lista_catalog[0][1]
assertividade = lista_catalog[0][linha]

print(tabulate(lista_catalog, headers=['ESTRATEGIA', 'PAR', 'WIN', 'GALE1', 'GALE2', 'GALE3', 'GALE4', 'GALE5', 'DOJI', 'LOSS', 'ASSERTIVIDADE'], tablefmt="mixed_grid"))

print('\n>> Melhor par:',ativo,'| Melhor estrategia:', estrateg,'| Assertividade:', assertividade,'\n')

### Função para escolher Estratégia ### 
while True:
    estrategia = input('>> Selecione a estratégia para operar: '+
                            '\n>> 1 -  Gaba M5'+
                            '\n>> 2 -  Triplicação M5'+
                            '\n>> 3 -  Não Triplicação M5'+
                            '\n>> 4 -  D21 M5'+
                            '\n>> 5 -  Garra M5'+
                            '\n>> 6 -  Três Vizinhos M5'+
                            '\n>> 7 -  Três Mosqueteiros M5'+
                            '\n>> 8 -  Torres Gêmeas M5'+
                            '\n>> 9 -  Milhão Minoria M5'+
                            '\n>> 10 - Milhão Maioria M5'+
                            '\n>> 11 - MHI1 Maioria M5'+
                            '\n>> 12 - MHI1 Minoria M5'+
                            '\n>> 13 - Five Flip M5'+
                            '\n>> 14 - AUTOMATICO'+
                             '\n-->')

    estrategia = int(estrategia)
    
    if estrategia == 1:
        break
    if estrategia == 2:
        break
    if estrategia == 3:
        break
    if estrategia == 4:
        break
    if estrategia == 5:
        break
    if estrategia == 6:
        break
    if estrategia == 7:
        break
    if estrategia == 8:
        break
    if estrategia == 9:
        break
    if estrategia == 10:
        break
    if estrategia == 11:
        break
    if estrategia == 12:
        break
    if estrategia == 13:
        break
    if estrategia == 14:
        break
    else:
        print('Escolha incorreta! Digite 1 ou até 14')

### chamada da estrategia ###
if estrategia == 1:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_gaba()
if estrategia == 2:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_triplicacao()
if estrategia == 3:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_naotriplicacao()
if estrategia == 4:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_d21()
if estrategia == 5:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_garram5()
if estrategia == 6:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_tresvizinhosm5() 
if estrategia == 7:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_tresmosqueteirosm5()
if estrategia == 8:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_torresgemeasm5()
if estrategia == 9:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_milhaominoriam5()
if estrategia == 10:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_milhaomaioriam5()
if estrategia == 11:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_mhi1maioriam5()
if estrategia == 12:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_mhi1minoriam5()
if estrategia == 13:
    ativo = input('\n>> Digite o ativo que deseja operar: ').upper()
    print('\n')
    estrategia_fiveflipm5() 
if estrategia == 14:
    while True:
        ### chamada da estrategia ###
        if estrateg == 'GABA':
            estrategia_gaba()
            break
        if estrateg == 'TRIPLICACAO M5':
            estrategia_triplicacao()
            break
        if estrateg == 'NAO TRIPLICACAO M5':
            estrategia_naotriplicacao()
            break
        if estrateg == 'D21 M5':
            estrategia_d21()
            break
        if estrateg == 'GARRA M5':
            estrategia_garram5()
            break
        if estrateg == 'TRES VIZINHOS M5':
            estrategia_tresvizinhosm5()
            break
        if estrateg == 'TRES MOSQUETEIROS M5':
            estrategia_tresmosqueteirosm5()
            break
        if estrateg == 'TORRES GEMEAS M5':
            estrategia_torresgemeasm5()
            break
        if estrateg == 'MILHAO MINORIA M5':
            estrategia_milhaominoriam5()
            break
        if estrateg == 'MILHAO MAIORIA M5':
            estrategia_milhaomaioriam5()
            break
        if estrateg == 'MHI1 MAIORIA M5':
            estrategia_mhi1maioriam5() 
            break
        if estrateg == 'MHI1 MINORIA M5':
            estrategia_mhi1minoriam5()
            break
        if estrateg == 'FIVE FLIP M5':
            estrategia_fiveflipm5()
            break
        
        else:
            print(' NAO ENCONTRADO ESTRATEGIA! error ')
            sys.exit()