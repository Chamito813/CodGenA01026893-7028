class SymbolAttributes:
    def __init__(self, name, kind, type_, lineno, scope, is_array=False, params=None, location=None):
        self.name = name                 
        self.kind = kind                  
        self.type = type_                 
        self.lineno = [lineno]           
        self.scope = scope                
        self.is_array = is_array          
        self.params = params or []        
        self.location = location

    def __str__(self):
        param_info = f"Params: {[p.name for p in self.params]}" if self.params else ""
        array_info = "[ ]" if self.is_array else ""
        return f"{self.name}{array_info} ({self.kind}, {self.type.name}, scope: {self.scope}) {param_info} at lines {self.lineno}"


symbol_table = {}


def st_insert(name, attr: SymbolAttributes):
    if name in symbol_table:
        existing = symbol_table[name][-1]
        if attr.lineno[0] not in existing.lineno:
            existing.lineno.append(attr.lineno[0])
    else:
        symbol_table[name] = [attr]


def st_lookup(name):
    if name in symbol_table:
        return symbol_table[name][-1]
    return None


def printSymTab():
    print("\nTabla de Símbolos:")
    print("Nombre           Tipo     Clase     Scope     Líneas   Extra")
    print("--------------------------------------------------------------")
    for name, attrs in symbol_table.items():
        for attr in attrs:
            line_list = ','.join(str(ln) for ln in attr.lineno)
            extra = "array" if attr.is_array else (f"params: {len(attr.params)}" if attr.kind == 'function' else "")
            print(f"{attr.name.ljust(15)}{attr.type.name.ljust(9)}{attr.kind.ljust(10)}{attr.scope.ljust(10)}{line_list.ljust(10)}{extra}")
