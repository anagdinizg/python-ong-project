import mysql.connector
from mysql.connector import Error
from datetime import date, datetime


class Animal:
    nome = ""
    data_nascimento = ""
    especie = ""
    porte = ""
    pelagem = ""
    sexo = ""
    observacoes = ""

    def _init_(self, nome, data_nascimento, especie, porte, pelagem, sexo, observacoes):
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.especie = especie
        self.porte = porte
        self.pelagem = pelagem
        self.sexo = sexo
        self.observacoes = observacoes

class Adotante:
    nome = ""
    cpf = ""
    endereco = ""
    contato = ""

    def _init_(self, nome, cpf, endereco, contato):
        self.nome = nome
        self.cpf = cpf
        self.endereco = endereco
        self.contato = contato

def conectar():
    try:
        bd = mysql.connector.connect(
            host='localhost',
            database='ONG_animais',
            user='root',
            password='1234$#@!.190'
        )
        if bd.is_connected():
            print('Conexão estabelecida.')
            return bd
    except Error as e:
        print(f'Erro ao conectar ao banco de dados: {e}')
        return None

def validar_sexo(sexo):
    sexo_valido = {'macho', 'femea', 'fêmea'}
    sexo_formatado = sexo.lower().strip()
    return sexo_formatado in sexo_valido

def validar_especie(especie):
    especie_valida = {'gato', 'cachorro'}
    especie_formatada = especie.lower().strip()
    return especie_formatada in especie_valida

def validar_porte(porte):
    porte_valido = {'pequeno', 'medio', 'médio', 'grande'}
    porte_formatado = porte.lower().strip()
    return porte_formatado in porte_valido

def validar_data(data):
    try:
        datetime.strptime(data, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def cadastrar_animal(bd, animal):
    try:
        cursor = bd.cursor()

        while True:

            if not validar_sexo(animal.sexo):
                print('Sexo inválido. Por favor, insira "macho" ou "femea".')
                animal.sexo = input('Digite o sexo do animal: ')
                continue

            if not validar_especie(animal.especie):
                print('Espécie inválida. Por favor, insira "gato" ou "cachorro".')
                animal.especie = input('Digite a espécie do animal: ')
                continue

            if not validar_porte(animal.porte):
                print('Porte inválido. Por favor, insira "pequeno", "medio" ou "grande".')
                animal.porte = input('Digite o porte do animal: ')
                continue

            if not validar_data(animal.data_nascimento):
                print("Data Invalida. Por favor, digite uma data valida no formato dd/mm/yyyy")
                animal.data_nascimento = input("Digite a data de nascimento: ")
                continue
            
            data_nascimento = datetime.strptime(animal.data_nascimento, '%d/%m/%Y').strftime('%Y-%m-%d')

            sql = 'INSERT INTO animal (nome, data_nascimento, especie, porte, pelagem, sexo, observacoes) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            val = (
            animal.nome, data_nascimento, animal.especie, animal.porte, animal.pelagem, animal.sexo, animal.observacoes)

            cursor.execute(sql, val)
            bd.commit()
            print('Animal cadastrado com sucesso.')

            break
    except Error as e:
        print(f'Erro ao cadastrar animal: {e}')

def listar_animais(bd, porte=None, especie=None, sexo=None):
    try:
        cursor = bd.cursor()
        sql = 'SELECT * FROM animal WHERE'
        params = []


        if porte:
            sql += ' porte = %s AND'
            params.append(porte)
        if especie:
            sql += ' especie = %s AND'
            params.append(especie)
        if sexo:
            sql += ' sexo = %s AND'
            params.append(sexo)


        if params:
            sql = sql[:-3]
            cursor.execute(sql, params)
        else:
            cursor.execute('SELECT * FROM animal')

        animais = cursor.fetchall()
        if animais:
            print('Animais disponíveis para adoção:')
            for animal in animais:
                print(
                    f"- ID: {animal[0]} | Nome: {animal[1]} | Data de nascimento: {animal[2]} | Especie: {animal[3]} | Porte: {animal[4]} | Pelagem: {animal[5]} | Sexo: {animal[6]} | Observações: {animal[7]}")
        else:
            print(
                'Não há animais disponíveis para adoção com os filtros informados.')
    except Error as e:
        print(f'Erro ao listar animais: {e}')

