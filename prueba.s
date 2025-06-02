.data
r: .word 0
i: .word 0

.globl main
.text
main:
	li $t0, 10	# Cargar constante 10 en $t0
	la $t1, r	# Cargar dirección de r en $t1
	sw $t0, 0($t1)	# Almacenar $t0 → r
	la $t1, i	# Cargar dirección de i en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← i
	li $t0, 0	# Cargar constante 0 en $t0
	la $t1, i	# Cargar dirección de i en $t1
	sw $t0, 0($t1)	# Almacenar $t0 → i
while0:
	la $t1, i	# Cargar dirección de i en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← i
	move $t1, $t0	# Guardar operando izquierdo en $t1
	li $t0, 10	# Cargar constante 10 en $t0
	slt $t0, $t1, $t0	# i < j ?
	beq $t0, $zero, endwhile1	# Condición falsa → fin while
	la $t1, i	# Cargar dirección de i en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← i
	move $t1, $t0	# Guardar operando izquierdo en $t1
	li $t0, 1	# Cargar constante 1 en $t0
	add $t0, $t1, $t0	# Suma
	la $t1, i	# Cargar dirección de i en $t1
	sw $t0, 0($t1)	# Almacenar $t0 → i
	la $t1, i	# Cargar dirección de i en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← i
	move $t1, $t0	# Guardar operando izquierdo en $t1
	li $t0, 5	# Cargar constante 5 en $t0
	slt $t0, $t1, $t0	# i < j ?
	beq $t0, $zero, else2	# Condición falsa → else
	la $t1, r	# Cargar dirección de r en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← r
	move $t1, $t0	# Guardar operando izquierdo en $t1
	li $t0, 25	# Cargar constante 25 en $t0
	add $t0, $t1, $t0	# Suma
	la $t1, r	# Cargar dirección de r en $t1
	sw $t0, 0($t1)	# Almacenar $t0 → r
	j endif3	# Saltar al fin del if
else2:
	la $t1, i	# Cargar dirección de i en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← i
	move $t1, $t0	# Guardar operando izquierdo en $t1
	li $t0, 5	# Cargar constante 5 en $t0
	seq $t0, $t1, $t0	# i == j ?
	beq $t0, $zero, else4	# Condición falsa → else
	la $t1, r	# Cargar dirección de r en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← r
	move $t1, $t0	# Guardar operando izquierdo en $t1
	li $t0, 35	# Cargar constante 35 en $t0
	sub $t0, $t1, $t0	# Resta
	la $t1, r	# Cargar dirección de r en $t1
	sw $t0, 0($t1)	# Almacenar $t0 → r
	j endif5	# Saltar al fin del if
else4:
	la $t1, r	# Cargar dirección de r en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← r
	move $t1, $t0	# Guardar operando izquierdo en $t1
	li $t0, 1	# Cargar constante 1 en $t0
	sub $t0, $t1, $t0	# Resta
	la $t1, r	# Cargar dirección de r en $t1
	sw $t0, 0($t1)	# Almacenar $t0 → r
endif5:
endif3:
	j while0	# Volver a condición
endwhile1:
	la $t1, r	# Cargar dirección de r en $t1
	lw $t0, 0($t1)	# Cargar $t0 ← r
	move $a0, $t0	# Pasar argumento a $a0
	li $v0, 1	# syscall print_int
	syscall
	li $v0, 10	# exit por defecto
	syscall
