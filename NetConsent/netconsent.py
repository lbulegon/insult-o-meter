import random
import time
import os
import hashlib
import msvcrt

# Configuração inicial
USERS = ["User1", "User2", "User3", "User4", "User5"]
INITIAL_BALANCE = 1000  # Cada usuário começa com 1000 Pi coins

# Criando ou carregando carteiras
wallets = {}
for user in USERS:
    wallet_file = f"wallet_{user}.txt"
    if not os.path.exists(wallet_file):
        with open(wallet_file, "w") as f:
            f.write(str(INITIAL_BALANCE))
    with open(wallet_file, "r") as f:
        wallets[user] = int(f.read().strip())

# Função para salvar o saldo das carteiras
def save_wallets():
    for user, balance in wallets.items():
        with open(f"wallet_{user}.txt", "w") as f:
            f.write(str(balance))

# Classe para representar uma Árvore de Merkle
class MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        self.levels = self.build_tree(transactions)
        self.root = self.levels[-1][0] if self.levels else None
    
    def hash_transaction(self, transaction):
        return hashlib.sha256(str(transaction).encode()).hexdigest()
    
    def build_tree(self, transactions):
        if not transactions:
            return []
        
        tree_levels = []
        current_level = [self.hash_transaction(tx) for tx in transactions]
        tree_levels.append(current_level)
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined_hash = hashlib.sha256((current_level[i] + current_level[i+1]).encode()).hexdigest()
                else:
                    combined_hash = current_level[i]
                next_level.append(combined_hash)
            tree_levels.append(next_level)
            current_level = next_level
        
        return tree_levels

    def save_to_file(self):
        with open("merkle_tree.txt", "w") as f:
            for level in range(len(self.levels)):
                f.write(f"Level {level}:\n")
                f.write(" ".join(self.levels[level]) + "\n\n")
            f.write(f"Merkle Root: {self.root}\n")

# Criando uma transação
def create_transaction(transaction_id, sender, receiver, amount):
    return {
        "transaction_id": transaction_id,
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "status": "pending"
    }

# Função principal
def run_network():
    transaction_counter = 1
    transactions = []

    with open("transacoes_geral.txt", "w") as file_geral, \
         open("transacoes_aceitas.txt", "w") as file_aceitas, \
         open("transacoes_rejeitadas.txt", "w") as file_rejeitadas:

        file_geral.write("Transações da Rede\n" + "="*50 + "\n")
        file_aceitas.write("Transações Aceitas\n" + "="*50 + "\n")
        file_rejeitadas.write("Transações Rejeitadas\n" + "="*50 + "\n")

        while True:
            sender, receiver = random.sample(USERS, 2)
            amount = random.randint(1, 100)
            transaction = create_transaction(f"TX{transaction_counter}", sender, receiver, amount)
            transaction_counter += 1
            
            print("Nova transação criada:", transaction)

            if wallets[sender] < amount:
                transaction["status"] = "insufficient_funds"
                print("Saldo insuficiente! Transação rejeitada.")
                file_rejeitadas.write(f"{transaction}\n")
            else:
                transactions.append(transaction)
                merkle_tree = MerkleTree(transactions)
                
                if merkle_tree.root:
                    transaction["status"] = "valid"
                    wallets[sender] -= amount
                    wallets[receiver] += amount
                    save_wallets()
                    print("Transação validada com Merkle Tree!")
                    file_aceitas.write(f"{transaction}\n")
                    merkle_tree.save_to_file()
                    print("Merkle tree saved in merkle_tree.txt")
                else:
                    transaction["status"] = "invalid"
                    print("Transação rejeitada!")
                    file_rejeitadas.write(f"{transaction}\n")
            
            file_geral.write(f"{transaction}\n")
            print("Saldo atualizado:", wallets)
            
            time.sleep(1)
            if msvcrt.kbhit():
                print("Loop interrompido.")
                break

def start():
    try:
        run_network()
    except KeyboardInterrupt:
        print("Programa encerrado.")

if __name__ == "__main__":
    start()
