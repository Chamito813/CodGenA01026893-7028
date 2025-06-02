.data
newline: .asciiz "\n"
esPar: .word 0
limite: .word 0
i: .word 0

.text
j main
.globl main

imprimirPar:
	move $t0, $a0	# param 'num' (en $a0) → $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 10	# const 10
	add $t0, $t1, $t0	# suma
	move $a0, $t0	# pasar valor a $a0 para print_int
	li   $v0, 1	# syscall print_int
	syscall
	la   $a0, newline	# cargar dirección de "\n"
	li   $v0, 4	# syscall print_string
	syscall
	li   $t0, 0	# output devuelve 0
	li $t0, 0	# const 0
	move $v0, $t0	# valor de retorno en $v0
	jr $ra	# retornar de imprimirPar
	jr $ra	# retornar de imprimirPar
imprimirImpar:
	move $t0, $a0	# param 'num' (en $a0) → $t0
	move $a0, $t0	# pasar valor a $a0 para print_int
	li   $v0, 1	# syscall print_int
	syscall
	la   $a0, newline	# cargar dirección de "\n"
	li   $v0, 4	# syscall print_string
	syscall
	li   $t0, 0	# output devuelve 0
	li $t0, 1	# const 1
	move $v0, $t0	# valor de retorno en $v0
	jr $ra	# retornar de imprimirImpar
	jr $ra	# retornar de imprimirImpar
recorrerNumeros:
	move $s0, $a0	# guardar n ($a0) → $s0 en recNum
	li $t0, 1	# const 1
	la $t1, i	# cargar dirección de i
	sw $t0, 0($t1)	# almacenar $t0 → i
	la $t1, esPar	# cargar dirección de esPar
	lw $t0, 0($t1)	# cargar esPar en $t0
	li $t0, 0	# const 0
	la $t1, esPar	# cargar dirección de esPar
	sw $t0, 0($t1)	# almacenar $t0 → esPar
while0:
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $t1, $t0	# guardar op izq en $t1
	move $t0, $s0	# param 'n' (en $s0) → $t0
	sle $t0, $t1, $t0	# menor o igual
	beq $t0, $zero, endwhile1	# condición falsa → fin while
	la $t1, esPar	# cargar dirección de esPar
	lw $t0, 0($t1)	# cargar esPar en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 1	# const 1
	seq $t0, $t1, $t0	# igual
	beq $t0, $zero, else2	# condición falsa → else
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $a0, $t0	# pasar arg a $a0
	jal imprimirPar	# llamar imprimirPar
	move $t0, $v0	# resultado de imprimirPar → $t0
	la $t1, esPar	# cargar dirección de esPar
	sw $t0, 0($t1)	# almacenar $t0 → esPar
	j endif3	# saltar fin if
else2:
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $a0, $t0	# pasar arg a $a0
	jal imprimirImpar	# llamar imprimirImpar
	move $t0, $v0	# resultado de imprimirImpar → $t0
	la $t1, esPar	# cargar dirección de esPar
	sw $t0, 0($t1)	# almacenar $t0 → esPar
endif3:
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 1	# const 1
	add $t0, $t1, $t0	# suma
	la $t1, i	# cargar dirección de i
	sw $t0, 0($t1)	# almacenar $t0 → i
	j while0	# volver a condición
endwhile1:
	jr $ra	# retornar de recorrerNumeros
main:
	li $t0, 30	# const 30
	la $t1, limite	# cargar dirección de limite
	sw $t0, 0($t1)	# almacenar $t0 → limite
	la $t1, limite	# cargar dirección de limite
	lw $t0, 0($t1)	# cargar limite en $t0
	move $a0, $t0	# pasar arg a $a0
	jal recorrerNumeros	# llamar recorrerNumeros
	move $t0, $v0	# resultado de recorrerNumeros → $t0
	li $v0, 10	# exit por defecto
	syscall
