from typing import Set

#                                         ==================== VALIDAÇÕES ALGORÍTMICAS ====================

class DocumentValidators:
    
    @staticmethod

#        Valida CPF através do algoritmo de dígitos verificadores.
    def validar_cpf(cpf: str) -> bool:

        if len(cpf) != 11 or not cpf.isdigit():
            return False
        
        if cpf == cpf[0] * 11:
            return False
        
#        Cálculo do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        if int(cpf[9]) != dv1:
            return False
        
#         Cálculo do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        return int(cpf[10]) == dv2

#        Valida número de cartão de crédito usando algoritmo de Luhn.
    @staticmethod
    def validar_luhn(numero: str) -> bool:
        if not numero.isdigit():
            return False
        
        def digitos(n):
            return [int(d) for d in n]
        
        digitos_inverso = digitos(numero)[::-1]
        soma = sum(digitos_inverso[::2])
        for d in digitos_inverso[1::2]:
            dobro = d * 2
            soma += dobro - 9 if dobro > 9 else dobro
        return soma % 10 == 0