def adotar_animal(bd, id_adotante, especie=None, porte=None, sexo=None):
    try:
        cursor = bd.cursor()

        cursor.execute('SELECT * FROM adotantes WHERE id = %s', (id_adotante,))

        adotante = cursor.fetchone()
        if not adotante:
            print('ID de adotante inválido. Certifique-se de inserir um ID válido.')
            return

        listar_animais(bd, porte, especie, sexo)

        id_animal = input('Escolha o ID do animal que deseja adotar: ')
        cursor.execute('SELECT * FROM animal WHERE id = %s', (id_animal,))
        animal = cursor.fetchone()

        if not animal:
            print('ID de animal inválido. Certifique-se de inserir um ID válido.')
            return


        data_adocao = date.today()
        cursor.execute('DELETE FROM animal WHERE id = %s',
                       (id_animal,))
        cursor.execute('INSERT INTO adoções (id_adotante, id_animal, data_adocao) VALUES (%s, %s, %s)',
                       (id_adotante, id_animal, data_adocao))
        bd.commit()
        file = open("Historico.txt","a")
        file.write(f"O adotante de ID {id_adotante} adotou o animal de ID {id_animal} em {data_adocao}.\n")
        print('Animal adotado com sucesso.')
    except Error as e:
        print(f'Erro ao adotar animal: {e}')

def cadastrar_adotante(bd, adotante):
    try:
        cursor = bd.cursor()
        sql = 'INSERT INTO adotantes (nome, cpf, endereco, contato) VALUES (%s, %s, %s, %s)'
        val = (adotante.nome, adotante.cpf, adotante.endereco, adotante.contato)
        cursor.execute(sql, val)
        bd.commit()


        adotante_id = cursor.lastrowid

        print(f'Bem-vindo, {adotante.nome}! Seu cadastro foi realizado com sucesso.')
        print(f'Seu ID de identificação é: {adotante_id}')
        print(
            'Por favor, lembre-se de guardar este ID de identificação pois ele será necessário para realizar adoções.')
    except Error as e:
        print(f'Erro ao cadastrar adotante: {e}')

def listar_adotantes(bd):
    try:
        cursor = bd.cursor()
        cursor.execute('SELECT * FROM adotantes')
        adotantes = cursor.fetchall()
        if adotantes:
            print('Lista de adotantes:')
            for adotante in adotantes:
                print(
                    f"- ID: {adotante[0]} | Nome: {adotante[1]} | CPF: {adotante[2]} | Contato: {adotante[3]} | Endereço: {adotante[4]}")
        else:
            print('Não há adotantes cadastrados.')
    except Error as e:
        print(f'Erro ao listar adotantes: {e}')

def visualizar_historico(bd):
    try:
        cursor = bd.cursor(dictionary=True)
        sql = "SELECT id_adotante, id_animal, data_adocao FROM adoções"
        cursor.execute(sql)
        adocoes = cursor.fetchall()

        if adocoes:
            file = open("Historico.txt","r")
            print(file.read())
        else:
            print("Nenhuma adoção registrada ainda.")

    except Error as e:
        print(f'Erro ao visualizar histórico: {e}')

def main():
    bd = conectar()
    if bd:
        while True:
            print('\n1. Cadastrar novo animal')
            print('2. Listar animais disponíveis para adoção')
            print('3. Adotar animal')
            print('4. Cadastrar novo adotante')
            print('5. Listar adotantes')
            print('6. Visualizar histórico de adoções')
            print('7. Sair')
            opcao = input('\nEscolha uma opção: ')

            if opcao == '1':
                nome = input('Nome do animal: ')
                data_nascimento = input('Data de nascimento (DD/MM/YYYY): ')
                especie = input('Espécie (cachorro ou gato): ')
                porte = input('Porte (Grande,Medio ou Pequeno): ')
                pelagem = input('Pelagem: ')
                sexo = input('Sexo (macho ou femea): ')
                observacoes = input('Observações: ')
                animal = Animal(nome, data_nascimento, especie, porte, pelagem, sexo, observacoes)
                cadastrar_animal(bd, animal)
            elif opcao == '2':
                print('Filtrar animais (deixe em branco para não filtrar):')
                porte = input('Porte: ')
                especie = input('Espécie: ')
                sexo = input('Sexo: ')
                listar_animais(bd, porte, especie, sexo)
            elif opcao == '3':
                listar_adotantes(bd)
                id_adotante = input('ID do adotante: ')
                print("Deixe em branco para não filtrar")
                especie = input('Espécie do animal: ')
                porte = input('Porte do animal: ')
                sexo = input('Sexo do animal: ')
                adotar_animal(bd, id_adotante, especie, porte, sexo)

            elif opcao == '4':
                nome = input('Nome completo do adotante: ')
                cpf = input('CPF do adotante: ')
                endereco = input('Endereço do adotante: ')
                contato = input('Contato do adotante: ')
                adotante = Adotante(nome, cpf, endereco, contato)
                cadastrar_adotante(bd, adotante)
            elif opcao == '5':
                listar_adotantes(bd)
            elif opcao == '6':
                visualizar_historico(bd)
            elif opcao == '7':
                print('Saindo...')
                break
            else:
                print('Opção inválida.')

        bd.close()

main()