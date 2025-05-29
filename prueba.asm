.data
y: .word 0
x: .word 0

.text
gcd:
	lw $t0, v($gp)	# Cargar variable v
	move $t1, $t0	# Guardar operando izquierdo
	li $t0, 0	# Cargar constante 0
	seq $t0, $t1, $t0	# Igualdad
	beq $t0, $zero, else0	# Saltar si condición es falsa
	lw $t0, u($gp)	# Cargar variable u
	move $v0, $t0	# Retornar valor
	jr $ra	# Regresar de función
	j endif1	# Saltar al final del if
else0:
	lw $t0, v($gp)	# Cargar variable v
	lw $t0, u($gp)	# Cargar variable u
	move $t1, $t0	# Guardar operando izquierdo
	lw $t0, v($gp)	# Cargar variable v
	move $t1, $t0	# Guardar operando izquierdo
	lw $t0, v($gp)	# Cargar variable v
	div $t1, $t0	# Dividir t1 entre t0
	mflo $t0	# Guardar cociente en $t0
	move $t1, $t0	# Guardar operando izquierdo
	lw $t0, v($gp)	# Cargar variable v
	mul $t0, $t1, $t0	# Multiplicación
	sub $t0, $t1, $t0	# Resta
	move $t0, $t0	# Guardar resultado temporal en $t0
	subu $sp, $sp, 4	# Reservar espacio en pila
	sw $t0, 0($sp)	# Push argumento desde $t0
	lw $t0, u($gp)	# Cargar variable u
	move $t1, $t0	# Guardar operando izquierdo
	lw $t0, v($gp)	# Cargar variable v
	move $t1, $t0	# Guardar operando izquierdo
	lw $t0, v($gp)	# Cargar variable v
	div $t1, $t0	# Dividir t1 entre t0
	mflo $t0	# Guardar cociente en $t0
	move $t1, $t0	# Guardar operando izquierdo
	lw $t0, v($gp)	# Cargar variable v
	mul $t0, $t1, $t0	# Multiplicación
	sub $t0, $t1, $t0	# Resta
	move $t1, $t0	# Guardar resultado temporal en $t1
	subu $sp, $sp, 4	# Reservar espacio en pila
	sw $t1, 0($sp)	# Push argumento desde $t1
	jal gcd	# Llamar función gcd
	move $t0, $v0	# Resultado a $t0
	addu $sp, $sp, 8	# Limpiar pila
	move $v0, $t0	# Retornar valor
	jr $ra	# Regresar de función
endif1:
main:
	li $v0, 5	# Leer entero
	syscall
	move $t0, $v0	# Guardar resultado de input
	sw $t0, x($gp)	# Asignar a x
	li $v0, 5	# Leer entero
	syscall
	move $t0, $v0	# Guardar resultado de input
	sw $t0, y($gp)	# Asignar a y
	lw $t0, x($gp)	# Cargar variable x
	lw $t0, y($gp)	# Cargar variable y
	move $t2, $t0	# Guardar resultado temporal en $t2
	subu $sp, $sp, 4	# Reservar espacio en pila
	sw $t2, 0($sp)	# Push argumento desde $t2
	lw $t0, y($gp)	# Cargar variable y
	move $t3, $t0	# Guardar resultado temporal en $t3
	subu $sp, $sp, 4	# Reservar espacio en pila
	sw $t3, 0($sp)	# Push argumento desde $t3
	jal gcd	# Llamar función gcd
	move $t0, $v0	# Resultado a $t0
	addu $sp, $sp, 8	# Limpiar pila
	move $a0, $t0	# Pasar argumento a $a0
	li $v0, 1	# Código de imprimir
	syscall
	li $v0, 10
	syscall
