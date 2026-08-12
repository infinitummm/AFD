import sys
import os

class DFA:
    def __init__(self, states: set, alphabet: set, initial_state: str, accept_states: set, delta: dict):
        self.states = states
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.accept_states = accept_states
        self.delta = delta

    def simulate(self, input_string: str):
        current_state = self.initial_state
        path = [current_state]

        for char in input_string:
            if char not in self.alphabet:
                return False, path, f"Símbolo '{char}' no pertenece al alfabeto"
            
            if current_state not in self.delta or char not in self.delta[current_state]:
                return False, path, f"Transición no definida para el estado '{current_state}' y símbolo '{char}'"
            
            current_state = self.delta[current_state][char]
            path.append(current_state)

        is_accepted = current_state in self.accept_states
        reason = None if is_accepted else f"El estado final '{current_state}' no es de aceptación"
        return is_accepted, path, reason

def load_config(config_path: str) -> DFA:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"El archivo de configuración '{config_path}' no existe.")

    sections = {}
    current_section = None

    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                current_section = line[1:].strip().lower()
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)

    states = set(p.strip() for p in sections.get('estados', [''])[0].split(',') if p.strip()) if 'estados' in sections else set()
    alphabet = set(p.strip() for p in sections.get('alfabeto', [''])[0].split(',') if p.strip()) if 'alfabeto' in sections else set()
    initial_state = sections.get('estado inicial', [''])[0].strip() if 'estado inicial' in sections and sections['estado inicial'] else ''
    accept_states = set(p.strip() for p in sections.get('estados finales', [''])[0].split(',') if p.strip()) if 'estados finales' in sections and sections['estados finales'] else set()

    if initial_state not in states:
        raise ValueError(f"Estado inicial '{initial_state}' no pertenece al conjunto de estados Q")

    if not accept_states.issubset(states):
        invalid = accept_states - states
        raise ValueError(f"Estados finales {invalid} no pertenecen al conjunto de estados Q")

    delta = {}
    for trans in sections.get('transiciones', []):
        parts = [p.strip() for p in trans.split(',')]
        if len(parts) == 3:
            src, sym, dst = parts
            if src not in states:
                raise ValueError(f"Estado de origen '{src}' en transición no pertenece al conjunto de estados Q")
            if dst not in states:
                raise ValueError(f"Estado de destino '{dst}' en transición no pertenece al conjunto de estados Q")
            if sym not in alphabet:
                raise ValueError(f"Símbolo '{sym}' en transición no pertenece al alfabeto Sigma")
            if src not in delta:
                delta[src] = {}
            delta[src][sym] = dst

    return DFA(states, alphabet, initial_state, accept_states, delta)


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 AFD.py <archivo_conf.txt> <archivo_cadenas.txt>")
        sys.exit(1)

    config_path = sys.argv[1]
    cadenas_path = sys.argv[2]

    try:
        dfa = load_config(config_path)
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        sys.exit(1)

    if not os.path.exists(cadenas_path):
        print(f"Error: El archivo de cadenas '{cadenas_path}' no existe.")
        sys.exit(1)

    with open(cadenas_path, 'r', encoding='utf-8') as f:
        cadenas = [line.rstrip('\r\n') for line in f]

    print(f"=== Procesando cadenas con el AFD desde '{config_path}' ===\n")
    for s in cadenas:
        accepted, path, reason = dfa.simulate(s)
        path_str = " -> ".join(path)
        if accepted:
            result_str = "ACEPTADA"
        else:
            result_str = f"RECHAZADA (Error: {reason})" if "no pertenece" in (reason or "") else (f"RECHAZADA ({reason})" if reason else "RECHAZADA")
        print(f"Cadena: '{s}' | Recorrido: {path_str} | Resultado: {result_str}")

if __name__ == '__main__':
    main()

